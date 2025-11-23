#!/usr/bin/env python3
"""
Streamlit Web Application for Multiversion B-Tree Simulator

This is the main simulation software that demonstrates the GPU Multiversion B-Tree
from the PACT 2022 paper in an interactive web interface.
"""

import streamlit as st
import sys
import os
from typing import List, Tuple, Optional
from collections import deque

# Add features to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features.base import MultiversionBTree, BTreeNode
from features.education import EDUCATION_CONTENT, get_operation_explanation, explain_version_chain
from features.regular_btree import RegularBTree

# Page configuration
st.set_page_config(
    page_title="Multiversion B-Tree Simulator",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .operation-success {
        color: #28a745;
        font-weight: bold;
    }
    .operation-error {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'tree' not in st.session_state:
        st.session_state.tree = MultiversionBTree(branching_factor=4)
    if 'regular_tree' not in st.session_state:
        st.session_state.regular_tree = RegularBTree(branching_factor=4)
    if 'operation_history' not in st.session_state:
        st.session_state.operation_history = []
    if 'selected_snapshot' not in st.session_state:
        st.session_state.selected_snapshot = None
    if 'education_mode' not in st.session_state:
        st.session_state.education_mode = True
    if 'last_operation' not in st.session_state:
        st.session_state.last_operation = None
    if 'comparison_mode' not in st.session_state:
        st.session_state.comparison_mode = False


def add_to_history(operation: str, details: str):
    """Add operation to history."""
    st.session_state.operation_history.append({
        'operation': operation,
        'details': details,
        'timestamp': st.session_state.tree.global_timestamp
    })


def get_tree_stats(tree: MultiversionBTree, snapshot_id: Optional[int] = None) -> dict:
    """Get statistics about the tree."""
    if tree.root is None:
        return {
            'total_nodes': 0,
            'total_versions': 0,
            'max_version_chain': 0,
            'total_keys': 0,
            'tree_height': 0
        }
    
    query_timestamp = tree.global_timestamp
    if snapshot_id is not None and snapshot_id in tree.snapshots:
        query_timestamp = tree.snapshots[snapshot_id]
    
    total_nodes = 0
    total_versions = 0
    max_chain = 0
    total_keys = 0
    height = 0
    
    def traverse(node: BTreeNode, depth: int, timestamp: int):
        nonlocal total_nodes, total_versions, max_chain, total_keys, height
        if node is None:
            return
        
        height = max(height, depth)
        versioned_node = node.get_version_at_timestamp(timestamp)
        
        # Count versions in chain
        chain_length = 0
        current = node
        while current is not None:
            chain_length += 1
            if current.timestamp <= timestamp:
                total_versions += 1
            current = current.next_version
        
        max_chain = max(max_chain, chain_length)
        total_nodes += 1
        
        if versioned_node.is_leaf:
            total_keys += len(versioned_node.keys)
        else:
            for child in versioned_node.children:
                if child is not None:
                    traverse(child, depth + 1, timestamp)
    
    traverse(tree.root, 0, query_timestamp)
    
    return {
        'total_nodes': total_nodes,
        'total_versions': total_versions,
        'max_version_chain': max_chain,
        'total_keys': total_keys,
        'tree_height': height
    }


def visualize_tree_text(tree: MultiversionBTree, snapshot_id: Optional[int] = None) -> str:
    """Create a text representation of the tree."""
    if tree.root is None:
        return "(empty tree)"
    
    query_timestamp = tree.global_timestamp
    if snapshot_id is not None and snapshot_id in tree.snapshots:
        query_timestamp = tree.snapshots[snapshot_id]
    
    lines = []
    
    def traverse(node: BTreeNode, prefix: str, is_last: bool, timestamp: int):
        if node is None:
            return
        
        versioned_node = node.get_version_at_timestamp(timestamp)
        connector = "└── " if is_last else "├── "
        
        # Count versions
        version_count = 0
        current = node
        while current is not None:
            if current.timestamp <= timestamp:
                version_count += 1
            current = current.next_version
        
        node_type = "Leaf" if versioned_node.is_leaf else "Internal"
        keys_str = ", ".join(map(str, versioned_node.keys))
        version_info = f" [v{version_count}, ts={versioned_node.timestamp}]"
        
        lines.append(f"{prefix}{connector}{node_type}: [{keys_str}]{version_info}")
        
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        if not versioned_node.is_leaf:
            children = [c for c in versioned_node.children if c is not None]
            for i, child in enumerate(children):
                traverse(child, new_prefix, i == len(children) - 1, timestamp)
    
    traverse(tree.root, "", True, query_timestamp)
    return "\n".join(lines)


def get_version_chain_info(node: BTreeNode, max_timestamp: int) -> List[dict]:
    """Get information about version chain for a node."""
    versions = []
    current = node
    while current is not None:
        if current.timestamp <= max_timestamp:
            versions.append({
                'timestamp': current.timestamp,
                'keys': current.keys.copy(),
                'is_leaf': current.is_leaf
            })
        current = current.next_version
    return versions


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🌳 Multiversion B-Tree Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Simulating the GPU Multiversion B-Tree from PACT 2022</div>', unsafe_allow_html=True)
    
    # Mode Toggles
    col_mode1, col_mode2 = st.columns(2)
    with col_mode1:
        education_mode = st.checkbox("📚 Education Mode", value=st.session_state.education_mode, 
                                     help="Show step-by-step explanations and paper concepts")
        st.session_state.education_mode = education_mode
    with col_mode2:
        comparison_mode = st.checkbox("⚖️ Comparison Mode", value=st.session_state.comparison_mode,
                                      help="Compare Multiversion B-Tree vs Regular B-Tree")
        st.session_state.comparison_mode = comparison_mode
    
    tree = st.session_state.tree
    regular_tree = st.session_state.regular_tree
    
    # Educational Concepts Panel (if education mode is on)
    if education_mode:
        st.info("🎓 **Education Mode Active**: You'll see detailed explanations of how the paper's concepts work!")
        
        # Concept selector
        selected_concept = st.selectbox(
            "📖 Learn About:",
            options=list(EDUCATION_CONTENT.keys()),
            format_func=lambda x: EDUCATION_CONTENT[x]['title'],
            key="concept_selector"
        )
        
        with st.expander(f"📚 {EDUCATION_CONTENT[selected_concept]['title']}", expanded=True):
            st.markdown(EDUCATION_CONTENT[selected_concept]['concept'])
            st.markdown("---")
            st.markdown("**From the Paper:**")
            st.markdown(EDUCATION_CONTENT[selected_concept]['paper_reference'])
        
        st.divider()
    
    # Sidebar - Operations
    with st.sidebar:
        st.header("🔧 Operations")
        
        # Insert operation
        st.subheader("Insert / Update")
        st.caption("💡 Note: Inserting an existing key updates its value (this is how 'update' works)")
        with st.form("insert_form"):
            insert_key = st.number_input("Key", min_value=1, value=10, step=1, key="insert_key")
            insert_value = st.number_input("Value", min_value=0, value=100, step=1, key="insert_value")
            use_versioning = st.checkbox("Use Versioning (Out-of-place)", value=True, 
                                         help="Uncheck for in-place updates (ViB-Tree)")
            insert_submitted = st.form_submit_button("Insert/Update", use_container_width=True)
        
        if insert_submitted:
            if tree.insert(insert_key, insert_value, use_versioning=use_versioning):
                add_to_history("Insert", f"key={insert_key}, value={insert_value}, versioning={use_versioning}")
                st.success(f"✓ Inserted key={insert_key}, value={insert_value}")
                st.session_state.last_operation = {
                    'type': 'Insert',
                    'key': insert_key,
                    'value': insert_value,
                    'versioning': use_versioning
                }
                # Also insert into regular tree for comparison
                if comparison_mode:
                    regular_tree.insert(insert_key, insert_value)
            else:
                st.error(f"✗ Failed to insert key={insert_key}")
        
        st.divider()
        
        # Find operation
        st.subheader("Find")
        with st.form("find_form"):
            find_key = st.number_input("Key", min_value=1, value=10, step=1, key="find_key")
            find_snapshot = st.selectbox(
                "Snapshot (optional)",
                options=[None] + list(tree.snapshots.keys()),
                format_func=lambda x: "Current" if x is None else f"Snapshot #{x}",
                key="find_snapshot"
            )
            find_submitted = st.form_submit_button("Find", use_container_width=True)
        
        if find_submitted:
            value = tree.find(find_key, snapshot_id=find_snapshot)
            if value is not None:
                snapshot_info = f" in snapshot #{find_snapshot}" if find_snapshot else ""
                st.success(f"✓ Found key={find_key}, value={value}{snapshot_info}")
                add_to_history("Find", f"key={find_key}, snapshot={find_snapshot}, result={value}")
                st.session_state.last_operation = {
                    'type': 'Find',
                    'key': find_key,
                    'snapshot': find_snapshot,
                    'result': value
                }
            else:
                st.warning(f"✗ Key {find_key} not found")
                add_to_history("Find", f"key={find_key}, snapshot={find_snapshot}, result=None")
                st.session_state.last_operation = {
                    'type': 'Find',
                    'key': find_key,
                    'snapshot': find_snapshot,
                    'result': None
                }
        
        st.divider()
        
        # Erase operation
        st.subheader("Erase (Delete)")
        with st.form("erase_form"):
            erase_key = st.number_input("Key to erase", min_value=1, value=10, step=1, key="erase_key")
            use_versioning_erase = st.checkbox("Use Versioning (Out-of-place)", value=True, 
                                              help="Uncheck for in-place deletion", key="erase_versioning")
            erase_submitted = st.form_submit_button("Erase", use_container_width=True)
        
        if erase_submitted:
            if tree.erase(erase_key, use_versioning=use_versioning_erase):
                add_to_history("Erase", f"key={erase_key}, versioning={use_versioning_erase}")
                st.success(f"✓ Erased key={erase_key}")
                st.session_state.last_operation = {
                    'type': 'Erase',
                    'key': erase_key,
                    'versioning': use_versioning_erase
                }
                # Also erase from regular tree for comparison
                if comparison_mode:
                    regular_tree.erase(erase_key)
            else:
                st.warning(f"✗ Key {erase_key} not found")
                add_to_history("Erase", f"key={erase_key}, result=not_found")
        
        st.divider()
        
        # Range Query operation
        st.subheader("Range Query")
        with st.form("range_query_form"):
            range_lower = st.number_input("Lower Bound (inclusive)", min_value=0, value=10, step=1, key="range_lower")
            range_upper = st.number_input("Upper Bound (exclusive)", min_value=1, value=50, step=1, key="range_upper")
            range_snapshot = st.selectbox(
                "Snapshot (optional)",
                options=[None] + list(tree.snapshots.keys()),
                format_func=lambda x: "Current" if x is None else f"Snapshot #{x}",
                key="range_snapshot"
            )
            range_submitted = st.form_submit_button("Range Query", use_container_width=True)
        
        if range_submitted:
            results = tree.range_query(range_lower, range_upper, snapshot_id=range_snapshot)
            if results:
                snapshot_info = f" in snapshot #{range_snapshot}" if range_snapshot else ""
                st.success(f"✓ Found {len(results)} keys in range [{range_lower}, {range_upper}){snapshot_info}")
                # Display results
                result_text = ", ".join([f"({k}, {v})" for k, v in results])
                st.code(result_text)
                add_to_history("Range Query", f"range=[{range_lower}, {range_upper}), snapshot={range_snapshot}, count={len(results)}")
                st.session_state.last_operation = {
                    'type': 'Range Query',
                    'lower': range_lower,
                    'upper': range_upper,
                    'snapshot': range_snapshot,
                    'results': results
                }
            else:
                st.info(f"No keys found in range [{range_lower}, {range_upper})")
                add_to_history("Range Query", f"range=[{range_lower}, {range_upper}), snapshot={range_snapshot}, count=0")
        
        st.divider()
        
        # Snapshot operation
        st.subheader("Snapshot")
        if st.button("Take Snapshot", use_container_width=True):
            snapshot_id = tree.take_snapshot()
            add_to_history("Snapshot", f"Created snapshot #{snapshot_id}")
            st.success(f"✓ Snapshot #{snapshot_id} created (timestamp: {tree.snapshots[snapshot_id]})")
            st.session_state.last_operation = {
                'type': 'Snapshot',
                'snapshot_id': snapshot_id,
                'timestamp': tree.snapshots[snapshot_id]
            }
        
        st.divider()
        
        # Tree management
        st.subheader("Tree Management")
        if st.button("Clear Tree", use_container_width=True):
            st.session_state.tree = MultiversionBTree(branching_factor=4)
            st.session_state.regular_tree = RegularBTree(branching_factor=4)
            st.session_state.operation_history = []
            st.session_state.selected_snapshot = None
            st.rerun()
        
        if st.button("Reset History", use_container_width=True):
            st.session_state.operation_history = []
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Tree Visualization")
        
        # Snapshot selector
        view_mode = st.radio(
            "View Mode",
            options=["Current", "Snapshot"],
            horizontal=True,
            key="view_mode"
        )
        
        selected_snapshot = None
        if view_mode == "Snapshot":
            if tree.snapshots:
                selected_snapshot = st.selectbox(
                    "Select Snapshot",
                    options=list(tree.snapshots.keys()),
                    format_func=lambda x: f"Snapshot #{x} (timestamp: {tree.snapshots[x]})"
                )
                st.session_state.selected_snapshot = selected_snapshot
            else:
                st.info("No snapshots taken yet. Take a snapshot first!")
                selected_snapshot = None
        
        # Tree visualization
        tree_text = visualize_tree_text(tree, snapshot_id=selected_snapshot)
        st.code(tree_text, language="text")
        
        # Operation Explanation (Education Mode)
        if education_mode and st.session_state.last_operation:
            st.subheader("🔍 What Just Happened?")
            last_op = st.session_state.last_operation
            
            if last_op['type'] == 'Insert':
                st.markdown(get_operation_explanation("Insert", last_op))
                if last_op.get('versioning', True):
                    st.info("💡 **Out-of-Place Update (VoB-Tree)**: A new version was created. This preserves history for snapshots.")
                else:
                    st.info("💡 **In-Place Update (ViB-Tree)**: The node was modified directly. More efficient but no history preserved.")
            
            elif last_op['type'] == 'Find':
                st.markdown(get_operation_explanation("Find", last_op))
                if last_op.get('snapshot'):
                    st.info(f"💡 **Snapshot Query**: Finding key in snapshot #{last_op['snapshot']}. The tree traverses version chains to find the correct version of each node at that timestamp.")
                else:
                    st.info("💡 **Current State Query**: Finding key in the current state (latest version).")
            
            elif last_op['type'] == 'Snapshot':
                st.markdown(get_operation_explanation("Snapshot", last_op))
                st.info("💡 **Snapshot Created**: The global timestamp was incremented. Future queries can use this snapshot ID to see the tree as it was at this moment.")
            
            elif last_op['type'] == 'Erase':
                st.markdown("""
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
                """)
                if last_op.get('versioning', True):
                    st.info("💡 **Out-of-Place Erase (VoB-Tree)**: A new version was created. The key is removed from the current version but still exists in older versions (for snapshots).")
                else:
                    st.info("💡 **In-Place Erase (ViB-Tree)**: The key was removed directly. More efficient but no history preserved.")
            
            elif last_op['type'] == 'Range Query':
                st.markdown("""
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
                """)
                if last_op.get('snapshot'):
                    st.info(f"💡 **Snapshot Range Query**: Querying range in snapshot #{last_op['snapshot']}. All results are from the same consistent state.")
                else:
                    st.info("💡 **Current State Range Query**: Querying the current state. Results reflect the latest version of the tree.")
            
            st.divider()
        
        # Version chain details
        if tree.root is not None:
            st.subheader("🔗 Version Chain Information")
            if education_mode:
                st.info("""
                **Understanding Version Chains:**
                - Each node can have multiple versions linked together
                - Newest version is at the head (most recent)
                - Older versions are linked via `next_version` pointer
                - When querying a snapshot, the tree finds the version with timestamp ≤ snapshot timestamp
                """)
            else:
                st.info("Each node can have multiple versions. The version chain shows all versions of nodes.")
            
            # Show version statistics
            stats = get_tree_stats(tree, snapshot_id=selected_snapshot)
            st.write(f"**Max version chain length:** {stats['max_version_chain']}")
            st.write(f"**Total versions:** {stats['total_versions']}")
            
            # Detailed version chain explanation (Education Mode)
            if education_mode and tree.root:
                query_timestamp = tree.global_timestamp
                if selected_snapshot is not None:
                    query_timestamp = tree.snapshots[selected_snapshot]
                
                with st.expander("🔬 Detailed Version Chain Analysis"):
                    st.markdown(explain_version_chain(tree.root, query_timestamp))
                    st.markdown("""
                    **How Version Chain Traversal Works:**
                    1. Start at the head (newest version)
                    2. Check each version's timestamp
                    3. Find the version with timestamp ≤ query timestamp
                    4. Use that version for the query
                    5. This ensures queries see a consistent state
                    """)
    
    with col2:
        st.header("📈 Statistics")
        
        stats = get_tree_stats(tree, snapshot_id=selected_snapshot)
        
        st.metric("Total Keys", stats['total_keys'])
        st.metric("Total Nodes", stats['total_nodes'])
        st.metric("Tree Height", stats['tree_height'])
        st.metric("Total Versions", stats['total_versions'])
        st.metric("Max Version Chain", stats['max_version_chain'])
        st.metric("Global Timestamp", tree.global_timestamp)
        st.metric("Snapshots", len(tree.snapshots))
        
        # Snapshot list
        if tree.snapshots:
            st.subheader("📸 Snapshots")
            for snap_id, timestamp in tree.snapshots.items():
                with st.expander(f"Snapshot #{snap_id} (ts: {timestamp})"):
                    snap_stats = get_tree_stats(tree, snapshot_id=snap_id)
                    st.write(f"Keys: {snap_stats['total_keys']}")
                    st.write(f"Nodes: {snap_stats['total_nodes']}")
                    if st.button(f"View Snapshot #{snap_id}", key=f"view_{snap_id}"):
                        st.session_state.selected_snapshot = snap_id
                        st.rerun()
    
    # Operation History
    st.header("📜 Operation History")
    if st.session_state.operation_history:
        # Show last 20 operations
        recent_history = st.session_state.operation_history[-20:]
        for op in reversed(recent_history):
            st.text(f"[ts={op['timestamp']}] {op['operation']}: {op['details']}")
    else:
        st.info("No operations performed yet.")
    
    # Comparison View
    if len(tree.snapshots) >= 2:
        st.header("🔍 Snapshot Comparison")
        col_a, col_b = st.columns(2)
        
        with col_a:
            snap_a = st.selectbox("Snapshot A", options=list(tree.snapshots.keys()), key="comp_a")
            stats_a = get_tree_stats(tree, snapshot_id=snap_a)
            st.write(f"**Keys:** {stats_a['total_keys']}")
            st.write(f"**Nodes:** {stats_a['total_nodes']}")
            st.code(visualize_tree_text(tree, snapshot_id=snap_a), language="text")
        
        with col_b:
            snap_b = st.selectbox("Snapshot B", options=list(tree.snapshots.keys()), key="comp_b")
            stats_b = get_tree_stats(tree, snapshot_id=snap_b)
            st.write(f"**Keys:** {stats_b['total_keys']}")
            st.write(f"**Nodes:** {stats_b['total_nodes']}")
            st.code(visualize_tree_text(tree, snapshot_id=snap_b), language="text")
        
        # Show differences
        diff_keys = stats_b['total_keys'] - stats_a['total_keys']
        diff_nodes = stats_b['total_nodes'] - stats_a['total_nodes']
        st.info(f"**Difference:** {diff_keys} keys, {diff_nodes} nodes between snapshots")
    
    # Educational Tutorial Section
    if education_mode:
        st.header("🎓 Interactive Tutorial")
        
        tutorial_step = st.radio(
            "Follow this tutorial to understand the paper's concepts:",
            options=[
                "1. Basic Insertion",
                "2. Understanding Versioning",
                "3. Taking Snapshots",
                "4. Querying Snapshots",
                "5. In-Place vs Out-of-Place",
                "6. Linearizability Demo"
            ],
            key="tutorial_step"
        )
        
        with st.expander("📝 Tutorial Instructions", expanded=True):
            if tutorial_step == "1. Basic Insertion":
                st.markdown("""
                **Step 1: Basic Insertion**
                
                1. In the sidebar, insert key=10, value=100
                2. Insert key=20, value=200
                3. Insert key=30, value=300
                4. Watch the tree visualization update
                5. Check the statistics to see the tree growing
                
                **What you're learning:** How keys are inserted into the B-Tree structure.
                """)
            
            elif tutorial_step == "2. Understanding Versioning":
                st.markdown("""
                **Step 2: Understanding Versioning**
                
                1. Insert key=10 with "Use Versioning" **checked**
                2. Take a snapshot (Snapshot #1)
                3. Insert key=20 with versioning **checked**
                4. Look at the version chain information
                5. Notice how versions are created
                
                **What you're learning:** How nodes get multiple versions when versioning is enabled.
                Each modification creates a new version linked to the old one.
                """)
            
            elif tutorial_step == "3. Taking Snapshots":
                st.markdown("""
                **Step 3: Taking Snapshots**
                
                1. Insert keys: 10, 20, 30
                2. Click "Take Snapshot" → creates Snapshot #1
                3. Insert more keys: 40, 50
                4. Click "Take Snapshot" again → creates Snapshot #2
                5. Check the snapshot list in statistics
                
                **What you're learning:** Snapshots capture the tree state at a specific timestamp.
                They're lightweight (just a timestamp) and enable historical queries.
                """)
            
            elif tutorial_step == "4. Querying Snapshots":
                st.markdown("""
                **Step 4: Querying Snapshots**
                
                1. Insert keys: 10, 20, 30
                2. Take Snapshot #1
                3. Insert keys: 40, 50
                4. Switch view mode to "Snapshot"
                5. Select Snapshot #1
                6. Notice the tree only shows keys 10, 20, 30
                7. Try finding key=40 in Snapshot #1 (won't be found!)
                8. Switch back to "Current" and find key=40 (will be found!)
                
                **What you're learning:** Snapshots preserve historical states.
                Queries on snapshots see the tree as it was when the snapshot was taken.
                """)
            
            elif tutorial_step == "5. In-Place vs Out-of-Place":
                st.markdown("""
                **Step 5: In-Place vs Out-of-Place Updates**
                
                1. Insert key=10 with versioning **unchecked** (in-place)
                2. Check statistics - notice version count
                3. Insert key=20 with versioning **checked** (out-of-place)
                4. Check statistics again - version count increased!
                5. Compare the version chain lengths
                
                **What you're learning:** 
                - **In-place (ViB-Tree)**: Direct modification, efficient, no history
                - **Out-of-place (VoB-Tree)**: Creates new versions, preserves history
                """)
            
            elif tutorial_step == "6. Linearizability Demo":
                st.markdown("""
                **Step 6: Linearizability Demo**
                
                1. Insert keys: 10, 20, 30
                2. Take Snapshot #1
                3. Insert keys: 40, 50 (simulating concurrent update)
                4. Query Snapshot #1 for keys 10, 20, 30 → all found
                5. Query Snapshot #1 for key 40 → NOT found (correct!)
                6. Query current state for key 40 → found (correct!)
                
                **What you're learning:** Linearizability means queries on snapshots see
                a consistent state. No mixing of old and new states. This is what makes
                the multiversion B-Tree correct for concurrent operations.
                """)
    
    # Comparison Mode: Show why Multiversion B-Tree is better
    if comparison_mode:
        st.header("⚖️ Comparison: Multiversion B-Tree vs Regular B-Tree")
        st.info("""
        **Why the Paper's Implementation is Better:**
        This comparison shows the key advantages of the multiversion B-Tree over a regular B-Tree.
        The paper implemented versioning to solve critical problems in concurrent environments.
        """)
        
        col_mv, col_reg = st.columns(2)
        
        with col_mv:
            st.subheader("🌳 Multiversion B-Tree (Paper's Implementation)")
            mv_stats = get_tree_stats(tree, snapshot_id=selected_snapshot)
            
            st.metric("Total Keys", mv_stats['total_keys'])
            st.metric("Total Nodes", mv_stats['total_nodes'])
            st.metric("Total Versions", mv_stats['total_versions'])
            st.metric("Snapshots Available", len(tree.snapshots))
            st.metric("Can Query History", "✅ Yes" if tree.snapshots else "❌ No snapshots yet")
            
            st.write("**Tree Structure:**")
            st.code(visualize_tree_text(tree, snapshot_id=selected_snapshot), language="text")
            
            # Advantages
            st.markdown("""
            **✅ Advantages:**
            - **Historical Queries**: Can query past states via snapshots
            - **Linearizability**: Ensures consistent concurrent operations
            - **Time-Travel**: Query the tree as it was at any point in time
            - **Concurrent Safety**: Updates don't interfere with historical queries
            - **Version Tracking**: See how data evolved over time
            """)
        
        with col_reg:
            st.subheader("🌲 Regular B-Tree (Traditional)")
            reg_stats = regular_tree.get_stats()
            
            st.metric("Total Keys", reg_stats['total_keys'])
            st.metric("Total Nodes", reg_stats['total_nodes'])
            st.metric("Total Versions", "N/A (No versioning)")
            st.metric("Snapshots Available", "❌ Not supported")
            st.metric("Can Query History", "❌ No")
            
            st.write("**Tree Structure:**")
            st.code(regular_tree.visualize_tree_text(), language="text")
            
            # Limitations
            st.markdown("""
            **❌ Limitations:**
            - **No History**: Cannot query past states
            - **No Snapshots**: Cannot capture tree state
            - **Concurrent Issues**: Updates can interfere with queries
            - **No Time-Travel**: Only see current state
            - **Data Loss**: Once updated, old state is lost forever
            """)
        
        # Demonstration of advantages
        st.divider()
        st.subheader("🎯 Key Improvements Demonstrated")
        
        demo_tab1, demo_tab2, demo_tab3 = st.tabs([
            "1. Historical Queries",
            "2. Concurrent Operations",
            "3. Why Versioning?"
        ])
        
        with demo_tab1:
            st.markdown("""
            **Problem Regular B-Tree Can't Solve:**
            
            Imagine you need to query the database as it was yesterday, or compare current data
            with data from last week. A regular B-Tree **cannot** do this - once data is updated,
            the old state is lost forever.
            
            **Multiversion B-Tree Solution:**
            """)
            
            if tree.snapshots:
                st.success("✅ **You can query snapshots!** Try selecting a snapshot in the view mode above.")
                st.write("**Example:**")
                st.write(f"- Current state has {mv_stats['total_keys']} keys")
                for snap_id, timestamp in list(tree.snapshots.items())[:3]:
                    snap_stats = get_tree_stats(tree, snapshot_id=snap_id)
                    st.write(f"- Snapshot #{snap_id} (timestamp {timestamp}) had {snap_stats['total_keys']} keys")
                st.info("💡 **This is impossible with a regular B-Tree!** Once you update, old data is gone.")
            else:
                st.warning("⚠️ Take a snapshot first to see this advantage!")
                st.write("**Steps to demonstrate:**")
                st.write("1. Insert some keys (e.g., 10, 20, 30)")
                st.write("2. Take a snapshot")
                st.write("3. Insert more keys (e.g., 40, 50)")
                st.write("4. Query the snapshot - you'll see only the original keys!")
        
        with demo_tab2:
            st.markdown("""
            **Problem: Concurrent Operations**
            
            In a regular B-Tree, if you're querying while another thread is updating, you might see
            inconsistent results (some old data, some new data). This violates linearizability.
            
            **Multiversion B-Tree Solution:**
            """)
            st.success("""
            ✅ **Linearizable Operations:**
            - Queries on snapshots see a **consistent** state
            - No mixing of old and new data
            - Updates don't interfere with historical queries
            - Each snapshot provides an atomic view
            """)
            
            if tree.snapshots and mv_stats['total_keys'] > 0:
                st.write("**Demonstration:**")
                st.write(f"1. Snapshot was taken when tree had {get_tree_stats(tree, snapshot_id=1)['total_keys']} keys")
                st.write(f"2. Current tree has {mv_stats['total_keys']} keys")
                st.write("3. Querying the snapshot will **always** return the same results")
                st.write("4. This is **guaranteed** by the versioning mechanism")
            else:
                st.info("💡 Take a snapshot and insert more keys to see this in action!")
        
        with demo_tab3:
            st.markdown("""
            **Why Did the Paper Implement Versioning?**
            
            The paper needed to solve these critical problems:
            """)
            
            reasons = [
                {
                    "problem": "**Concurrent Multipoint Queries**",
                    "regular": "Regular B-Tree: Range queries can see inconsistent state during updates",
                    "multiversion": "Multiversion B-Tree: Snapshots provide consistent views for range queries",
                    "paper_quote": "\"The baseline GPU B-Tree structure provides no guarantees on the linearizability of concurrent range queries and updates.\""
                },
                {
                    "problem": "**Historical Data Access**",
                    "regular": "Regular B-Tree: Cannot access past states",
                    "multiversion": "Multiversion B-Tree: Can query any historical state via snapshots",
                    "paper_quote": "\"A snapshot is a read-only version of a data structure that contains all key-value pairs stored when a take_snapshot operation is performed.\""
                },
                {
                    "problem": "**GPU Database Requirements**",
                    "regular": "Regular B-Tree: Not suitable for GPU databases needing historical queries",
                    "multiversion": "Multiversion B-Tree: Designed for GPU databases with time-travel queries",
                    "paper_quote": "\"GPUs are increasingly used in data science, machine learning, and data analytics pipelines.\""
                }
            ]
            
            for i, reason in enumerate(reasons, 1):
                with st.expander(f"{i}. {reason['problem']}", expanded=(i==1)):
                    st.markdown(f"**Regular B-Tree:** {reason['regular']}")
                    st.markdown(f"**Multiversion B-Tree:** {reason['multiversion']}")
                    st.markdown(f"*From the Paper:* {reason['paper_quote']}")
            
            st.markdown("""
            **Key Insight:**
            
            The paper's implementation uses **Copy-on-Write (COW)** versioning to enable:
            - ✅ Historical queries without blocking updates
            - ✅ Linearizable concurrent operations
            - ✅ Efficient memory usage (only versions what's needed)
            - ✅ GPU-optimized design for high-performance databases
            """)
        
        # Visual comparison metrics
        st.divider()
        st.subheader("📊 Performance & Capability Comparison")
        
        comparison_data = {
            "Feature": [
                "Historical Queries",
                "Snapshot Support",
                "Linearizability",
                "Concurrent Safety",
                "Time-Travel Queries",
                "Memory Overhead",
                "Update Efficiency (no snapshots)",
                "Update Efficiency (with snapshots)"
            ],
            "Regular B-Tree": [
                "❌ No",
                "❌ No",
                "❌ No guarantee",
                "⚠️ Limited",
                "❌ No",
                "✅ Low",
                "✅ Fast (1 write)",
                "N/A"
            ],
            "Multiversion B-Tree": [
                "✅ Yes",
                "✅ Yes",
                "✅ Guaranteed",
                "✅ Safe",
                "✅ Yes",
                "⚠️ Moderate (versions)",
                "✅ Fast (1 write, ViB-Tree)",
                "⚠️ Slower (2 writes, VoB-Tree)"
            ]
        }
        
        import pandas as pd
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.info("""
        **Trade-off Analysis:**
        
        The multiversion B-Tree trades some memory and update efficiency for:
        - ✅ **Correctness**: Linearizable operations
        - ✅ **Functionality**: Historical queries
        - ✅ **Safety**: Concurrent operation guarantees
        
        This is why the paper chose this design - **correctness and functionality are more important
        than pure speed** for GPU databases that need to support complex queries.
        """)
    
    # Information panel
    with st.expander("ℹ️ About This Simulator"):
        st.markdown("""
        This simulator demonstrates the **GPU Multiversion B-Tree** from the PACT 2022 paper.
        
        **Key Features:**
        - ✅ Node versioning with version chains
        - ✅ Snapshot functionality for historical queries
        - ✅ In-place (ViB-Tree) and out-of-place (VoB-Tree) updates
        - ✅ Point queries with snapshot support
        - ✅ Version chain traversal
        
        **How to Use:**
        1. Enable Education Mode to see detailed explanations
        2. Follow the interactive tutorial
        3. Insert keys using the sidebar
        4. Take snapshots to capture tree state
        5. Query snapshots to see historical states
        6. Compare different snapshots
        
        **Paper Reference:**
        "A GPU Multiversion B-Tree" by Awad, Porumbescu, and Owens (PACT 2022)
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("**Multiversion B-Tree Simulator** | Based on PACT 2022 Paper")


if __name__ == "__main__":
    main()

