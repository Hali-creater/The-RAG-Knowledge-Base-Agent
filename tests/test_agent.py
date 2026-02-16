import unittest
import os
from src.memory_manager import MemoryManager
from src.text_splitter import TextSplitter
from src.utils import allowed_file

class TestRAGComponents(unittest.TestCase):
    def test_memory_manager(self):
        memory = MemoryManager(max_history=2)
        memory.add_exchange("Hi", "Hello")
        memory.add_exchange("How are you?", "I am fine")
        memory.add_exchange("Extra", "Pop")

        history = memory.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['question'], "How are you?")
        self.assertEqual(history[1]['question'], "Extra")

    def test_memory_follow_up(self):
        memory = MemoryManager()
        memory.add_exchange("Tell me about apples", "Apples are red")
        self.assertTrue(memory.is_follow_up("What color is it?"))
        self.assertFalse(memory.is_follow_up("What is the weather?"))

    def test_allowed_file(self):
        self.assertTrue(allowed_file("test.pdf"))
        self.assertTrue(allowed_file("test.docx"))
        self.assertTrue(allowed_file("test.txt"))
        self.assertTrue(allowed_file("test.md"))
        self.assertFalse(allowed_file("test.exe"))
        self.assertFalse(allowed_file("test.jpg"))

    def test_text_splitter(self):
        splitter = TextSplitter(chunk_size=100, chunk_overlap=10)
        from langchain_core.documents import Document
        docs = [Document(page_content="A" * 500)]
        chunks = splitter.split_documents(docs)
        self.assertGreater(len(chunks), 1)

if __name__ == '__main__':
    unittest.main()
