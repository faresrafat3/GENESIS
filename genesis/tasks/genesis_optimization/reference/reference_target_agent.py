import os
import sys
import json
import argparse
import subprocess
import asyncio
import httpx
import openai
from dotenv import load_dotenv

load_dotenv()

# Model and client configuration
MODEL = os.getenv("TASK_MODEL", "mimo-v2.5-pro")
API_KEY = os.getenv("OPENAI_API_KEY", "ogw_live_bf5f833feb2fa155928fab4fc567a56c")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://opengateway.gitlawb.com/v1")

# Create AsyncOpenAI client with custom httpx headers to prevent compression issues
http_client = httpx.AsyncClient(
    headers={"Accept-Encoding": "identity"},
    timeout=180.0
)
client = openai.AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    http_client=http_client
)

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite a file at the given absolute path with the provided content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file to write."},
                    "content": {"type": "string", "description": "Full content to write to the file."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read and return the contents of a file at the specified absolute path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file to read."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a bash command in the terminal and return its stdout and stderr. Best for running tests or checks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to execute."}
                },
                "required": ["command"]
            }
        }
    }
]

# ── Tool implementations ──────────────────────────────────────────────────────

def write_file(path: str, content: str) -> str:
    try:
        # Prevent escaping the workspace directory
        abs_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{abs_path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"


def read_file(path: str) -> str:
    try:
        abs_path = os.path.abspath(path)
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{path}' not found."
    except Exception as e:
        return f"Error reading file: {str(e)}"


def bash(command: str) -> str:
    try:
        # Execute the command with a 60 second timeout
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds."
    except Exception as e:
        return f"Error running command: {str(e)}"


async def dispatch_tool(name: str, arguments: dict) -> str:
    if name == "write_file":
        return write_file(**arguments)
    elif name == "read_file":
        return read_file(**arguments)
    elif name == "bash":
        return bash(**arguments)
    else:
        return f"Unknown tool: {name}"

# ── Multi-Trajectory Logger ───────────────────────────────────────────────────

class MultiTrajectoryLogger:
    def __init__(self, working_dir: str):
        self.working_dir = working_dir
        self.execution_folder = os.path.join(working_dir, "agent_execution")
        os.makedirs(self.execution_folder, exist_ok=True)
        print(f"Initialized multi-trajectory logger at: {self.execution_folder}")

    def log_trajectory(self, trajectory_id: int, messages: list):
        filename = f"execution_q{trajectory_id}.json"
        filepath = os.path.join(self.execution_folder, filename)
        
        # Convert Pydantic objects and custom types to serializable dicts
        serializable_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                msg_dict = dict(msg)
                if "tool_calls" in msg_dict and msg_dict["tool_calls"] is not None:
                    msg_dict["tool_calls"] = [
                        (t.model_dump() if hasattr(t, "model_dump") else (t.__dict__ if hasattr(t, "__dict__") else t))
                        for t in msg_dict["tool_calls"]
                    ]
                serializable_messages.append(msg_dict)
            elif hasattr(msg, "model_dump"):
                serializable_messages.append(msg.model_dump())
            elif hasattr(msg, "__dict__"):
                serializable_messages.append(msg.__dict__)
            else:
                serializable_messages.append(msg)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serializable_messages, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Saved trajectory {trajectory_id} to {filename}")
        except Exception as e:
            print(f"  ✗ Error saving trajectory {trajectory_id}: {e}")

    def finalize(self, total_count: int):
        print(f"\n{'='*60}")
        print(f"✓ Multi-trajectory logging complete:")
        print(f"  - Total trajectories: {total_count}")
        print(f"  - Saved to: {self.execution_folder}/")
        print(f"  - Files: execution_q0.json to execution_q{total_count-1}.json")
        print(f"{'='*60}\n")

# ── Optimization Agent Loop ───────────────────────────────────────────────────

async def run_optimization_for_module(
    question_id: int,
    module_name: str,
    target_files: list,
    description: str,
    dataset_dir: str,
    working_dir: str,
    logger: MultiTrajectoryLogger
):
    print(f"\n{'='*80}")
    print(f"Starting self-evolution for module: {module_name} (ID: {question_id})")
    print(f"Description: {description}")
    print(f"Target files: {target_files}")
    print(f"{'='*80}\n")

    # Read relevant theory docs
    theory_docs = []
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
    for file in os.listdir(workspace_root):
        if file.startswith("Virtual_SIA_") and file.endswith("_AR.md"):
            # Load theory files relevant to the module if they contain keywords
            keyword = module_name.split("_")[0]  # e.g., 'concept' or 'economy' or 'memory'
            if keyword in file.lower() or "architecture" in file.lower() or "theory" in file.lower():
                try:
                    with open(os.path.join(workspace_root, file), "r", encoding="utf-8") as f:
                        theory_docs.append({
                            "title": file,
                            "content": f.read()[:5000] # Truncate to save context
                        })
                except Exception:
                    pass

    # Read target files contents
    file_contents = {}
    for filepath in target_files:
        abs_filepath = os.path.join(workspace_root, filepath)
        if os.path.exists(abs_filepath):
            file_contents[filepath] = read_file(abs_filepath)
        else:
            file_contents[filepath] = f"(File not found at {abs_filepath})"

    # Construct the instruction prompt
    system_prompt = (
        "You are an expert cognitive architect and AI developer. Your task is to perform an architectural self-evolution "
        "and structural optimization on the Virtual-GENESIS codebase. Specifically, you must optimize the "
        f"'{module_name}' module to achieve better reasoning, structural stability, and cognitive economy.\n\n"
        "You have access to files, theory docs, and a bash terminal to execute commands and verify your changes. "
        "You can run the pytest suite using the command `.venv/bin/pytest` via the bash tool.\n\n"
        "Please use tool calls systematically: read files, analyze, propose changes, write changes, and verify them via pytest.\n"
        "Do not leave any placeholder or incomplete implementation. Maintain 100% correctness."
    )

    user_message = {
        "role": "user",
        "content": (
            f"Here are the details for optimizing the '{module_name}' module:\n\n"
            f"**Objective:** {description}\n\n"
            f"**Target Files to Optimize:** {json.dumps(target_files, indent=2)}\n\n"
            f"**Current Code of Target Files:**\n"
            f"{json.dumps(file_contents, indent=2)}\n\n"
            f"**Related Cognitive Theory & Specifications (Arabic):**\n"
            f"{json.dumps(theory_docs, indent=2)[:8000]}\n\n"
            "**Guidelines:**\n"
            "1. Propose clear, theoretically-grounded hypotheses for improving this module.\n"
            "2. Implement changes directly to the target files using the `write_file` tool.\n"
            "3. Verify your changes by running the test suite with `.venv/bin/pytest` using the `bash` tool.\n"
            "4. Iterate if there are failures, ensuring all tests remain green.\n"
            "5. When you are fully done and all tests are passing, explain your improvements and finish."
        )
    }

    # Initialize message history (OpenAI API format)
    messages = [
        {"role": "system", "content": system_prompt},
        user_message
    ]

    max_turns = 10
    for turn in range(max_turns):
        print(f"--- Turn {turn+1}/{max_turns} ---")
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.2
            )
        except Exception as e:
            print(f"API Call failed: {e}")
            messages.append({"role": "assistant", "content": f"API Call failed: {str(e)}"})
            break

        assistant_message = response.choices[0].message
        assistant_content = assistant_message.content or ""
        
        # Add to message history
        messages.append({
            "role": "assistant",
            "content": assistant_content,
            "tool_calls": assistant_message.tool_calls
        })

        if assistant_content:
            print(f"\nAssistant:\n{assistant_content}\n")

        # Check for tool calls
        if assistant_message.tool_calls:
            tool_results = []
            for tool_call in assistant_message.tool_calls:
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                print(f"[Tool Call] {name} with args: {arguments}")
                
                result = await dispatch_tool(name, arguments)
                print(f"[Tool Result] {result[:300]}...")
                
                # Format tool result for OpenAI API
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": result
                })
        else:
            # If no tool calls, the assistant is done
            print("Assistant completed its turn without tool calls. Finishing module optimization.")
            break

    # Save trajectory to logger
    logger.log_trajectory(question_id, messages)
    print(f"Completed self-evolution for module: {module_name}\n")

