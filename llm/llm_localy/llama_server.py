import subprocess
import time
from pathlib import Path

import httpx
from langchain_openai import ChatOpenAI


BASE_DIR = Path(__file__).resolve().parents[2]
SERVER_PATH = BASE_DIR / "llama_cpp_server" / "llama-server.exe"

HOST = "127.0.0.1"
PORT = 8080
BASE_URL = f"http://{HOST}:{PORT}"


class LlamaServer:
    def __init__(self):
        self.process = None
        self.model_path = None
        self.mmproj_path = None

    def load_model( self, model_path: str,  mmproj_path: str | None = None, n_ctx: int = 4096,  n_gpu_layers: int = 99 ):
        path = Path(model_path).resolve()

        if not path.is_file():
            raise FileNotFoundError(f"Model not found: {path}")

        if not SERVER_PATH.is_file():
            raise FileNotFoundError(f"Server not found: {SERVER_PATH}")

        mmproj = None

        if mmproj_path is not None:
            mmproj = Path(mmproj_path).resolve()

            if not mmproj.is_file():
                raise FileNotFoundError( f"Vision projector not found: {mmproj}")

        # Avoid reloading the same model and projector.
        if (  self.model_path == path and self.mmproj_path == mmproj  and self.process is not None  and self.process.poll() is None):
            return

        # Unload the previous model.
        self.unload_model()

        print(f"\nLoading model: {path.name}")

        command = [
            str(SERVER_PATH),
            "-m", str(path),
            "-ngl", str(n_gpu_layers),
            "-c", str(n_ctx),
            "--jinja",
            "--host", HOST,
            "--port", str(PORT),
        ]

        # Enable vision when a projector is supplied.
        if mmproj is not None:
            command.extend(["--mmproj", str(mmproj)])
            print(f"Loading vision projector: {mmproj.name}")

        self.process = subprocess.Popen(
            command,
            cwd=str(SERVER_PATH.parent),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        try:
            self._wait_for_server()
        except Exception:
            self.unload_model()
            raise

        self.model_path = path
        self.mmproj_path = mmproj

        print(f"Model ready: {path.name}")

    def _wait_for_server(self, timeout: int = 120):
        start = time.monotonic()

        while time.monotonic() - start < timeout:
            if self.process.poll() is not None:
                raise RuntimeError(
                    f"llama-server exited with code "
                    f"{self.process.returncode}"
                )

            try:
                response = httpx.get(
                    f"{BASE_URL}/health",
                    timeout=2,
                )

                if response.status_code == 200:
                    return

            except httpx.RequestError:
                pass

            time.sleep(0.5)

        raise TimeoutError("Model loading timed out")

    def get_llm(
        self,
        temperature: float = 0,
        max_tokens: int = 1024,
        streaming: bool = False,
    ):
        if (
            self.process is None
            or self.process.poll() is not None
            or self.model_path is None
        ):
            raise RuntimeError("No model loaded")

        return ChatOpenAI(
            base_url=f"{BASE_URL}/v1",
            api_key="local",
            model=self.model_path.name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            stream_usage=False,
        )

    def unload_model(self):
        if self.process is not None:
            print("\nStopping previous model...")

            if self.process.poll() is None:
                self.process.terminate()

                try:
                    self.process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()

            self.process = None

        self.model_path = None
        self.mmproj_path = None

    def close(self):
        self.unload_model()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()