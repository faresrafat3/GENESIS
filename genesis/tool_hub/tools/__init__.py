# Tool Hub — Tools Package
# Each module defines ALL_TOOLS list
from genesis.tool_hub.tools.web_search import ALL_TOOLS as WEB_TOOLS
from genesis.tool_hub.tools.code_exec import ALL_TOOLS as CODE_TOOLS
from genesis.tool_hub.tools.llm_call import ALL_TOOLS as LLM_TOOLS

ALL_TOOLS = WEB_TOOLS + CODE_TOOLS + LLM_TOOLS
