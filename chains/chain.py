from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda
from pathlib import Path
from llm.model import get_local_llm
from prompts.prompt import BROWSER_WORKER_PROMPT, EXECUTOR_PROMPT, PROGRESS_PROMPT
from tools.agent_tools import browser_tools, click_at

MODEL_DIR = Path(__file__).resolve().parent.parent / "llm_model"
MODEL_PATH = MODEL_DIR / "Qwen3.5-4B-Q4_K_M.gguf"
MMPROJ_PATH = MODEL_DIR / "mmproj-F32.gguf"

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



llm = llm = get_local_llm(model_path=MODEL_PATH, mmproj_path=MMPROJ_PATH)
llm_with_tools = llm.bind_tools(browser_tools)

progress_chain = PROGRESS_PROMPT | llm | RunnableLambda(print_tokens("progress_chain")) | JsonOutputParser()

browser_worker_chain =  BROWSER_WORKER_PROMPT | llm_with_tools | RunnableLambda(print_tokens("browser_worker_chain"))

executor_chain = EXECUTOR_PROMPT | llm.bind_tools([click_at]) | JsonOutputParser() | RunnableLambda(print_tokens("executor_chain"))


 