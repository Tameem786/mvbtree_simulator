"""
Educational content and explanations for the Multiversion B-Tree simulator.

This module provides educational explanations of the paper's concepts.
"""

EDUCATION_CONTENT = {
    "versioning": {
        "title": "Node Versioning",
        "concept": """
        **What is Versioning?**
        
        In a multiversion B-Tree, each node can have multiple versions. This allows the tree to maintain
        historical states while still allowing updates.
        
        **How it Works:**
        1. When a node needs to be modified and a snapshot exists, a NEW version is created
        2. The new version is a copy of the original node with modifications
        3. Versions are linked in a chain: newest → older → older → ...
        4. Each version has a timestamp indicating when it was created
        
        **Why it Matters:**
        - Allows queries to see historical states (via snapshots)
        - Enables linearizable concurrent operations
        - Preserves data integrity during concurrent updates
        """,
        "paper_reference": """
        **From the Paper:**
        "Each tree node is represented as a version list. The most recent version is the head of the list.
        Any pointer in the B-Tree structure only points to the head node of a version list."
        """
    },
    
    "snapshots": {
        "title": "Snapshots",
        "concept": """
        **What is a Snapshot?**
        
        A snapshot is a read-only view of the tree at a specific point in time. It allows you to
        query the tree as it existed when the snapshot was taken.
        
        **How it Works:**
        1. `take_snapshot()` atomically increments the global timestamp
        2. This timestamp is stored as the snapshot ID
        3. When querying with a snapshot ID, the tree traverses version chains
        4. For each node, it finds the version with timestamp ≤ snapshot timestamp
        5. This gives you a consistent view of the tree at that moment
        
        **Why it Matters:**
        - Enables historical queries
        - Provides linearizability for concurrent operations
        - Allows time-travel queries
        """,
        "paper_reference": """
        **From the Paper:**
        "A snapshot is a read-only version of a data structure that contains all key-value pairs
        stored when a take_snapshot operation is performed. The paper achieves linearizable multipoint
        queries by taking a snapshot and then performing queries on that fixed snapshot."
        """
    },
    
    "in_place": {
        "title": "In-Place Updates (ViB-Tree)",
        "concept": """
        **What is In-Place Update?**
        
        In-place updates directly modify the existing node without creating a new version.
        This is more efficient but only works when no snapshots are active.
        
        **How it Works:**
        1. Check if snapshot is active (global timestamp matches node timestamp)
        2. If safe, directly modify the node
        3. Only one write operation needed
        4. More efficient but doesn't preserve history
        
        **When to Use:**
        - When no snapshots are active
        - When you don't need historical queries
        - For better performance
        """,
        "paper_reference": """
        **From the Paper:**
        "In-place update (ViB-Tree) mutates the tree node directly (one write). Only possible when
        a take_snapshot is not running concurrently, and the current global timestamp matches the
        modified node's timestamp."
        """
    },
    
    "out_of_place": {
        "title": "Out-of-Place Updates (VoB-Tree)",
        "concept": """
        **What is Out-of-Place Update?**
        
        Out-of-place updates use Copy-on-Write (COW) strategy. When a node needs modification,
        a new version is created, modified, and linked to the old version.
        
        **How it Works:**
        1. Create a copy of the node to be modified
        2. Modify the copy (add/remove keys)
        3. Link the new version to the old version (version chain)
        4. Update pointer to point to new version
        5. Two write operations: copy + modify
        
        **When to Use:**
        - When snapshots may be active
        - When you need historical queries
        - For concurrent operations
        """,
        "paper_reference": """
        **From the Paper:**
        "Out-of-place update (VoB-Tree) uses Copy-on-Write (COW); creates a copy of the node,
        modifies the copy, and updates the pointer to the copy (two writes). Required when the
        take_snapshot operation may execute concurrently with updates or queries."
        """
    },
    
    "linearizability": {
        "title": "Linearizability",
        "concept": """
        **What is Linearizability?**
        
        Linearizability ensures that concurrent operations appear to execute atomically at some
        point between their invocation and response. This provides an intuitive understanding of
        concurrent operations.
        
        **How Multiversion B-Tree Achieves It:**
        1. Snapshots provide a consistent view of the tree
        2. All queries on a snapshot see the same state
        3. No mixing of old and new states
        4. Operations appear to execute in some sequential order
        
        **Example:**
        - Thread 1: Takes snapshot, then queries
        - Thread 2: Inserts new keys
        - Thread 1's queries will NOT see Thread 2's insertions
        - This is correct behavior - the snapshot preserves the state
        """,
        "paper_reference": """
        **From the Paper:**
        "Linearizability ensures that the effect of a data structure operation must appear to take
        effect atomically at a specific point—called the linearization point—between the operation's
        invocation and response."
        """
    },
    
    "version_chain": {
        "title": "Version Chain Traversal",
        "concept": """
        **What is Version Chain Traversal?**
        
        When querying with a snapshot, the tree must find the correct version of each node.
        This is done by traversing the version chain.
        
        **How it Works:**
        1. Start at the head (newest version) of a node
        2. Traverse the version chain (newest → older)
        3. Find the version with timestamp ≤ snapshot timestamp
        4. Use that version for the query
        5. Continue traversal with that version
        
        **Example:**
        - Node has versions: [ts=5] → [ts=3] → [ts=1]
        - Query snapshot with timestamp=4
        - Traverse: ts=5 (too new) → ts=3 (valid!) → use this version
        """,
        "paper_reference": """
        **From the Paper:**
        "When a query starts, it traverses the tree. Each time a node is loaded, the query attempts
        to initialize its timestamp, traverses side-links, and then traverses the version list.
        The traversal stops when it finds a node whose timestamp is at most the query's timestamp."
        """
    }
}


