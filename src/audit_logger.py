import os
import json
from datetime import datetime
from loguru import logger

AUDIT_LOG_FILE = "logs/audit_trail.jsonl"

def log_query(user_role: str, question: str, answer: str, sources: list, knowledge_area: str, confidence: str, assistant_type: str):
    """Logs query details for compliance and audit purposes."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_role": user_role,
        "knowledge_area": knowledge_area,
        "assistant_type": assistant_type,
        "question": question,
        "answer": answer,
        "sources": sources,
        "confidence": confidence
    }

    try:
        os.makedirs(os.path.dirname(AUDIT_LOG_FILE), exist_ok=True)
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")

def get_audit_logs(limit: int = 50):
    """Retrieves the latest audit logs."""
    logs = []
    if not os.path.exists(AUDIT_LOG_FILE):
        return logs

    try:
        with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                logs.append(json.loads(line))
        return list(reversed(logs))
    except Exception as e:
        logger.error(f"Failed to read audit logs: {e}")
        return []
