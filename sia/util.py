import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Literal

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

# Backend type definition
AgentBackend = Literal["claude", "openhands", "openai"]


async def run_agent_claude(model_name, max_turns, prompt, agent_working_directory):
    """Run agent using Claude Code SDK

    Note: Claude Code automatically saves trajectories to ~/.claude/projects/
    """
    from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

    logger.info("=" * 80)
    logger.info(f"Starting agent execution with {model_name} model")
    logger.info(f"Working directory: {agent_working_directory}")
    logger.info(f"Max turns: {max_turns}")
    logger.info("=" * 80)

    turn_count = 0
    start_time = datetime.now()

    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                cwd=agent_working_directory,
                allowed_tools=["Bash", "Read", "Write", "Edit", "Glob"],
                permission_mode="bypassPermissions",
                max_turns=max_turns,
                model=model_name,
            ),
        ):
            logged_content = False

            if hasattr(message, "content") and message.content:
                for block in message.content:
                    # Log agent text responses
                    if hasattr(block, "text") and block.text:
                        if not logged_content:
                            turn_count += 1
                            logger.info(f"\n{'─' * 80}")
                            logger.info(f"TURN {turn_count}: Agent Response")
                            logger.info(f"{'─' * 80}")
                            logged_content = True
                        logger.info(f"{block.text}")

                    # Log tool calls
                    elif hasattr(block, "name"):
                        if not logged_content:
                            turn_count += 1
                            logger.info(f"\n{'─' * 80}")
                            logger.info(f"TURN {turn_count}: Tool Execution")
                            logger.info(f"{'─' * 80}")
                            logged_content = True

                        logger.info(f"🔧 Tool: {block.name}")
                        if hasattr(block, "input") and block.input:
                            # Pretty print tool input
                            import json

                            try:
                                input_str = json.dumps(block.input, indent=2)
                                logger.info(f"   Input: {input_str}")
                            except (TypeError, ValueError):
                                logger.info(f"   Input: {block.input}")

                    # Log tool results
                    elif hasattr(block, "type") and block.type == "tool_result":
                        if hasattr(block, "content"):
                            result = block.content if isinstance(block.content, str) else str(block.content)
                            # Truncate very long outputs
                            if len(result) > 500:
                                result = result[:500] + f"\n... (truncated, {len(result)} total chars)"
                            logger.info(f"   ✓ Result: {result}")

            # Log final result
            if isinstance(message, ResultMessage):
                elapsed_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"\n{'=' * 80}")
                logger.info("EXECUTION COMPLETE")
                logger.info(f"{'=' * 80}")
                logger.info(f"Total turns: {turn_count}")
                logger.info(f"Execution time: {elapsed_time:.2f} seconds")
                logger.info(f"Final result: {message.result}")
                logger.info(f"{'=' * 80}")

    except Exception as e:
        logger.error(f"\n{'!' * 80}")
        logger.error(f"ERROR: {e!s}")
        logger.error(f"{'!' * 80}", exc_info=True)
        raise