def get_operation_explanation(operation: str, details: dict) -> str:
    """Generate step-by-step explanation for an operation."""
    explanations = {
        "Insert": """
        **Step-by-Step Insert Operation:**
        
        1. **Find the leaf node** where the key should be inserted
        2. **Check if versioning is needed:**
           - If versioning enabled → Create new version (out-of-place)
           - If versioning disabled → Modify directly (in-place)
        3. **Insert key-value pair** in sorted order
        4. **Update timestamp** if creating new version
        5. **Link versions** if using versioning
        
        **What Happens:**
        - New version created (if versioning enabled)
        - Global timestamp incremented
        - Version chain updated
        """,
        
        "Find": """
        **Step-by-Step Find Operation:**
        
        1. **Determine query timestamp:**
           - If snapshot ID provided → use snapshot timestamp
           - Otherwise → use current global timestamp
        2. **Start at root node**
        3. **For each node:**
           - Get correct version for query timestamp
           - Traverse version chain if needed
           - Compare key with node keys
        4. **Navigate to child** (if internal node) or **return value** (if leaf)
        5. **Continue recursively** until found or not found
        
        **What Happens:**
        - Version chain traversal for each node
        - Consistent view based on snapshot
        """,
        
        "Snapshot": """
        **Step-by-Step Snapshot Operation:**
        
        1. **Atomically increment** global timestamp
        2. **Store snapshot ID** → timestamp mapping
        3. **Return snapshot ID** to caller
        
        **What Happens:**
        - Global timestamp increases
        - New snapshot ID created
        - Future queries can use this snapshot
        
        **Important:**
        - Snapshots are lightweight (just a timestamp)
        - No copying of tree structure
        - Versions are created lazily when needed
        """,
        
        "Erase": """
        **Step-by-Step Erase Operation:**
        
        1. **Find the leaf node** containing the key
        2. **Check if versioning is needed:**
           - If versioning enabled → Create new version (out-of-place)
           - If versioning disabled → Modify directly (in-place)
        3. **Remove key-value pair** from the node
        4. **Update timestamp** if creating new version
        5. **Link versions** if using versioning
        
        **What Happens:**
        - Key is removed from the tree
        - New version created (if versioning enabled)
        - Historical queries can still see the key in old snapshots
        """,
        
        "Range Query": """
        **Step-by-Step Range Query Operation:**
        
        1. **Determine query timestamp:**
           - If snapshot ID provided → use snapshot timestamp
           - Otherwise → use current global timestamp
        2. **Start at root node**
        3. **For each node:**
           - Get correct version for query timestamp
           - Traverse version chain if needed
           - Check if range overlaps with node's keys
        4. **Navigate to children** that might contain keys in range
        5. **Collect all keys** in [lower_bound, upper_bound)
        6. **Return sorted results**
        
        **What Happens:**
        - All keys in the range are found
        - Results are consistent with the snapshot (if specified)
        - This is a **linearizable multipoint query** - all results from the same point in time
        """
    }
    
    return explanations.get(operation, "Operation explanation not available.")


def explain_version_chain(node: 'BTreeNode', snapshot_timestamp: int) -> str:
    """Explain how version chain traversal works for a specific node."""
    if node is None:
        return "Node is None."
    
    versions = []
    current = node
    while current is not None:
        versions.append({
            'timestamp': current.timestamp,
            'valid': current.timestamp <= snapshot_timestamp
        })
        current = current.next_version
    
    explanation = f"**Version Chain for Node:**\n\n"
    explanation += f"Query timestamp: {snapshot_timestamp}\n\n"
    
    for i, v in enumerate(versions):
        marker = "✓" if v['valid'] else "✗"
        explanation += f"{marker} Version {i+1}: timestamp={v['timestamp']}"
        if v['valid']:
            explanation += " ← **This version will be used**"
        explanation += "\n"
    
    return explanation

