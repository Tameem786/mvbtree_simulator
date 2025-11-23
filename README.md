# Multiversion B-Tree Simulator

A Python-based simulation of the GPU Multiversion B-Tree data structure from the PACT 2022 paper: **"A GPU Multiversion B-Tree"** by Muhammad A. Awad, Serban D. Porumbescu, and John D. Owens (PACT '22).

This simulator demonstrates the core concepts of the multiversion B-Tree in a simplified, CPU-based implementation suitable for educational purposes and class projects.

## Project Structure

```
mvbtree_simulator/
├── features/
│   └── base.py          # Base multiversion B-Tree implementation
├── tests/
│   └── test_basic.py    # Basic tests
├── app.py               # Streamlit web application (main simulation software)
├── main.py              # CLI interface
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── QUICK_START.md      # Quick start guide
├── ARCHITECTURE.md     # Architecture documentation
├── run_app.sh          # Script to run app (Linux/Mac)
└── run_app.bat         # Script to run app (Windows)
```

## Features from the Paper

This simulator implements and demonstrates the following features from the PACT 2022 paper:

### Core Data Structure Features

#### ✅ **1. Multiversion B-Tree Structure**
- B-Tree with configurable branching factor
- Cache-line-sized node concept (simplified for CPU simulation)
- Support for internal and leaf nodes

#### ✅ **2. Node Versioning**
- Each node can have multiple versions (version list/chain)
- Most recent version is the head of the version list
- Version chain traversal to find appropriate version for a given timestamp
- Timestamp-based version identification

#### ✅ **3. Snapshot Functionality**
- `take_snapshot()` operation that atomically captures the current state
- Snapshot ID assignment and management
- Global timestamp counter for version tracking
- Query operations can specify a snapshot ID to query historical states

### Update Strategies

#### ✅ **4. In-Place Updates (ViB-Tree)**
- Direct modification of nodes when no active snapshots
- Only possible when global timestamp matches node timestamp
- More efficient (single write operation)
- Used when snapshots are not concurrently active

#### ✅ **5. Out-of-Place Updates (VoB-Tree)**
- Copy-on-Write (COW) strategy
- Creates new version of modified nodes
- Required when snapshots may be active concurrently
- Links new version to older versions (version chain)
- Two write operations (copy + modify)

### Query Operations

#### ✅ **6. Point Queries (Find)**
- Find a specific key in the tree
- Supports querying current state or specific snapshot
- Traverses version chains to find correct node version
- Returns associated value or None if not found

#### ✅ **7. Range Queries**
- Query all keys within a range [lower_bound, upper_bound)
- Linearizable multipoint queries
- Supports snapshot-based range queries
- Returns all key-value pairs in the specified range

### Mutation Operations

#### ✅ **8. Insert Operations**
- Insert key-value pairs into the tree
- Automatic version creation when needed
- Handles node splitting (simplified)
- Supports both in-place and out-of-place strategies

#### ✅ **9. Delete/Erase Operations**
- Remove keys from the tree
- Version-aware deletion
- Supports both in-place and out-of-place strategies
- Historical queries can still see erased keys in old snapshots

### Concurrency and Correctness

#### ✅ **10. Linearizability Guarantee**
- Ensures concurrent operations appear to execute atomically
- Snapshot-based queries provide consistent views
- Demonstrates how versioning enables linearizable multipoint queries
- Range queries on snapshots return consistent results

#### ⏳ **11. Concurrent Operations Simulation**
- Simulate concurrent insertions and queries
- Concurrent insert and range query operations
- Concurrent find and erase operations
- Thread-safe operations (simulated for CPU)

### Memory Management

#### ⏳ **12. Epoch-Based Reclamation (EBR) Simulation**
- Safe memory reclamation for retired node versions
- Epoch tracking for memory safety
- Prevents use-after-free errors
- Demonstrates GPU-optimized memory reclamation strategy

### Advanced Features

#### ⏳ **13. Snapshot Scopes (Simplified)**
- **Host-side snapshot**: Device-wide barrier (simplified as global snapshot)
- **Stream-concurrent snapshot**: Snapshot on specific stream (simulated)
- **Tile-wide snapshot**: Snapshot within a tile/block (simulated)

#### ⏳ **14. Side-Links for Concurrent Traversal**
- Side-links to chain nodes on the same level
- Allows traversal to continue even when nodes are split
- Enables lock-free concurrent operations

#### ✅ **15. Statistics and Metrics**
- Track number of versions per node
- Total nodes, keys, and tree height
- Snapshot statistics
- Version chain length statistics
- Real-time metrics dashboard in web app

### Visualization and Analysis

#### ✅ **16. Tree Visualization**
- Text-based visual representation of tree structure
- Show version chains for each node
- Display node types (Leaf/Internal) and timestamps
- View tree at current state or specific snapshots

#### ✅ **17. Comparison Mode**
- Compare multiversion B-Tree with regular B-Tree
- Side-by-side feature comparison
- Demonstrates advantages of multiversion approach
- Shows limitations of regular B-Tree
- Interactive comparison in web application

#### ✅ **18. Education Mode**
- Step-by-step operation explanations
- Show what happens during each operation
- Educational explanations of paper concepts
- Interactive tutorial with 6 steps
- Concept learning panel
- Operation history tracking
- Detailed version chain analysis

## Implementation Status

### ✅ Implemented (Current)
- **Core Data Structure:**
  - Multiversion B-Tree structure with configurable branching factor
  - Node versioning with version chains
  - Snapshot functionality with timestamp management
  - Version chain traversal for historical queries

- **Operations:**
  - Insert operations (with in-place and out-of-place strategies)
  - Find operations (point queries) - current and snapshot-based
  - Erase/Delete operations (with versioning support)
  - Range queries (multipoint queries) - current and snapshot-based
  - Snapshot creation and management

- **Interfaces:**
  - CLI interface (`main.py`) for command-line testing
  - Streamlit web application (`app.py`) with interactive UI
  - Basic test suite (`tests/test_basic.py`)

- **Features:**
  - Education Mode with detailed explanations and interactive tutorial
  - Comparison Mode (Multiversion B-Tree vs Regular B-Tree)
  - Tree visualization (text-based)
  - Statistics and metrics dashboard
  - Operation history tracking
  - Snapshot comparison
  - Regular B-Tree implementation for comparison

### ⏳ Planned (Future Enhancements)
- **Advanced Concurrency:**
  - Concurrent operations simulation (threading)
  - Epoch-Based Reclamation (EBR) simulation
  - Side-links for concurrent traversal

- **Advanced Features:**
  - Graphical tree visualization (D3.js or similar)
  - Advanced snapshot scopes (host-side, stream-concurrent, tile-wide)
  - Enhanced statistics dashboard with memory overhead measurement
  - Operation rate tracking and performance metrics

## Requirements

- Python 3.7+
- Streamlit (for web application)
- Optional: graphviz, plotly (for enhanced visualization)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run Streamlit Web Application (Main Simulation Software)

The Streamlit app is the main simulation software that provides an interactive web interface:

```bash
# Method 1: Direct command
streamlit run app.py

# Method 2: Using script (Linux/Mac)
bash run_app.sh

# Method 3: Using script (Windows)
run_app.bat
```

The app will open in your default web browser at `http://localhost:8501`

**Features of the Web App:**
- 🌳 Interactive tree visualization (text-based)
- 🔧 Insert, Find, Erase, Range Query, and Snapshot operations
- 📸 Snapshot management and comparison
- 📈 Real-time statistics dashboard
- 🔗 Version chain visualization and analysis
- 📜 Operation history tracking
- 📚 Education Mode with detailed explanations and interactive tutorial
- ⚖️ Comparison Mode (Multiversion vs Regular B-Tree)

### Run Tests
```bash
python tests/test_basic.py
```

### Run CLI Interface
```bash
python main.py
```

### Example Workflow
1. Insert keys: `insert(10, 100)`, `insert(20, 200)`, `insert(30, 300)`
2. Take snapshot: `snapshot_id = take_snapshot()`
3. Insert more keys: `insert(40, 400)`, `insert(50, 500)`
4. Query snapshot: `find(10, snapshot_id=1)` → returns 100
5. Query current: `find(40)` → returns 400
6. Query snapshot for new key: `find(40, snapshot_id=1)` → returns None

See [QUICK_START.md](QUICK_START.md) for detailed examples.

## Paper Reference

**A GPU Multiversion B-Tree**  
Muhammad A. Awad, Serban D. Porumbescu, and John D. Owens  
*Proceedings of the International Conference on Parallel Architectures and Compilation Techniques (PACT 2022)*  
DOI: [10.1145/3559009.3569681](https://dl.acm.org/doi/10.1145/3559009.3569681)

## Key Concepts Demonstrated

1. **Versioning**: How nodes maintain multiple versions to support historical queries
2. **Snapshots**: Atomic capture of tree state at a specific point in time
3. **Copy-on-Write**: Creating new versions only when necessary
4. **Linearizability**: How versioning enables consistent concurrent queries
5. **Memory Efficiency**: Trade-offs between in-place and out-of-place updates

## License

This simulator is created for educational purposes as a class project based on the research paper.

