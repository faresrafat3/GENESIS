"""
API Key Pool Manager — Smart Key Rotation for Free Tier Benchmarks
==================================================================

Purpose:
    إدارة مجموعة من مفاتيح OpenRouter (أو أي OpenAI-compatible) بشكل ذكي:
    - يدور على المفاتيح تلقائياً
    - يكتشف لما مفتاح يخلص quota (429 / insufficient credits / rate_limit)
    - ينقل للمفتاح التالي بدون فقدان طلبات
    - يحفظ إحصائيات استخدام لكل مفتاح (persisted في cache file)

SECURITY (CRITICAL — اقرأ ده):
    لا تحط أي مفتاح حقيقي في هذا الملف أو أي ملف يتم commit.
    المفاتيح تأتي من:
    1. environment variables (e.g. OPENROUTER_API_KEY_1, _2, ...)
    2. ملف .env محلي (مُدرج في .gitignore بالفعل)
    3. ملف keys file محلي يحدد بـ --keys_file

    قبل أي push:  git diff --staged | grep -E "sk-or-v1-|sk-"
    لو طلع أي ناتج، أوقف الـ commit واحذف الـ key.

Usage:
    from tools.api_key_pool import APIKeyPool, get_default_pool

    pool = get_default_pool()  # يقرأ من البيئة + .env تلقائياً
    client = pool.get_client()  # OpenAI client مع المفتاح الحالي

    try:
        response = client.chat.completions.create(...)
    except Exception as e:
        pool.report_failure(e)        # ينقل للمفتاح التالي لو لازم
        client = pool.get_client()    # client جديد بمفتاح جديد
        response = client.chat.completions.create(...)

    # أو الطريقة الأسهل: wrapper تلقائي
    response = pool.call_with_retry(
        lambda client: client.chat.completions.create(...)
    )

تصميم عام: يصلح لأي OpenAI-compatible API (OpenRouter, OpenAI, Together, etc.)
"""
from __future__ import annotations

import json
import os
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

try:
    import openai
except ImportError:
    openai = None  # سيتم التحقق عند الاستخدام


# أنماط أخطاء معروفة من OpenRouter / OpenAI / Together
# Daily-exhaust patterns: عند ظهور أي من دول، الـ key بايلت لباقي اليوم
# (لا فائدة من cooldown 60s؛ نحطه في daily_exhausted_until = end of day UTC)
DAILY_EXHAUST_PATTERNS = [
    "free-models-per-day",
    "per-day",
    "daily limit",
    "daily quota",
    "tokens per day",
    "requests per day",
]
RATE_LIMIT_PATTERNS = [
    "rate limit",
    "rate_limit",
    "rate-limit",
    "429",
    "too many requests",
    "quota",
    "insufficient_quota",
    "insufficient credits",
    "credit balance",
    "exceeded",
    "throttl",  # throttled / throttling
]
PERMANENT_FAILURE_PATTERNS = [
    "invalid_api_key",
    "incorrect api key",
    "authentication",
    "401",
    "403",
    "forbidden",
    "no auth credentials",
    "user not found",
    "account suspended",
]


@dataclass
class KeyStats:
    """إحصائيات مفتاح واحد."""
    key_id: str  # اسم المفتاح (مش القيمة الحقيقية)
    requests: int = 0
    successes: int = 0
    failures: int = 0
    rate_limited_at: Optional[float] = None  # timestamp (short cooldown)
    daily_exhausted_until: Optional[float] = None  # timestamp بنهاية اليوم UTC
    permanently_failed: bool = False
    last_error: str = ""
    failure_codes: dict[str, int] = field(default_factory=dict)

    def success_rate(self) -> float:
        return self.successes / self.requests if self.requests else 0.0

    def is_available(self, cooldown_seconds: float = 60.0) -> bool:
        """هل المفتاح ده متاح للاستخدام دلوقتي؟"""
        if self.permanently_failed:
            return False
        now = time.time()
        # daily exhaust له أولوية
        if self.daily_exhausted_until and now < self.daily_exhausted_until:
            return False
        if self.rate_limited_at is None:
            return True
        return (now - self.rate_limited_at) > cooldown_seconds


