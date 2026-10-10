"""Human-in-the-loop approval queue and audit log."""

import json
import os
import time
from datetime import datetime
from typing import Dict, List

AUDIT_FILE = os.getenv("AUDIT_FILE", "openoil_audit.jsonl")
PENDING_FILE = os.getenv("PENDING_FILE", "openoil_pending.json")

class Governance:
    def __init__(self):
        self.pending = []
        self.load_pending()

    def load_pending(self):
        if os.path.exists(PENDING_FILE):
            try:
                with open(PENDING_FILE) as f:
                    self.pending = json.load(f)
            except Exception:
                self.pending = []

    def save_pending(self):
        try:
            with open(PENDING_FILE, "w") as f:
                json.dump(self.pending, f, indent=2)
        except Exception:
            pass

    def requires_approval(self, signal: Dict) -> bool:
        return abs(signal.get("confidence", 0)) > 0.7

    def request_approval(self, signal: Dict, analysis: Dict, reason: str = "high_impact") -> str:
        req_id = f"req_{int(time.time())}"
        entry = {"id": req_id, "timestamp": datetime.utcnow().isoformat(), "signal": signal, "status": "pending"}
        self.pending.append(entry)
        self.save_pending()
        return req_id
