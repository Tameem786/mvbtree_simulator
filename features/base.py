"""
Base implementation of Multiversion B-Tree simulator.

This module implements a simplified version of the GPU Multiversion B-Tree
from the PACT 2022 paper, designed to run on CPU for educational purposes.
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class BTreeNode:
    """Represents a node in the multiversion B-Tree."""
    keys: List[int]  # List of keys in this node
    values: List[int]  # List of values (for leaf nodes)
    children: List[Optional['BTreeNode']]  # Child pointers
    is_leaf: bool
    timestamp: int  # When this version was created
    next_version: Optional['BTreeNode']  # Pointer to older version
    
    def __init__(self, is_leaf: bool = True, timestamp: int = 0):
        self.keys = []
        self.values = []
        self.children = []
        self.is_leaf = is_leaf
        self.timestamp = timestamp
        self.next_version = None
    
    def get_version_at_timestamp(self, snapshot_timestamp: int) -> Optional['BTreeNode']:
        """
        Traverse version chain to find the node version valid at snapshot_timestamp.
        Returns the most recent version with timestamp <= snapshot_timestamp.
        """
        current = self
        best_version = None
        
        while current is not None:
            if current.timestamp <= snapshot_timestamp:
                if best_version is None or current.timestamp > best_version.timestamp:
                    best_version = current
            current = current.next_version
        
        return best_version if best_version is not None else self


class MultiversionBTree:
    """
    Simplified Multiversion B-Tree implementation.
    
    This is a basic implementation that demonstrates:
    - Versioning of nodes
    - Snapshot functionality
    - Insert and find operations
    """
    
    def __init__(self, branching_factor: int = 4):
        """
        Initialize an empty multiversion B-Tree.
        
        Args:
            branching_factor: Maximum number of children per node (default: 4 for simplicity)
        """
        self.branching_factor = branching_factor
        self.root: Optional[BTreeNode] = None
        self.global_timestamp = 0
        self.snapshots: dict[int, int] = {}  # snapshot_id -> timestamp mapping
    
    def take_snapshot(self) -> int:
        """
        Take a snapshot of the current state of the tree.
        
        Returns:
            snapshot_id: Unique identifier for this snapshot
        """
        snapshot_id = len(self.snapshots) + 1
        self.snapshots[snapshot_id] = self.global_timestamp
        return snapshot_id
    
    def _increment_timestamp(self) -> int:
        """Increment and return the global timestamp."""
        self.global_timestamp += 1
        return self.global_timestamp
    
    def _create_new_version(self, node: BTreeNode) -> BTreeNode:
        """
        Create a new version of a node (copy-on-write).
        
        Args:
            node: The node to version
            
        Returns:
            New node that is a copy of the original
        """
        new_node = BTreeNode(is_leaf=node.is_leaf, timestamp=self._increment_timestamp())
        new_node.keys = node.keys.copy()
        new_node.values = node.values.copy()
        new_node.children = node.children.copy()
        new_node.next_version = node  # Link to older version
        return new_node
    
    def insert(self, key: int, value: int, use_versioning: bool = True) -> bool:
        """
        Insert a key-value pair into the tree.
        
        Args:
            key: The key to insert
            value: The value associated with the key
            use_versioning: If True, create new versions (out-of-place). 
                          If False, modify in-place when possible.
        
        Returns:
            True if insertion was successful, False if key already exists
        """
        if self.root is None:
            self.root = BTreeNode(is_leaf=True, timestamp=self._increment_timestamp())
            self.root.keys.append(key)
            self.root.values.append(value)
            return True
        
        # For simplicity, we'll use versioning for all inserts
        # In a full implementation, we'd check if snapshot is active
        if use_versioning:
            self.root = self._insert_with_versioning(self.root, key, value)
        else:
            self.root = self._insert_in_place(self.root, key, value)
        
        return True
    
    def _insert_with_versioning(self, node: BTreeNode, key: int, value: int) -> BTreeNode:
        """
        Insert with versioning (out-of-place update).
        Creates a new version of nodes that are modified.
        """
        # Create a new version of this node
        new_node = self._create_new_version(node)
        
        if new_node.is_leaf:
            # Insert into leaf node
            if key in new_node.keys:
                # Key already exists, update value
                idx = new_node.keys.index(key)
                new_node.values[idx] = value
            else:
                # Insert new key-value pair in sorted order
                idx = 0
                while idx < len(new_node.keys) and new_node.keys[idx] < key:
                    idx += 1
                new_node.keys.insert(idx, key)
                new_node.values.insert(idx, value)
        else:
            # Internal node - find child to insert into
            child_idx = 0
            while child_idx < len(new_node.keys) and new_node.keys[child_idx] < key:
                child_idx += 1
            
            # Recursively insert into child
            if new_node.children[child_idx] is not None:
                new_node.children[child_idx] = self._insert_with_versioning(
                    new_node.children[child_idx], key, value
                )
        
        return new_node
    
    def _insert_in_place(self, node: BTreeNode, key: int, value: int) -> BTreeNode:
        """
        Insert without versioning (in-place update).
        Only used when no snapshots are active.
        """
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
        else:
            child_idx = 0
            while child_idx < len(node.keys) and node.keys[child_idx] < key:
                child_idx += 1
            
            if node.children[child_idx] is not None:
                node.children[child_idx] = self._insert_in_place(
                    node.children[child_idx], key, value
                )
        
        return node
    
    def find(self, key: int, snapshot_id: Optional[int] = None) -> Optional[int]:
        """
        Find a key in the tree.
        
        Args:
            key: The key to search for
            snapshot_id: Optional snapshot ID to query a specific version
            
        Returns:
            The value associated with the key, or None if not found
        """
        if self.root is None:
            return None
        
        # Get the timestamp for this query
        query_timestamp = self.global_timestamp
        if snapshot_id is not None and snapshot_id in self.snapshots:
            query_timestamp = self.snapshots[snapshot_id]
        
        return self._find_in_node(self.root, key, query_timestamp)
    
    def _find_in_node(self, node: BTreeNode, key: int, timestamp: int) -> Optional[int]:
        """
        Recursively search for a key in a node, using the appropriate version.
        """
        # Get the correct version of this node for the given timestamp
        versioned_node = node.get_version_at_timestamp(timestamp)
        
        if versioned_node.is_leaf:
            # Search in leaf node
            if key in versioned_node.keys:
                idx = versioned_node.keys.index(key)
                return versioned_node.values[idx]
            return None
        else:
            # Internal node - find child to search
            child_idx = 0
            while child_idx < len(versioned_node.keys) and versioned_node.keys[child_idx] < key:
                child_idx += 1
            
            # Search in appropriate child
            if child_idx < len(versioned_node.children) and versioned_node.children[child_idx] is not None:
                return self._find_in_node(versioned_node.children[child_idx], key, timestamp)
            return None
    
    def get_all_keys(self, snapshot_id: Optional[int] = None) -> List[int]:
        """
        Get all keys in the tree (for a specific snapshot if provided).
        
        Args:
            snapshot_id: Optional snapshot ID
            
        Returns:
            List of all keys in sorted order
        """
        if self.root is None:
            return []
        
        query_timestamp = self.global_timestamp
        if snapshot_id is not None and snapshot_id in self.snapshots:
            query_timestamp = self.snapshots[snapshot_id]
        
        keys = []
        self._collect_keys(self.root, keys, query_timestamp)
        return sorted(keys)
    
    def _collect_keys(self, node: BTreeNode, keys: List[int], timestamp: int):
        """Recursively collect all keys from the tree."""
        versioned_node = node.get_version_at_timestamp(timestamp)
        
        if versioned_node.is_leaf:
            keys.extend(versioned_node.keys)
        else:
            for i, child in enumerate(versioned_node.children):
                if child is not None:
                    self._collect_keys(child, keys, timestamp)
                if i < len(versioned_node.keys):
                    keys.append(versioned_node.keys[i])
    
    def print_tree(self, snapshot_id: Optional[int] = None, indent: str = ""):
        """
        Print the tree structure (for debugging/visualization).
        
        Args:
            snapshot_id: Optional snapshot ID to print a specific version
            indent: Indentation string for recursive printing
        """
        if self.root is None:
            print("(empty tree)")
            return
        
        query_timestamp = self.global_timestamp
        if snapshot_id is not None and snapshot_id in self.snapshots:
            query_timestamp = self.snapshots[snapshot_id]
        
        self._print_node(self.root, query_timestamp, indent)
    
    def erase(self, key: int, use_versioning: bool = True) -> bool:
        """
        Erase (delete) a key from the tree.
        
        Args:
            key: The key to erase
            use_versioning: If True, create new versions (out-of-place). 
                          If False, modify in-place when possible.
        
        Returns:
            True if key was found and erased, False if key not found
        """
        if self.root is None:
            return False
        
        if use_versioning:
            result = self._erase_with_versioning(self.root, key)
            if result[0]:  # Key was found
                self.root = result[1] if result[1] is not None else self.root
            return result[0]
        else:
            return self._erase_in_place(self.root, key)
    
    def _erase_with_versioning(self, node: BTreeNode, key: int) -> Tuple[bool, Optional[BTreeNode]]:
        """
        Erase with versioning (out-of-place update).
        Returns (found, new_node_or_none)
        """
        if node is None:
            return (False, None)
        
        # Create a new version of this node
        new_node = self._create_new_version(node)
        
        if new_node.is_leaf:
            # Erase from leaf node
            if key in new_node.keys:
                idx = new_node.keys.index(key)
                new_node.keys.pop(idx)
                new_node.values.pop(idx)
                return (True, new_node)
            return (False, new_node)
        else:
            # Internal node - find child to erase from
            child_idx = 0
            while child_idx < len(new_node.keys) and new_node.keys[child_idx] < key:
                child_idx += 1
            
            # Recursively erase from child
            if child_idx < len(new_node.children) and new_node.children[child_idx] is not None:
                found, updated_child = self._erase_with_versioning(new_node.children[child_idx], key)
                if found:
                    new_node.children[child_idx] = updated_child
                return (found, new_node)
            return (False, new_node)
    
    def _erase_in_place(self, node: BTreeNode, key: int) -> bool:
        """Erase without versioning (in-place update)."""
        if node is None:
            return False
        
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
                return self._erase_in_place(node.children[child_idx], key)
            return False
    
    def range_query(self, lower_bound: int, upper_bound: int, snapshot_id: Optional[int] = None) -> List[Tuple[int, int]]:
        """
        Perform a range query to find all keys in [lower_bound, upper_bound).
        
        Args:
            lower_bound: Lower bound (inclusive)
            upper_bound: Upper bound (exclusive)
            snapshot_id: Optional snapshot ID to query a specific version
            
        Returns:
            List of (key, value) tuples in the range
        """
        if self.root is None:
            return []
        
        query_timestamp = self.global_timestamp
        if snapshot_id is not None and snapshot_id in self.snapshots:
            query_timestamp = self.snapshots[snapshot_id]
        
        results = []
        self._range_query_in_node(self.root, lower_bound, upper_bound, query_timestamp, results)
        return sorted(results, key=lambda x: x[0])  # Sort by key
    
    def _range_query_in_node(self, node: BTreeNode, lower_bound: int, upper_bound: int, 
                             timestamp: int, results: List[Tuple[int, int]]):
        """Recursively perform range query in a node."""
        if node is None:
            return
        
        versioned_node = node.get_version_at_timestamp(timestamp)
        
        if versioned_node.is_leaf:
            # Search in leaf node
            for i, key in enumerate(versioned_node.keys):
                if lower_bound <= key < upper_bound:
                    results.append((key, versioned_node.values[i]))
        else:
            # Internal node - traverse children
            for i, child in enumerate(versioned_node.children):
                if child is not None:
                    # Check if we need to traverse this child
                    should_traverse = True
                    if i < len(versioned_node.keys):
                        # Child is before key[i], traverse if lower_bound <= key[i]
                        if versioned_node.keys[i] < lower_bound:
                            should_traverse = False
                    if i > 0:
                        # Child is after key[i-1], traverse if key[i-1] < upper_bound
                        if versioned_node.keys[i-1] >= upper_bound:
                            should_traverse = False
                    
                    if should_traverse:
                        self._range_query_in_node(child, lower_bound, upper_bound, timestamp, results)
                    
                    # Check if key at position i is in range
                    if i < len(versioned_node.keys):
                        key = versioned_node.keys[i]
                        if lower_bound <= key < upper_bound:
                            # For internal nodes, we don't store values, so skip
                            pass
    
    def _print_node(self, node: BTreeNode, timestamp: int, indent: str):
        """Recursively print a node and its children."""
        versioned_node = node.get_version_at_timestamp(timestamp)
        
        if versioned_node.is_leaf:
            print(f"{indent}Leaf[ts={versioned_node.timestamp}]: keys={versioned_node.keys}, values={versioned_node.values}")
        else:
            print(f"{indent}Internal[ts={versioned_node.timestamp}]: keys={versioned_node.keys}")
            for i, child in enumerate(versioned_node.children):
                if child is not None:
                    self._print_node(child, timestamp, indent + "  ")

