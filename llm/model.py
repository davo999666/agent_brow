from pathlib import Path
from langchain_openai import ChatOpenAI

from llm.llm_localy.llama_server import LlamaServer


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "llm_model"

MODEL_PATH = MODEL_DIR / "Qwen3.5-4B-Q4_K_M.gguf"

# Replace with your actual compatible projector filename
MMPROJ_PATH = MODEL_DIR / "mmproj-F32.gguf"

_server = LlamaServer()


def get_local_llm(
    model_path: str | Path = MODEL_PATH,
    temperature: float = 0.3,
    vision: bool = False,
    mmproj_path: str | Path | None = None,
):
    path = Path(model_path)

    if not path.is_absolute():
        path = BASE_DIR / path

    path = path.resolve()

    projector = None

    if vision:
        projector = Path(mmproj_path or MMPROJ_PATH)

        if not projector.is_absolute():
            projector = BASE_DIR / projector

        projector = projector.resolve()

    if (
        _server.model_path != path
        or _server.mmproj_path != projector
        or _server.process is None
        or _server.process.poll() is not None
    ):
        _server.load_model(
            model_path=str(path),
            mmproj_path=str(projector) if projector else None,
        )

    return ChatOpenAI(
        base_url="http://127.0.0.1:8080/v1",
        api_key="local",
        model=path.name,
        temperature=temperature,
        streaming=True,
        stream_usage=False,
        max_tokens=1024,
    )


def stop_local_llm():
    _server.unload_model()