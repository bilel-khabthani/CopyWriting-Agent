"""Thin, dependency-light client for a local Ollama server.

Phase 1 deliverable: a single reusable object that talks to Ollama's
/api/chat endpoint, supports JSON output, retries transient failures, and
turns low-level network errors into friendly, actionable messages.
"""

import json
import time
from typing import Any, Optional

import httpx

import config


class OllamaError(Exception):
    """Base class for any Ollama communication problem."""


class OllamaConnectionError(OllamaError):
    """Ollama is not reachable (server down / wrong host)."""


class OllamaModelError(OllamaError):
    """The requested model is missing or failed to load."""


class OllamaClient:
    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self.host = (host or config.OLLAMA_HOST).rstrip("/")
        self.model = model or config.MODEL
        self.timeout = timeout or config.REQUEST_TIMEOUT
        self._client = httpx.Client(base_url=self.host, timeout=self.timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "OllamaClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def _post_chat(self, payload: dict) -> dict:
        try:
            resp = self._client.post("/api/chat", json=payload)
        except httpx.ConnectError as exc:
            raise OllamaConnectionError(
                "Can't reach Ollama at {0}. Start it with: ollama serve".format(self.host)
            ) from exc
        except httpx.TimeoutException as exc:
            raise OllamaError(
                "Ollama took longer than {0:.0f}s to respond.".format(self.timeout)
            ) from exc
        except httpx.HTTPError as exc:
            raise OllamaError("Network error talking to Ollama: {0}".format(exc)) from exc

        if resp.status_code == 404:
            model = payload.get("model", self.model)
            raise OllamaModelError(
                "Model '{0}' is not installed. Run: ollama pull {0}".format(model)
            )
        if resp.status_code >= 400:
            raise OllamaError(
                "Ollama returned {0}: {1}".format(resp.status_code, resp.text[:300])
            )
        return resp.json()

    def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        num_ctx: Optional[int] = None,
        num_predict: Optional[int] = None,
        json_mode: bool = False,
        model: Optional[str] = None,
        retries: int = 2,
    ) -> str:
        """Send a chat request and return the assistant text."""
        model = model or self.model
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": config.KEEP_ALIVE,
            "options": {
                "temperature": temperature,
                "num_ctx": num_ctx or config.NUM_CTX,
                "num_predict": num_predict or config.NUM_PREDICT,
            },
        }
        if json_mode:
            payload["format"] = "json"

        last_error = None
        for attempt in range(retries + 1):
            try:
                data = self._post_chat(payload)
                content = (data.get("message") or {}).get("content", "")
                if not content.strip():
                    raise OllamaError("The model returned an empty response.")
                return content
            except (OllamaConnectionError, OllamaModelError):
                raise
            except OllamaError as exc:
                last_error = exc
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
        raise last_error

    def chat_json(
        self,
        messages: list,
        temperature: float = 0.3,
        model: Optional[str] = None,
        retries: int = 2,
    ) -> Any:
        """Send a chat request that must return valid JSON."""
        raw = self.chat(
            messages,
            temperature=temperature,
            json_mode=True,
            model=model,
            retries=retries,
        )
        return self._parse_json(raw)

    @staticmethod
    def _parse_json(raw: str) -> Any:
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise OllamaError("The model did not return valid JSON.") from exc

    def is_available(self) -> bool:
        try:
            return self._client.get("/api/tags").status_code == 200
        except httpx.HTTPError:
            return False

    def model_installed(self, model: Optional[str] = None) -> bool:
        model = model or self.model
        try:
            resp = self._client.get("/api/tags")
            resp.raise_for_status()
        except httpx.HTTPError:
            return False
        base = model.split(":")[0]
        names = [m.get("name", "") for m in resp.json().get("models", [])]
        return any(n == model or n.split(":")[0] == base for n in names)


if __name__ == "__main__":
    client = OllamaClient()
    print("Ollama reachable :", client.is_available())
    print("Host             :", client.host)
    print("Model installed  :", client.model_installed())
    reply = client.chat(
        [{"role": "user", "content": "Reply with the single word: ready"}],
        temperature=0.0,
        num_predict=16,
    )
    print("Model reply      :", reply.strip())
    client.close()
