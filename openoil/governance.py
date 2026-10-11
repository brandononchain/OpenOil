"""
OpenOil Governance & Audit
Human-in-the-loop approval queue and full immutable audit log.
"""

import json
import time
import os
from typing import Dict, List, Optional
from datetime import datetime

AUDIT_FILE = os.getenv("AUDIT_FILE", "openoil_audit.jsonl")
APPROVAL_FILE = os.getenv("APPROVAL_FILE", "openoil_approvals.json")

class Governance:
    def __init__(self):
        self.pending: List[Dict] = []
        self.load_pending()

    def load_pending(self):
        if os.path.exists(APPROVAL_FILE):
            try:
                with open(APPROVAL_FILE) as f:
                    self.pending = json.load(f)
            except Exception:
                self.pending = []

    def save_pending(self):
        try:
            with open(APPROVAL_FILE, "w") as f:
                json.dump(self.pending, f, default=str, indent=2)
        except Exception:
            pass

    def request_approval(self, signal: Dict, analysis: Dict, reason: str = "high_impact") -> str:
        """Queue a trade for human approval."""
        req_id = f"req_{int(time.time())}"
        entry = {
            "id": req_id,
            "timestamp": datetime.utcnow().isoformat(),
            "signal": signal,
            "analysis_summary": {
                "bias": analysis.get("overall_bias"),
                "ensemble": analysis.get("ensemble", {}).get("ensemble_bias"),
                "regime": analysis.get("regime", {}).get("regime")
            },
            "reason": reason,
            "status": "pending"
        }
        self.pending.append(entry)
        self.save_pending()
        self.audit("approval_requested", entry)
        return req_id

    def approve(self, req_id: str, approver: str = "human") -> Dict:
        for p in self.pending:
            if p["id"] == req_id and p["status"] == "pending":
                p["status"] = "approved"
                p["approver"] = approver
                p["approved_at"] = datetime.utcnow().isoformat()
                self.save_pending()
                self.audit("approval_granted", p)
                return p
        return {"error": "not_found"}

    def reject(self, req_id: str, reason: str = "") -> Dict:
        for p in self.pending:
            if p["id"] == req_id and p["status"] == "pending":
                p["status"] = "rejected"
                p["reject_reason"] = reason
                self.save_pending()
                self.audit("approval_rejected", p)
                return p
        return {"error": "not_found"}

    def audit(self, event: str, payload: Dict):
        """Append-only audit log."""
        record = {
            "ts": time.time(),
            "iso": datetime.utcnow().isoformat(),
            "event": event,
            "payload": payload
        }
        try:
            with open(AUDIT_FILE, "a") as f:
                f.write(json.dumps(record, default=str) + "\n")
        except Exception:
            pass

    def recent_audit(self, limit: int = 20) -> List[Dict]:
        if not os.path.exists(AUDIT_FILE):
            return []
        lines = []
        try:
            with open(AUDIT_FILE) as f:
                lines = f.readlines()[-limit:]
        except Exception:
            return []
        return [json.loads(l) for l in lines if l.strip()]

    def pending_approvals(self) -> List[Dict]:
        return [p for p in self.pending if p["status"] == "pending"]