async def run_agent_openhands(model_name, max_turns, prompt, agent_working_directory):
    """Run agent using OpenHands SDK"""
    try:
        from openhands.sdk import LLM, Agent, Conversation, Tool
        from openhands.tools.file_editor import FileEditorTool
        from openhands.tools.terminal import TerminalTool
    except ImportError:
        logger.error("OpenHands SDK not installed. Install with: pip install openhands-ai")
        raise

    logger.info("=" * 80)
    logger.info(f"Starting OpenHands agent execution with {model_name} model")
    logger.info(f"Working directory: {agent_working_directory}")
    logger.info(f"Max turns: {max_turns}")
    logger.info("=" * 80)

    turn_count = 0
    start_time = datetime.now()

    try:
        # Determine API key based on model provider
        api_key = None
        if "claude" in model_name.lower() or "anthropic" in model_name.lower():
            api_key = os.getenv("ANTHROPIC_API_KEY")
        elif "gemini" in model_name.lower() or "google" in model_name.lower():
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        elif "gpt" in model_name.lower() or "openai" in model_name.lower():
            api_key = os.getenv("OPENAI_API_KEY")
        else:
            # Fallback to generic LLM_API_KEY
            api_key = os.getenv("LLM_API_KEY")

        if not api_key:
            logger.warning(f"No API key found for model {model_name}. Using LLM_API_KEY if available.")
            api_key = os.getenv("LLM_API_KEY")

        # Create LLM instance
        llm = LLM(
            model=model_name,
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE") or os.getenv("LLM_BASE_URL"),
        )

        # Create agent with available tools
        agent = Agent(
            llm=llm,
            tools=[
                Tool(name=TerminalTool.name),
                Tool(name=FileEditorTool.name),
            ],
        )

        # Create conversation with workspace and persistence
        # Trajectory will be saved in: agent_working_directory/openhands_trajectory/
        trajectory_dir = os.path.join(agent_working_directory, "openhands_trajectory")

        conversation = Conversation(agent=agent, workspace=agent_working_directory, persistence_dir=trajectory_dir)

        # Send the task prompt
        logger.info(f"\n{'─' * 80}")
        logger.info(f"TURN {turn_count + 1}: Sending prompt to agent")
        logger.info(f"{'─' * 80}")
        conversation.send_message(prompt)

        # Run the agent
        logger.info(f"Running agent (max turns: {max_turns})...")
        logger.info(f"  → Trajectory will be saved to: {trajectory_dir}")
        result = conversation.run()

        # Log completion
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"\n{'=' * 80}")
        logger.info("EXECUTION COMPLETE")
        logger.info(f"{'=' * 80}")
        logger.info(f"Execution time: {elapsed_time:.2f} seconds")
        logger.info(f"Final result: {result}")
        logger.info(f"  ✓ Trajectory saved to: {trajectory_dir}")
        logger.info(f"{'=' * 80}")

    except Exception as e:
        logger.error(f"\n{'!' * 80}")
        logger.error(f"ERROR: {e!s}")
        logger.error(f"{'!' * 80}", exc_info=True)
        raise


def _make_openai_client():
    """Create an OpenAI client with compression disabled to work around gateway gzip issues."""
    import openai

    api_key = (
        os.getenv("OPENAI_API_KEY")
        or os.getenv("LLM_API_KEY")
        or "dummy"
    )
    base_url = (
        os.getenv("OPENAI_BASE_URL")
        or os.getenv("OPENAI_API_BASE")
        or os.getenv("LLM_BASE_URL")
    )

    http_client = httpx.Client(
        headers={"Accept-Encoding": "identity"},
        timeout=120.0,
    )

    kwargs = dict(api_key=api_key, http_client=http_client)
    if base_url:
        kwargs["base_url"] = base_url

    return openai.OpenAI(**kwargs)


