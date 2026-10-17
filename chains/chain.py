
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda
from pathlib import Path

from llm.model import get_local_llm
from prompts.prompt import BROWSER_WORKER_PROMPT, PROGRESS_PROMPT
from tools.agent_tools import browser_tools


MODEL_DIR = Path(__file__).resolve().parent.parent / "llm_model"
MODEL_PATH = MODEL_DIR / "Qwen3.5-4B-Q4_K_M.gguf"
MMPROJ_PATH = MODEL_DIR / "mmproj-F32.gguf"
SHOWUI_MODEL_PATH = MODEL_DIR / "showui-2b-q4_k_m.gguf"
SHOWUI_MMPROJ_PATH = MODEL_DIR / "showui-mmproj.gguf"


def print_tokens(chain_name):
    def _print(message):
        usage = message.usage_metadata or {}

        print(
            f"[{chain_name}] "
            f"Input: {usage.get('input_tokens', 0)} | "
            f"Output: {usage.get('output_tokens', 0)} | "
            f"Total: {usage.get('total_tokens', 0)}"
        )

        return message

    return _print


# ==================== LAZY LOADING ====================

def invoke_qwen(messages):
    llm = get_local_llm(model_path=MODEL_PATH,  mmproj_path=MMPROJ_PATH)
    return llm.invoke(messages)


def invoke_qwen_tools(messages):
    llm = get_local_llm( model_path=MODEL_PATH, mmproj_path=MMPROJ_PATH )

    tools = [ tool for tool in browser_tools  if tool.name != "click_at"]
    return llm.bind_tools(tools).invoke(messages)



progress_chain = PROGRESS_PROMPT | RunnableLambda(invoke_qwen) | RunnableLambda(print_tokens("progress_chain")) | JsonOutputParser()

browser_worker_chain = BROWSER_WORKER_PROMPT | RunnableLambda(invoke_qwen_tools) | RunnableLambda(print_tokens("browser_worker_chain"))


