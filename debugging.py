from langchain_core.runnables import RunnableLambda
from pathlib import Path
from datetime import datetime


LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def save_log(chain_name, log_type, data):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    file_path = LOG_DIR / f"{chain_name}_{log_type}_{timestamp}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(repr(data))

    print(f"[{chain_name}] {log_type} saved: {file_path}")


def print_input(chain_name):
    def _print(data):
        save_log(chain_name, "input", data)
        return data

    return RunnableLambda(_print)


def print_output(chain_name):
    def _print(data):
        save_log(chain_name, "output", data)
        return data

    return RunnableLambda(_print)