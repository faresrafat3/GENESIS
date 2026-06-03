# مذكرة تنفيذ طبقة الاستمرارية (Persistence Layer)

## الهدف
بناء طبقة تخزين دائم (persistent storage) لنظام SIA بدون اي اعتماديات خارجية باستخدام مكتبة sqlite3 المدمجة في Python stdlib.

## القرارات التصميمية

### 1. لماذا SQLite؟
- **صفر اعتماديات**: sqlite3 جزء من Python stdlib - لا حاجة لـ pip install اي شيء
- **ملف واحد**: قاعدة البيانات كاملة في ملف واحد (.db) - سهلة النقل والنسخ الاحتياطي
- **ACID compliant**: ضمان سلامة البيانات حتى في حالة انقطاع التيار
- **اداء ممتاز**: اسرع من ملفات JSON للقراءة/الكتابة المتكررة

### 2. WAL Mode (Write-Ahead Logging)
تفعيل WAL mode عبر `PRAGMA journal_mode=WAL` يعطينا:
- قراءة متزامنة بدون حجب (concurrent readers)
- كتابة بدون حجب القراءات الجارية
- اداء افضل في حالات القراءة المكثفة (read-heavy workloads)

### 3. JSON Columns للمرونة
استخدام اعمدة TEXT تحتوي JSON للحقول المعقدة:
- `scope_json`: كائن Scope بكل تفاصيله
- `claims_json`: قوائم المزاعم النظرية
- `data_json`: بيانات اضافية متغيرة البنية
- `meta_json`: metadata عامة

هذا يعطينا مرونة schema بدون الحاجة لـ ALTER TABLE عند اضافة حقول جديدة.

### 4. واجهة موحدة (Drop-in Replacement)
كل store يطبق نفس واجهة النسخة المحفوظة في الذاكرة:
- `SQLiteMemoryStore` = نفس واجهة `InMemoryMemoryStore`
- `SQLiteConceptRegistry` = نفس واجهة `InMemoryConceptRegistry`
- `SQLiteTheoryRegistry` = نفس واجهة `InMemoryTheoryRegistry`

التبديل بينهم عبر `APIConfig.use_persistence = True/False`.

### 5. Checkpointing للاستمرارية
- `save_checkpoint(session_id, state_dict, db_path)`: حفظ حالة كاملة كـ JSON
- `load_checkpoint(session_id, db_path)`: استعادة اخر حالة محفوظة
- كل session له checkpoints مستقلة
- يمكن حفظ عدة checkpoints لنفس الجلسة (versioning)

### 6. ادارة Schema عبر migrations.py
- `initialize_database()`: انشاء كل الجداول + الفهارس
- `schema_version` table: تتبع اصدار schema الحالي
- `CREATE TABLE IF NOT EXISTS`: آمنة للتشغيل المتكرر (idempotent)

## البنية المعمارية

```
virtual_genesis/persistence/
    __init__.py              # تصدير كل الكلاسات
    migrations.py            # انشاء الجداول والفهارس
    sqlite_store.py          # SQLiteMemoryStore
    sqlite_concept_registry.py  # SQLiteConceptRegistry
    sqlite_theory_registry.py   # SQLiteTheoryRegistry
    sqlite_identity_store.py    # SQLiteIdentityStore
    checkpoint.py            # save/load checkpoint
```

## الجداول

| الجدول | الغرض |
|--------|-------|
| memories | تخزين MemoryUnit بكل حقولها |
| concepts | تخزين ConceptCard (المفاهيم المعتمدة) |
| candidates | تخزين ConceptCandidate (المفاهيم المرشحة) |
| theories | تخزين LocalTheoryObject |
| identity | تخزين AgentIdentityObject |
| checkpoints | نقاط حفظ حالة الجلسات |
| schema_version | اصدار schema الحالي |

## الاختبارات
37 اختبار يغطي:
- انشاء الجداول وتفعيل WAL
- CRUD كامل لكل store
- Deduplication بالاسم (المفاهيم/النظريات)
- Checkpoint save/load
- استمرارية البيانات عبر instances مختلفة
- تكامل Session مع persistence
