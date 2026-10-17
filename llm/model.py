
from pathlib import Path
from langchain_openai import ChatOpenAI
from llm.llm_localy.llama_server import LlamaServer

_server = LlamaServer()


def get_local_llm( model_path: str | Path, temperature: float = 0.3, mmproj_path: str | Path | None = None, n_ctx: int = 4096):
    path = Path(model_path).resolve()

    if not path.is_file():
        raise FileNotFoundError(f"Model not found: {path}")

    projector = Path(mmproj_path).resolve() if mmproj_path else None
    projector = projector if projector and projector.is_file() else None

    if (
        _server.model_path != path
        or _server.mmproj_path != projector
        or _server.process is None
        or _server.process.poll() is not None
        or getattr(_server, "n_ctx", None) != n_ctx
    ):
        _server.load_model(
            model_path=str(path),
            mmproj_path=str(projector) if projector else None,
            n_ctx=n_ctx,
        )

    return ChatOpenAI(
        base_url="http://127.0.0.1:8080/v1",
        api_key="local",
        model=path.name,
        temperature=temperature,
        streaming=True,
        stream_usage=True,
        max_tokens=1024,
    )


def get_showui_llm(model_path: str | Path, mmproj_path: str | Path):
    return get_local_llm(
        model_path=model_path,
        mmproj_path=mmproj_path,
        temperature=0,
        n_ctx=2048,
    )


def stop_local_llm():
    _server.unload_model()