class APIKeyPool:
    """
    Pool ذكي للمفاتيح. Thread-safe بشكل أساسي (state read/write بسيطة).

    Args:
        keys: dict من {key_id: api_key_value}. key_id اسم رمزي للـ logging فقط.
        base_url: OpenAI-compatible endpoint URL.
        rate_limit_cooldown: ثواني الانتظار قبل إعادة محاولة مفتاح rate-limited.
        stats_file: مسار لحفظ إحصائيات الاستخدام (None = لا يحفظ).
    """

    def __init__(
        self,
        keys: dict[str, str],
        *,
        base_url: str = "https://openrouter.ai/api/v1",
        rate_limit_cooldown: float = 60.0,
        stats_file: Optional[Path] = None,
    ):
        if openai is None:
            raise ImportError("openai package not installed. Run: pip install openai")
        if not keys:
            raise ValueError("APIKeyPool needs at least one key")

        self.base_url = base_url
        self.rate_limit_cooldown = rate_limit_cooldown
        self.stats_file = Path(stats_file) if stats_file else None

        self._keys: dict[str, str] = dict(keys)
        self._stats: dict[str, KeyStats] = {
            kid: KeyStats(key_id=kid) for kid in keys
        }
        self._order: list[str] = list(keys.keys())  # round-robin order
        self._cursor: int = 0

        if self.stats_file and self.stats_file.exists():
            self._load_stats()

    # ----- public API -----

    def get_client(self, key_id: Optional[str] = None) -> "openai.OpenAI":
        """يرجع OpenAI client بمفتاح متاح. لو key_id محدد، يستخدمه."""
        if key_id:
            if key_id not in self._keys:
                raise KeyError(f"Unknown key_id: {key_id}")
            kid = key_id
        else:
            kid = self._next_available_key_id()
        return openai.OpenAI(api_key=self._keys[kid], base_url=self.base_url)

    def current_key_id(self) -> str:
        """يرجع key_id الحالي (للـ logging)."""
        return self._order[self._cursor]

    def call_with_retry(
        self,
        fn: Callable[["openai.OpenAI"], Any],
        *,
        max_attempts: Optional[int] = None,
        per_attempt_sleep: float = 0.5,
        on_attempt: Optional[Callable[[int, str, str], None]] = None,
    ) -> Any:
        """
        ينفذ fn(client) ويعيد المحاولة لو فيه rate limit / auth error.

        Args:
            fn: دالة تأخذ client وترجع response.
            max_attempts: عدد المحاولات (default = عدد المفاتيح المتاحة).
            per_attempt_sleep: ثواني انتظار قبل كل retry.
            on_attempt: callback(attempt_num, key_id, status) للـ logging.

        Returns:
            ناتج fn لما تنجح.

        Raises:
            آخر exception لو كل المفاتيح فشلت.
        """
        if max_attempts is None:
            max_attempts = max(len(self._keys), 3)

        last_exc: Optional[Exception] = None
        for attempt in range(1, max_attempts + 1):
            kid = self._next_available_key_id()
            stats = self._stats[kid]
            stats.requests += 1
            client = openai.OpenAI(api_key=self._keys[kid], base_url=self.base_url)
            try:
                if on_attempt:
                    on_attempt(attempt, kid, "trying")
                result = fn(client)
                stats.successes += 1
                self._save_stats_if_needed()
                if on_attempt:
                    on_attempt(attempt, kid, "success")
                return result
            except Exception as e:  # noqa: BLE001
                last_exc = e
                stats.failures += 1
                self._classify_and_record_failure(kid, e)
                if on_attempt:
                    on_attempt(attempt, kid, f"failed:{type(e).__name__}")
                self._save_stats_if_needed()
                time.sleep(per_attempt_sleep)
                # نكمل مع المفتاح التالي

        raise RuntimeError(
            f"All {max_attempts} attempts failed. Last error: {last_exc}"
        ) from last_exc

    def report_failure(self, exc: Exception) -> bool:
        """
        تبلغ الـ pool إن فيه فشل في المفتاح الحالي.
        يرجع True لو المفتاح اتعزل (rate limited / dead).
        """
        kid = self._order[self._cursor]
        self._classify_and_record_failure(kid, exc)
        self._save_stats_if_needed()
        return self._stats[kid].permanently_failed or self._stats[kid].rate_limited_at is not None

    def stats_summary(self) -> dict[str, Any]:
        """ملخص قابل للطباعة."""
        return {
            "total_keys": len(self._keys),
            "available_now": sum(1 for s in self._stats.values() if s.is_available(self.rate_limit_cooldown)),
            "permanently_failed": sum(1 for s in self._stats.values() if s.permanently_failed),
            "per_key": {
                kid: {
                    "requests": s.requests,
                    "successes": s.successes,
                    "failures": s.failures,
                    "success_rate": round(s.success_rate(), 3),
                    "available": s.is_available(self.rate_limit_cooldown),
                    "rate_limited_seconds_ago": (
                        round(time.time() - s.rate_limited_at) if s.rate_limited_at else None
                    ),
                    "last_error": s.last_error[:80],
                }
                for kid, s in self._stats.items()
            },
        }

    def print_summary(self) -> None:
        """طباعة منسقة لحالة الـ pool."""
        s = self.stats_summary()
        print(f"=== APIKeyPool Summary ===")
        print(f"Total: {s['total_keys']} | Available: {s['available_now']} | Dead: {s['permanently_failed']}")
        for kid, info in s["per_key"].items():
            mark = "✓" if info["available"] else ("✗ dead" if info["last_error"] and "401" in info["last_error"] else "✗ cooldown")
            print(f"  [{mark}] {kid:18s} req={info['requests']:4d} ok={info['successes']:4d} "
                  f"fail={info['failures']:3d} rate={info['success_rate']*100:5.1f}%")

    # ----- internal -----

    def _next_available_key_id(self) -> str:
        """Round-robin يقدم cursor بعد كل اختيار، يتخطى المفاتيح الميتة / المرهقة.

        ده الـ behavior الصح: كل طلب جديد يستخدم مفتاح تالي بالدور،
        مش نفس المفتاح لحد ما يفشل.
        """
        n = len(self._order)
        for _ in range(n):
            kid = self._order[self._cursor]
            # 🔑 تقديم الـ cursor للطلب التالي مهما كان الناتج
            self._cursor = (self._cursor + 1) % n
            if self._stats[kid].is_available(self.rate_limit_cooldown):
                return kid
        # كل المفاتيح إما ميتة أو في cooldown أو daily-exhausted
        non_perm = [
            (kid, s) for kid, s in self._stats.items() if not s.permanently_failed
        ]
        if not non_perm:
            raise RuntimeError("All keys permanently failed (auth errors). Check key validity.")

        # تحقق: هل كل المفاتيح في daily-exhausted؟ لو أيوة، fail fast.
        all_daily_exhausted = all(
            s.daily_exhausted_until and time.time() < s.daily_exhausted_until
            for _, s in non_perm
        )
        if all_daily_exhausted:
            now = time.time()
            min_wait = min(s.daily_exhausted_until - now for _, s in non_perm)
            hours = min_wait / 3600
            raise RuntimeError(
                f"All {len(non_perm)} keys are DAILY-EXHAUSTED. "
                f"Earliest reset: {hours:.1f}h from now (UTC midnight). "
                f"Options: (1) wait until reset, (2) add credits to one account "
                f"on https://openrouter.ai to unlock 1000 req/day."
            )

        # في مفاتيح يا rate-limited (cooldown قصير) — استنى الأقرب
        rl_candidates = [
            (s.rate_limited_at or float("inf"), kid)
            for kid, s in non_perm
            if s.rate_limited_at and not (s.daily_exhausted_until and time.time() < s.daily_exhausted_until)
        ]
        if not rl_candidates:
            # ما فيش rate-limited متاحة — كلها داخل في daily exhaust بس واحدة وحاولنا
            raise RuntimeError("No usable keys available — all either dead or daily-exhausted.")
        rl_candidates.sort()
        kid = rl_candidates[0][1]
        wait = max(0, self.rate_limit_cooldown - (time.time() - (self._stats[kid].rate_limited_at or 0)))
        print(f"  ⏳ All keys cooling down. Waiting {wait:.1f}s for {kid}...")
        time.sleep(wait + 0.1)
        self._stats[kid].rate_limited_at = None
        return kid

    def _classify_and_record_failure(self, kid: str, exc: Exception) -> None:
        stats = self._stats[kid]
        msg = (str(exc) + " " + getattr(exc, "message", "")).lower()
        stats.last_error = str(exc)[:300]

        # status code
        code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
        if code:
            stats.failure_codes[str(code)] = stats.failure_codes.get(str(code), 0) + 1

        # تصنيف
        if any(p in msg for p in PERMANENT_FAILURE_PATTERNS):
            stats.permanently_failed = True
            print(f"  ❌ Key {kid} marked DEAD: {str(exc)[:120]}")
        elif any(p in msg for p in DAILY_EXHAUST_PATTERNS):
            # المفتاح خلص حصته اليومية — عزله لباقي اليوم UTC
            import datetime as _dt
            tomorrow = _dt.datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + _dt.timedelta(days=1)
            stats.daily_exhausted_until = tomorrow.timestamp()
            hours_left = (stats.daily_exhausted_until - time.time()) / 3600
            print(f"  🚫 Key {kid} DAILY-EXHAUSTED until UTC midnight "
                  f"(~{hours_left:.1f}h). Not retrying.")
            # روح للمفتاح التالي
            self._cursor = (self._cursor + 1) % len(self._order)
        elif any(p in msg for p in RATE_LIMIT_PATTERNS):
            stats.rate_limited_at = time.time()
            print(f"  ⚠️  Key {kid} rate-limited (cooldown {self.rate_limit_cooldown}s): {str(exc)[:80]}")
            # روح للمفتاح التالي
            self._cursor = (self._cursor + 1) % len(self._order)
        else:
            # خطأ آخر — لا نعزل المفتاح، بس نسجل
            pass

    def _save_stats_if_needed(self) -> None:
        if not self.stats_file:
            return
        try:
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "saved_at": datetime.now().isoformat(),
                "base_url": self.base_url,
                "stats": {kid: asdict(s) for kid, s in self._stats.items()},
            }
            self.stats_file.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            print(f"  (warn) failed to save stats: {e}")

    def _load_stats(self) -> None:
        try:
            data = json.loads(self.stats_file.read_text(encoding="utf-8"))
            for kid, raw in data.get("stats", {}).items():
                if kid in self._stats:
                    # نحمل الإحصائيات بس، نرجع cooldown timestamps لـ None
                    # عشان نديهم فرصة جديدة من بداية الـ session
                    self._stats[kid] = KeyStats(
                        key_id=kid,
                        requests=raw.get("requests", 0),
                        successes=raw.get("successes", 0),
                        failures=raw.get("failures", 0),
                        permanently_failed=raw.get("permanently_failed", False),
                        last_error=raw.get("last_error", ""),
                        failure_codes=raw.get("failure_codes", {}),
                    )
        except Exception as e:
            print(f"  (warn) failed to load stats: {e}")


