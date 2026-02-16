from datetime import datetime
from typing import List, Dict

class MemoryManager:
    def __init__(self, max_history: int = 5):
        self.max_history = max_history
        self.history: List[Dict] = []

    def add_exchange(self, question: str, answer: str):
        self.history.append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_history(self) -> List[Dict]:
        return self.history

    def get_formatted_history(self) -> str:
        formatted = ""
        for exchange in self.history:
            formatted += f"User: {exchange['question']}\nAgent: {exchange['answer']}\n\n"
        return formatted

    def clear_memory(self):
        self.history = []

    def is_follow_up(self, question: str) -> bool:
        if not self.history:
            return False

        follow_up_indicators = ["it", "that", "this", "the other one", "what you just said", "tell me more"]
        question_lower = question.lower()
        return any(indicator in question_lower for indicator in follow_up_indicators)