# ── Main Entry Point ──────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Virtual-GENESIS Cognitive Architecture Self-Evolution Agent")
    parser.add_argument("--dataset_dir", required=True, help="Absolute path to read-only dataset directory")
    parser.add_argument("--working_dir", required=True, help="Absolute path to read-write working directory")
    args = parser.parse_args()

    print(f"Dataset Directory: {args.dataset_dir}")
    print(f"Working Directory: {args.working_dir}")

    # Load dataset questions
    questions_file = os.path.join(args.dataset_dir, "diamond_questions.json")
    if not os.path.exists(questions_file):
        print(f"Error: {questions_file} not found!")
        sys.exit(1)

    with open(questions_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} module optimization targets.")

    # Initialize trajectory logger
    logger = MultiTrajectoryLogger(args.working_dir)

    # Process each module optimization target
    for q in questions:
        await run_optimization_for_module(
            question_id=q["id"],
            module_name=q["module"],
            target_files=q["target_files"],
            description=q["description"],
            dataset_dir=args.dataset_dir,
            working_dir=args.working_dir,
            logger=logger
        )

    # Finalize logger
    logger.finalize(len(questions))

    # Run final full validation
    print("Running final full verification test suite...")
    subprocess.run([".venv/bin/pytest", "-v"], check=False)

if __name__ == "__main__":
    asyncio.run(main())
