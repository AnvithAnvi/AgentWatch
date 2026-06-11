import threading
import time
import queue
import requests
from typing import Optional, Dict, Any


class Sender:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None,
                 batch_size: int = 10, flush_interval: float = 1.0):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self._q: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def post(self, path: str, json: Dict[str, Any]):
        # return a placeholder immediate response dict to keep compatibility
        self._q.put(("POST", path, json))
        return {"queued": True}

    def patch(self, path: str, json: Dict[str, Any]):
        self._q.put(("PATCH", path, json))
        return {"queued": True}

    def _worker(self):
        batch = []
        last_flush = time.time()
        while not self._stop.is_set():
            try:
                item = self._q.get(timeout=self.flush_interval)
                batch.append(item)
            except Exception:
                pass

            now = time.time()
            if (len(batch) >= self.batch_size) or (batch and now - last_flush >= self.flush_interval):
                self._flush(batch)
                batch = []
                last_flush = now

        # flush remaining
        if batch:
            self._flush(batch)

    def _flush(self, batch):
        for method, path, payload in batch:
            try:
                url = f"{self.base_url}{path}"
                if method == "POST":
                    requests.post(url, json=payload, headers=self.headers, timeout=5)
                elif method == "PATCH":
                    requests.patch(url, json=payload, headers=self.headers, timeout=5)
            except Exception:
                # best-effort, drop on failure
                pass

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=2)
