import json
import time
from collections import deque
from typing import Dict, List, Any

class MemorySystem:
    def __init__(self, max_short_term=100, max_long_term=1000):
        self.short_term_memory = deque(maxlen=max_short_term)
        self.long_term_memory = []
        self.max_long_term = max_long_term
        self.knowledge_base = {}
        
    def add_experience(self, experience: Dict[str, Any]):
        experience['timestamp'] = time.time()
        self.short_term_memory.append(experience)
        
        # Move important experiences to long-term memory
        if self._is_important(experience):
            self._consolidate_to_long_term(experience)
    
    def _is_important(self, experience: Dict[str, Any]) -> bool:
        # Simple importance scoring
        importance_keywords = ['error', 'success', 'learn', 'remember', 'important']
        text = str(experience.get('content', '')).lower()
        return any(keyword in text for keyword in importance_keywords)
    
    def _consolidate_to_long_term(self, experience: Dict[str, Any]):
        if len(self.long_term_memory) >= self.max_long_term:
            self.long_term_memory.pop(0)
        self.long_term_memory.append(experience)
    
    def recall(self, query: str, memory_type='both') -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()
        
        if memory_type in ['short', 'both']:
            for memory in self.short_term_memory:
                if query_lower in str(memory.get('content', '')).lower():
                    results.append(memory)
        
        if memory_type in ['long', 'both']:
            for memory in self.long_term_memory:
                if query_lower in str(memory.get('content', '')).lower():
                    results.append(memory)
        
        return results
    
    def learn_fact(self, key: str, value: Any):
        self.knowledge_base[key] = value
    
    def get_knowledge(self, key: str) -> Any:
        return self.knowledge_base.get(key)
    
    def save_memory(self, filepath: str):
        memory_data = {
            'short_term': list(self.short_term_memory),
            'long_term': self.long_term_memory,
            'knowledge_base': self.knowledge_base
        }
        with open(filepath, 'w') as f:
            json.dump(memory_data, f, indent=2)
    
    def load_memory(self, filepath: str):
        try:
            with open(filepath, 'r') as f:
                memory_data = json.load(f)
            
            self.short_term_memory = deque(memory_data.get('short_term', []), 
                                         maxlen=self.short_term_memory.maxlen)
            self.long_term_memory = memory_data.get('long_term', [])
            self.knowledge_base = memory_data.get('knowledge_base', {})
        except FileNotFoundError:
            print("No existing memory file found. Starting fresh.")