import sys
from unittest.mock import MagicMock

# Mock onprem and other modules that might be missing or large
sys.modules['onprem'] = MagicMock()
sys.modules['langchain_openai'] = MagicMock()
sys.modules['langchain_chroma'] = MagicMock()
sys.modules['langchain_community'] = MagicMock()
sys.modules['langchain_core'] = MagicMock()
sys.modules['langchain_text_splitters'] = MagicMock()

import pytest
# We only run relevant tests
# tests/test_agent.py and tests/test_rag_logic.py might fail due to deep dependency on old architecture
# we should run tests/test_local_rag.py and tests/test_agent.py (if updated)
