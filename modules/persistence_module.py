import json
import os
from datetime import datetime
from typing import Dict, Any

class PersistenceModule:
    """Handles saving/loading agent state to/from disk."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Create data directory if it doesn't exist."""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Save current state atomically to JSON."""
        try:
            # Write to temp file first, then rename (atomic)
            temp_path = f"{self.filepath}.tmp"
            state['last_saved'] = datetime.now().isoformat()
            
            with open(temp_path, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            
            os.replace(temp_path, self.filepath)
            return True
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False
    
    def load_state(self) -> Dict[str, Any]:
        """Load state from disk, or return default if not exists."""
        if not os.path.exists(self.filepath):
            return self._default_state()
        
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Load failed, using defaults: {e}")
            return self._default_state()
    
    def _default_state(self) -> Dict[str, Any]:
        """Return fresh state for new agent."""
        from config import INITIAL_CASH
        return {
            'cash': INITIAL_CASH,
            'holdings': {},  # {symbol: {quantity, avg_price}}
            'trades': [],    # List of trade dicts
            'status': 'stopped',  # stopped / running / paused
            'last_prices': {},
            'indicators': {},
            'created_at': datetime.now().isoformat()
        }