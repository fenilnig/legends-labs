from collections import OrderedDict
import torch
import gc
from typing import Dict, Any

class EngineManager:
    """
    LRU Cache Manager for TTSEngines with VRAM Budgeting.
    Maintains a maximum of 2.5GB free VRAM buffer for external tools.
    """
    def __init__(self, engines: Dict[str, Any]):
        self.engines = engines
        # active_cache keeps track of loaded engines (name -> engine) in LRU order
        self.active_cache = OrderedDict()
        
        # 2.5GB in bytes
        self.min_free_vram = 2.5 * 1024 * 1024 * 1024 

    def _get_free_vram(self) -> int:
        if not torch.cuda.is_available():
            return float('inf') # Infinite free if CPU
            
        try:
            free, total = torch.cuda.mem_get_info()
            return free
        except Exception:
            return float('inf') # Fallback if error

    def _unload_oldest(self):
        if not self.active_cache:
            return False
            
        # Unload the least recently used engine (first item in OrderedDict)
        oldest_name, oldest_engine = self.active_cache.popitem(last=False)
        print(f"[LRU Cache] Unloading {oldest_name} to free VRAM...")
        try:
            oldest_engine.unload()
        except Exception as e:
            print(f"Error unloading {oldest_name}: {e}")
            
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
            
        return True

    def get_engine(self, name: str) -> Any:
        if name not in self.engines:
            return self.engines.get("Mock")
            
        engine = self.engines[name]
        
        # Mark as recently used
        if name in self.active_cache:
            self.active_cache.move_to_end(name)
        else:
            # We are about to load it. Check VRAM budget first.
            # (Note: we don't know the exact size of the model before loading, 
            # so we just ensure we have the minimum buffer right now. 
            # A more robust system would know the model size requirement).
            while self._get_free_vram() < self.min_free_vram:
                unloaded = self._unload_oldest()
                if not unloaded:
                    print("[Warning] Cannot free more VRAM, falling back to CPU load if possible.")
                    break
                    
            self.active_cache[name] = engine
            # The load happens inside the engine's generate() loop or here if preferred,
            # but our architecture currently calls load() asynchronously inside engine.generate().
            # So the actual memory footprint spikes during generate().
            # To be perfect, we should intercept and call unload here if needed.
            
        return engine
