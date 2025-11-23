"""
Regular B-Tree implementation for comparison with Multiversion B-Tree.

This is a simple B-Tree without versioning, used to demonstrate the advantages
of the multiversion approach from the paper.
"""

from typing import Optional, List
from dataclasses import dataclass


@dataclass
class RegularBTreeNode:
    """Represents a node in a regular B-Tree (no versioning)."""
    keys: List[int]
    values: List[int]
    children: List[Optional['RegularBTreeNode']]
    is_leaf: bool
    
    def __init__(self, is_leaf: bool = True):
        self.keys = []
        self.values = []
        self.children = []
        self.is_leaf = is_leaf


class RegularBTree:
    """
    Regular B-Tree without versioning.
    
    This is used for comparison to show why the multiversion B-Tree is better.
    """
    
    def __init__(self, branching_factor: int = 4):
        self.branching_factor = branching_factor
        self.root: Optional[RegularBTreeNode] = None
        self.operation_count = 0
    
    def insert(self, key: int, value: int) -> bool:
        """Insert a key-value pair (in-place only, no versioning)."""
        self.operation_count += 1
        if self.root is None:
            self.root = RegularBTreeNode(is_leaf=True)
            self.root.keys.append(key)
            self.root.values.append(value)
            return True
        
        return self._insert(self.root, key, value)
    
    def _insert(self, node: RegularBTreeNode, key: int, value: int) -> bool:
        """Recursive insert."""
        if node.is_leaf:
            if key in node.keys:
                idx = node.keys.index(key)
                node.values[idx] = value
            else:
                idx = 0
                while idx < len(node.keys) and node.keys[idx] < key:
                    idx += 1
                node.keys.insert(idx, key)
                node.values.insert(idx, value)
            return True
        else:
            child_idx = 0
            while child_idx < len(node.keys) and node.keys[child_idx] < key:
                child_idx += 1
            
            if child_idx < len(node.children) and node.children[child_idx] is not None:
                return self._insert(node.children[child_idx], key, value)
            return False
    
    def erase(self, key: int) -> bool:
        """Erase a key (in-place only, no versioning)."""
        self.operation_count += 1
        if self.root is None:
            return False
        return self._erase(self.root, key)
    
    def _erase(self, node: RegularBTreeNode, key: int) -> bool:
        """Recursive erase."""
        if node.is_leaf:
            if key in node.keys:
                idx = node.keys.index(key)
                node.keys.pop(idx)
                node.values.pop(idx)
                return True
            return False
        else:
            child_idx = 0
            while child_idx < len(node.keys) and node.keys[child_idx] < key:
                child_idx += 1
            
            if child_idx < len(node.children) and node.children[child_idx] is not None:
                return self._erase(node.children[child_idx], key)
            return False
    
    def find(self, key: int) -> Optional[int]:
        """Find a key (only current state, no snapshots)."""
        self.operation_count += 1
        if self.root is None:
            return None
        return self._find(self.root, key)
    
    def _find(self, node: RegularBTreeNode, key: int) -> Optional[int]:
        """Recursive find."""
        if node.is_leaf:
            if key in node.keys:
                idx = node.keys.index(key)
                return node.values[idx]
            return None
        else:
            child_idx = 0
            while child_idx < len(node.keys) and node.keys[child_idx] < key:
                child_idx += 1
            
            if child_idx < len(node.children) and node.children[child_idx] is not None:
                return self._find(node.children[child_idx], key)
            return None
    
    def get_all_keys(self) -> List[int]:
        """Get all keys (only current state)."""
        if self.root is None:
            return []
        keys = []
        self._collect_keys(self.root, keys)
        return sorted(keys)
    
    def _collect_keys(self, node: RegularBTreeNode, keys: List[int]):
        """Recursively collect keys."""
        if node.is_leaf:
            keys.extend(node.keys)
        else:
            for i, child in enumerate(node.children):
                if child is not None:
                    self._collect_keys(child, keys)
                if i < len(node.keys):
                    keys.append(node.keys[i])
    
    def get_stats(self) -> dict:
        """Get statistics about the tree."""
        if self.root is None:
            return {
                'total_nodes': 0,
                'total_keys': 0,
                'tree_height': 0,
                'operation_count': self.operation_count
            }
        
        total_nodes = 0
        total_keys = 0
        height = 0
        
        def traverse(node: RegularBTreeNode, depth: int):
            nonlocal total_nodes, total_keys, height
            if node is None:
                return
            
            height = max(height, depth)
            total_nodes += 1
            
            if node.is_leaf:
                total_keys += len(node.keys)
            else:
                for child in node.children:
                    if child is not None:
                        traverse(child, depth + 1)
        
        traverse(self.root, 0)
        
        return {
            'total_nodes': total_nodes,
            'total_keys': total_keys,
            'tree_height': height,
            'operation_count': self.operation_count
        }
    
    def visualize_tree_text(self) -> str:
        """Create text representation."""
        if self.root is None:
            return "(empty tree)"
        
        lines = []
        
        def traverse(node: RegularBTreeNode, prefix: str, is_last: bool):
            if node is None:
                return
            
            connector = "└── " if is_last else "├── "
            node_type = "Leaf" if node.is_leaf else "Internal"
            keys_str = ", ".join(map(str, node.keys))
            
            lines.append(f"{prefix}{connector}{node_type}: [{keys_str}]")
            
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            if not node.is_leaf:
                children = [c for c in node.children if c is not None]
                for i, child in enumerate(children):
                    traverse(child, new_prefix, i == len(children) - 1)
        
        traverse(self.root, "", True)
        return "\n".join(lines)

