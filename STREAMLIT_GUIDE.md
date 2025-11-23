# Streamlit Web Application Guide

## Overview

The Streamlit web application (`app.py`) is the main simulation software that provides an interactive interface to explore and demonstrate the Multiversion B-Tree concepts from the PACT 2022 paper.

## Running the Application

### Prerequisites
```bash
pip install -r requirements.txt
```

### Start the App
```bash
streamlit run app.py
```

The application will automatically open in your web browser at `http://localhost:8501`

## Interface Overview

### Sidebar - Operations Panel

#### Insert Operation
- **Key**: Integer key to insert
- **Value**: Integer value associated with the key
- **Use Versioning**: Checkbox to enable/disable versioning
  - ✅ Checked: Out-of-place update (VoB-Tree) - creates new versions
  - ❌ Unchecked: In-place update (ViB-Tree) - modifies directly

#### Find Operation
- **Key**: Key to search for
- **Snapshot**: Optional snapshot to query (or "Current" for latest state)
- Returns the value associated with the key

#### Snapshot Operation
- Click "Take Snapshot" to capture the current tree state
- Each snapshot gets a unique ID and timestamp

#### Tree Management
- **Clear Tree**: Reset the entire tree
- **Reset History**: Clear operation history

### Main Panel

#### Tree Visualization
- Text-based tree visualization showing:
  - Node structure (keys)
  - Node type (Leaf/Internal)
  - Version count and timestamp
- **View Mode**: Toggle between "Current" and "Snapshot" view
- When in Snapshot mode, select which snapshot to view

#### Statistics Dashboard
Real-time metrics:
- **Total Keys**: Number of keys in the tree
- **Total Nodes**: Number of nodes
- **Tree Height**: Maximum depth
- **Total Versions**: Total number of node versions
- **Max Version Chain**: Longest version chain
- **Global Timestamp**: Current global timestamp
- **Snapshots**: Number of snapshots taken

#### Snapshot List
- View all snapshots
- Click to view a specific snapshot
- See statistics for each snapshot

#### Operation History
- Chronological list of all operations
- Shows operation type, details, and timestamp

#### Snapshot Comparison
- Compare two snapshots side-by-side
- See differences in keys and nodes
- Visualize how the tree changed between snapshots

## Example Workflow

### 1. Basic Insertion and Querying
1. In sidebar, insert key=10, value=100
2. Insert key=20, value=200
3. Insert key=30, value=300
4. Use "Find" to search for key=20 → should return 200

### 2. Snapshot Demonstration
1. Insert keys: 10, 20, 30
2. Click "Take Snapshot" → creates Snapshot #1
3. Insert more keys: 40, 50
4. Switch to "Snapshot" view mode
5. Select "Snapshot #1"
6. Notice the tree only shows keys 10, 20, 30 (the state when snapshot was taken)
7. Switch back to "Current" to see all keys including 40, 50

### 3. Versioning Demonstration
1. Insert key=10, value=100
2. Take Snapshot #1
3. Insert key=20, value=200 (with versioning enabled)
4. Check the tree visualization - you'll see version information
5. The statistics show version counts

### 4. In-Place vs Out-of-Place Updates
1. Insert key=10 with "Use Versioning" **unchecked** (in-place)
2. Take a snapshot
3. Insert key=20 with "Use Versioning" **checked** (out-of-place)
4. Compare the version chain lengths in statistics

### 5. Snapshot Comparison
1. Insert keys: 10, 20, 30
2. Take Snapshot #1
3. Insert keys: 40, 50, 60
4. Take Snapshot #2
5. Scroll to "Snapshot Comparison" section
6. Compare Snapshot #1 vs Snapshot #2
7. See the difference in key counts

## Key Concepts Demonstrated

### 1. **Versioning**
- Each node can have multiple versions
- Version chains are shown in the tree visualization
- Statistics show version counts

### 2. **Snapshots**
- Atomic capture of tree state
- Query historical states using snapshot IDs
- Compare different snapshots

### 3. **Copy-on-Write (COW)**
- When versioning is enabled, new versions are created
- Original versions are preserved
- Enables historical queries

### 4. **In-Place vs Out-of-Place**
- Toggle versioning to see the difference
- In-place is more efficient but doesn't preserve history
- Out-of-place preserves history for snapshots

### 5. **Linearizability**
- Snapshots provide consistent views
- Queries on snapshots return results as if executed at that point in time
- No mixing of old and new states

## Tips

1. **Start Simple**: Begin with a few insertions to understand the structure
2. **Use Snapshots**: Take snapshots frequently to see versioning in action
3. **Compare Snapshots**: Use the comparison feature to see how the tree evolves
4. **Check Statistics**: Monitor version counts and tree metrics
5. **View History**: Check operation history to track what you've done

## Troubleshooting

### App won't start
- Make sure Streamlit is installed: `pip install streamlit`
- Check Python version: `python --version` (should be 3.7+)

### Tree visualization looks wrong
- The text-based visualization is simplified
- For complex trees, focus on the statistics and snapshot comparison

### Can't see version chains
- Make sure you've taken a snapshot before inserting more keys
- Enable "Use Versioning" checkbox when inserting

## Next Steps

After exploring the basic features:
1. Try inserting many keys to see how the tree grows
2. Create multiple snapshots and compare them
3. Experiment with in-place vs out-of-place updates
4. Use the operation history to understand the sequence of operations