# ============ Loading helpers ============

def load_keys_from_env(
    prefix: str = "OPENROUTER_API_KEY",
    *,
    include_legacy: bool = True,
) -> dict[str, str]:
    """
    يقرأ المفاتيح من environment variables.

    أنماط تُلتقط:
    - OPENROUTER_API_KEY                 (المفتاح الأساسي)
    - OPENROUTER_API_KEY_1, _2, _3, ...  (مفاتيح إضافية)
    - OPENROUTER_API_KEY_AHMED, _FARES, ... (بأسماء وصفية)
    - OPENAI_API_KEY (لو include_legacy=True وما فيش مفاتيح OpenRouter)
    """
    keys: dict[str, str] = {}
    pattern = re.compile(rf"^{re.escape(prefix)}(?:_(\w+))?$")
    for env_name, val in os.environ.items():
        m = pattern.match(env_name)
        if m and val and val.strip():
            suffix = m.group(1) or "default"
            keys[suffix.lower()] = val.strip()

    if not keys and include_legacy:
        legacy = os.environ.get("OPENAI_API_KEY", "").strip()
        if legacy:
            keys["legacy"] = legacy

    return keys


def load_keys_from_file(path: str | Path) -> dict[str, str]:
    """
    يقرأ المفاتيح من ملف JSON أو ملف .env بسيط.

    JSON format:
        {"ahmed": "sk-or-v1-...", "fares1": "sk-or-v1-..."}

    .env format (KEY=VALUE per line, # للتعليقات):
        AHMED=sk-or-v1-...
        FARES1=sk-or-v1-...
    """
    path = Path(path)
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8")

    # JSON?
    if path.suffix.lower() == ".json" or content.lstrip().startswith("{"):
        try:
            data = json.loads(content)
            return {str(k).lower(): str(v).strip() for k, v in data.items() if v}
        except json.JSONDecodeError:
            pass

    # .env format
    keys: dict[str, str] = {}
    for line_no, raw in enumerate(content.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip().lstrip("export ").strip()
        v = v.strip().strip('"').strip("'")
        if v:
            # نشيل البادئة لو موجودة عشان نحصل على suffix نظيف
            label = k.replace("OPENROUTER_API_KEY_", "").replace("OPENROUTER_API_KEY", "default")
            keys[label.lower()] = v
    return keys


def get_default_pool(
    keys_file: Optional[str | Path] = None,
    *,
    base_url: str = "https://openrouter.ai/api/v1",
    rate_limit_cooldown: float = 60.0,
    stats_file: Optional[str | Path] = "logs/api_key_pool_stats.json",
    verbose: bool = True,
) -> APIKeyPool:
    """
    Pool افتراضي يجمع المفاتيح من:
    1. environment variables (OPENROUTER_API_KEY*, OPENAI_API_KEY)
    2. keys_file (لو مُحدد)
    3. .env المحلي (لو الـ python-dotenv مثبت)

    لازم يكون فيه مفتاح واحد على الأقل، وإلا يرفع ValueError.
    """
    # حاول تحمل .env تلقائياً لو dotenv موجود
    dotenv_loaded = False
    try:
        from dotenv import load_dotenv  # type: ignore
        # نحاول كل المسارات المحتملة
        for env_path in (".env", ".env.local", ".env.keys"):
            if Path(env_path).exists():
                load_dotenv(env_path, override=False)
                dotenv_loaded = True
                if verbose:
                    print(f"  (info) loaded env vars from {env_path}")
    except ImportError:
        if verbose:
            print("  (warn) python-dotenv not installed; .env file will NOT be auto-loaded.")
            print("        install it: pip install python-dotenv")

    keys: dict[str, str] = {}
    keys.update(load_keys_from_env())
    if keys_file:
        keys.update(load_keys_from_file(keys_file))

    if not keys:
        # حاول ملف افتراضي
        for fallback in (".env.keys", "keys.json", ".secrets/openrouter_keys.json"):
            if Path(fallback).exists():
                keys.update(load_keys_from_file(fallback))
                if keys:
                    if verbose:
                        print(f"  (info) loaded {len(keys)} keys from {fallback}")
                    break

    if not keys:
        raise ValueError(
            "No API keys found. Set OPENROUTER_API_KEY (or _1, _2, ...) in env, "
            "or create .env with OPENROUTER_API_KEY_NAME=sk-or-v1-...\n"
            "See .env.example for template."
        )

    # تشخيص: لو لقى مفتاح واحد بس، نقول للمستخدم ليه
    if verbose and len(keys) == 1:
        keyname = list(keys.keys())[0]
        if keyname in ("default", "legacy"):
            print(f"  ⚠️  Only 1 key found (label='{keyname}'). To use multiple keys:")
            print(f"      Edit .env to use OPENROUTER_API_KEY_AHMED=..., OPENROUTER_API_KEY_FARES1=... etc.")
            print(f"      The pool needs the OPENROUTER_API_KEY_<NAME> pattern, not just OPENROUTER_API_KEY.")
            # نتحقق هل في الـ env فعلاً مفاتيح إضافية ما اتقروش
            import os as _os
            extras = [n for n in _os.environ if n.startswith("OPENROUTER_API_KEY_")]
            if extras:
                print(f"      Found {len(extras)} env vars matching the pattern but they may be empty:")
                for n in extras:
                    val = _os.environ.get(n, "")
                    state = "EMPTY" if not val.strip() else f"set ({len(val)} chars)"
                    print(f"        {n}: {state}")

    pool = APIKeyPool(
        keys=keys,
        base_url=base_url,
        rate_limit_cooldown=rate_limit_cooldown,
        stats_file=Path(stats_file) if stats_file else None,
    )
    if verbose:
        print(f"  ✓ APIKeyPool ready with {len(keys)} keys: {list(keys.keys())}")
    return pool


if __name__ == "__main__":
    # smoke test
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--keys_file", default=None)
    p.add_argument("--test_call", action="store_true",
                   help="Make a small test API call to verify keys work")
    p.add_argument("--check_quotas", action="store_true",
                   help="Probe EACH key individually with tiny call to see who is exhausted")
    p.add_argument("--probe_model", default="openai/gpt-oss-120b:free",
                   help="Model to use for quota probing")
    args = p.parse_args()
    pool = get_default_pool(keys_file=args.keys_file)
    pool.print_summary()
    if args.test_call:
        print("\nTesting first key with a tiny call...")
        try:
            result = pool.call_with_retry(
                lambda c: c.chat.completions.create(
                    model=args.probe_model,
                    messages=[{"role": "user", "content": "Reply with just: OK"}],
                    max_tokens=5,
                    temperature=0.0,
                ),
                on_attempt=lambda n, k, s: print(f"  attempt {n} key={k} status={s}"),
            )
            print(f"  ✓ Response: {result.choices[0].message.content!r}")
        except Exception as e:
            print(f"  ✗ Test call failed: {e}")
        pool.print_summary()
    if args.check_quotas:
        # Probe each key individually
        print(f"\n=== Probing each key with model={args.probe_model} ===")
        for kid in list(pool._keys.keys()):
            client = pool.get_client(key_id=kid)
            try:
                resp = client.chat.completions.create(
                    model=args.probe_model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=2,
                    temperature=0.0,
                )
                content = resp.choices[0].message.content or "(empty)"
                print(f"  ✓ {kid:25s} OK: {content[:30]!r}")
                pool._stats[kid].requests += 1
                pool._stats[kid].successes += 1
            except Exception as e:
                msg = str(e)[:100]
                if "per-day" in str(e).lower() or "daily" in str(e).lower():
                    status = "🚫 DAILY-EXHAUSTED"
                elif "rate" in str(e).lower() or "429" in str(e):
                    status = "⚠️  RATE-LIMITED"
                elif "401" in str(e) or "auth" in str(e).lower():
                    status = "❌ DEAD"
                else:
                    status = "✗ ERROR"
                print(f"  {status} {kid:25s} {msg}")
                pool._stats[kid].requests += 1
                pool._classify_and_record_failure(kid, e)
        pool._save_stats_if_needed()
        print()
        pool.print_summary()
