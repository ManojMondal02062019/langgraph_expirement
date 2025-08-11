from langgraph.config import get_store
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
store.put(  
    ("users",),  
    "user_123",  
    {
        "name": "John Smith",
        "language": "English",
    } 
)