async def run_agent_openai(model_name, max_turns, prompt, agent_working_directory):
    """Run an agentic loop using the OpenAI client directly with bash + file tools.

    Works with any OpenAI-compatible gateway (e.g. openGateway).
    The httpx client is configured with Accept-Encoding: identity to prevent
    gzip decompression errors from non-standard gateways.
    """
    import asyncio

    client = _make_openai_client()

    # Strip provider prefix if present (e.g. "openai/mimo-v2.5-pro" -> "mimo-v2.5-pro")
    bare_model = model_name.split("/", 1)[-1] if "/" in model_name else model_name

    # Tool definitions: bash execution + file read/write
    tools = [
        {
            "type": "function",
            "function": {
                "name": "bash",
                "description": "Run a bash command in the agent working directory and return stdout+stderr.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The bash command to execute."}
                    },
                    "required": ["command"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file (creates parent dirs automatically).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Absolute or relative file path."},
                        "content": {"type": "string", "description": "File content to write."},
                    },
                    "required": ["path", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the content of a file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Absolute or relative file path."},
                    },
                    "required": ["path"],
                },
            },
        },
    ]

    def execute_tool(name: str, args: dict) -> str:
        """Execute a tool call and return the string result."""
        try:
            if name == "bash":
                cmd = args.get("command", "")
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=agent_working_directory,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    executable="/bin/bash",
                )
                output = result.stdout + result.stderr
                if len(output) > 8000:
                    output = output[:4000] + "\n...[truncated]...\n" + output[-4000:]
                return output or "(no output)"

            elif name == "write_file":
                path = args["path"]
                content = args["content"]
                if not os.path.isabs(path):
                    path = os.path.join(agent_working_directory, path)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Written {len(content)} bytes to {path}"

            elif name == "read_file":
                path = args["path"]
                if not os.path.isabs(path):
                    path = os.path.join(agent_working_directory, path)
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                if len(content) > 8000:
                    content = content[:8000] + "\n...[truncated]..."
                return content

            else:
                return f"Unknown tool: {name}"

        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out after 120 seconds"
        except Exception as exc:
            return f"ERROR: {exc}"

    logger.info("=" * 80)
    logger.info(f"Starting OpenAI agent execution with model: {bare_model}")
    logger.info(f"Working directory: {agent_working_directory}")
    logger.info(f"Max turns: {max_turns}")
    logger.info("=" * 80)

    messages = [{"role": "user", "content": prompt}]
    max_turns_int = int(max_turns) if isinstance(max_turns, str) else max_turns
    start_time = datetime.now()
    turn_count = 0

    loop = asyncio.get_event_loop()

    while turn_count < max_turns_int:
        turn_count += 1
        logger.info(f"\n{'─' * 80}")
        logger.info(f"TURN {turn_count}: Calling model {bare_model}")
        logger.info(f"{'─' * 80}")

        try:
            response = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model=bare_model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                ),
            )
        except Exception as exc:
            logger.error(f"LLM call failed: {exc}")
            raise

        choice = response.choices[0]
        msg = choice.message

        # Append assistant message
        assistant_msg = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ]
        messages.append(assistant_msg)

        if msg.content:
            logger.info(f"Assistant: {msg.content[:500]}")

        # If no tool calls, the agent is done
        if not msg.tool_calls:
            logger.info("Agent finished (no tool calls).")
            break

        # Execute all tool calls
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            try:
                fn_args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                fn_args = {}

            logger.info(f"🔧 Tool: {fn_name}({list(fn_args.keys())})")
            result_str = execute_tool(fn_name, fn_args)
            logger.info(f"   ✓ Result preview: {result_str[:200]}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result_str,
            })

        # Check stop reason
        if choice.finish_reason == "stop":
            logger.info("Agent finished (stop reason).")
            break

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"\n{'=' * 80}")
    logger.info("EXECUTION COMPLETE")
    logger.info(f"Total turns: {turn_count} | Time: {elapsed:.1f}s")
    logger.info(f"{'=' * 80}")


async def run_agent(
    model_name: str, max_turns: str, prompt: str, agent_working_directory: str, backend: AgentBackend = "claude"
):
    """
    Run an agent with the specified backend.

    Args:
        model_name: The model to use (format depends on backend)
        max_turns: Maximum number of turns for the agent
        prompt: The task prompt to send to the agent
        agent_working_directory: Working directory for the agent
        backend: Which agent backend to use ("claude", "openhands", or "openai")

    Examples:
        # Claude backend with Claude models
        await run_agent("haiku", 20, prompt, "/path/to/dir", backend="claude")

        # OpenHands backend with Gemini
        await run_agent("gemini/gemini-3.1-pro-preview", 20, prompt, "/path/to/dir", backend="openhands")

        # OpenAI-compatible backend (openGateway, etc.) with compression fix
        await run_agent("openai/mimo-v2.5-pro", 20, prompt, "/path/to/dir", backend="openai")
    """
    logger.info(f"Using {backend} backend")

    if backend == "claude":
        await run_agent_claude(model_name, max_turns, prompt, agent_working_directory)
    elif backend == "openhands":
        await run_agent_openhands(model_name, max_turns, prompt, agent_working_directory)
    elif backend == "openai":
        await run_agent_openai(model_name, max_turns, prompt, agent_working_directory)
    else:
        raise ValueError(f"Unknown backend: {backend}. Must be 'claude', 'openhands', or 'openai'")
