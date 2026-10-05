import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from legends_labs.core.constants import DATA_DIR

@dataclass
class PipelineNode:
    id: str
    operation: str
    params: Dict[str, Any]
    input_hash: str
    output_cache_path: Optional[str] = None
    is_dirty: bool = False

class ProcessingPipeline:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.nodes: List[PipelineNode] = []
        self.cache_dir = DATA_DIR / "cache" / project_id
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._operations: Dict[str, Callable] = {}
        
    def register_operation(self, name: str, func: Callable):
        self._operations[name] = func
        
    def add_node(self, operation: str, params: Dict[str, Any]):
        node_id = f"node_{len(self.nodes)}"
        input_hash = self._get_last_output_hash()
        
        node = PipelineNode(
            id=node_id,
            operation=operation,
            params=params,
            input_hash=input_hash,
            is_dirty=True
        )
        self.nodes.append(node)
        return node
        
    def modify_node(self, node_id: str, new_params: Dict[str, Any]):
        """Update a node's params and mark it + everything downstream as dirty."""
        idx = next((i for i, n in enumerate(self.nodes) if n.id == node_id), -1)
        if idx == -1: return
        
        self.nodes[idx].params = new_params
        for i in range(idx, len(self.nodes)):
            self.nodes[i].is_dirty = True
            
    def _get_last_output_hash(self) -> str:
        if not self.nodes: return "ROOT"
        last_node = self.nodes[-1]
        if last_node.output_cache_path:
            return hashlib.sha256(last_node.output_cache_path.encode()).hexdigest()
        return f"DIRTY_{last_node.id}"

    def execute(self, initial_audio_path: str):
        """Run the pipeline. Only processes dirty nodes."""
        current_audio = initial_audio_path
        
        for node in self.nodes:
            if not node.is_dirty and node.output_cache_path:
                # Use cached result
                current_audio = node.output_cache_path
                continue
                
            # Node is dirty, run it
            if node.operation not in self._operations:
                raise ValueError(f"Unknown operation: {node.operation}")
                
            func = self._operations[node.operation]
            
            # Generate a cache path based on inputs
            cache_name = f"{node.id}_{hashlib.sha256(json.dumps(node.params, sort_keys=True).encode()).hexdigest()}.wav"
            output_path = str(self.cache_dir / cache_name)
            
            logger.info("[Pipeline] Running {} -> {}", node.operation, output_path)
            
            # Run the effect
            try:
                current_audio = func(current_audio, output_path, **node.params)
            except Exception:
                logger.exception(
                    "Pipeline node {} ({}) failed", node.id, node.operation
                )
                raise
            
            # Update node
            node.output_cache_path = current_audio
            node.is_dirty = False
            
        return current_audio
