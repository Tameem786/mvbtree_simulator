# Simulation Software Architecture

## Recommended Approach: **Web Application with Interactive Visualization**

For a class project demonstrating a data structure, a **web application** is the best choice because:

### Advantages:
1. ✅ **Easy to demonstrate** - Just open in browser, no installation
2. ✅ **Visual tree representation** - Show the B-Tree structure graphically
3. ✅ **Interactive controls** - Click buttons to insert, query, take snapshots
4. ✅ **Version visualization** - Show version chains and snapshots visually
5. ✅ **Easy to share** - Send a link or run locally
6. ✅ **Cross-platform** - Works on Windows, Mac, Linux
7. ✅ **Professional appearance** - Looks polished for presentations

### What the Web App Should Include:

#### 1. **Main Visualization Panel**
- Interactive B-Tree diagram
- Shows node structure (keys, values)
- Highlights active nodes during operations
- Color-coded version chains

#### 2. **Control Panel**
- Insert: Input key/value, click insert
- Find: Input key, select snapshot (optional)
- Range Query: Input lower/upper bounds
- Delete: Input key to remove
- Take Snapshot: Button to create snapshot
- Clear Tree: Reset everything

#### 3. **Snapshot View**
- List of all snapshots
- Click snapshot to view tree at that point
- Compare two snapshots side-by-side
- Show what changed between snapshots

#### 4. **Version Chain Visualization**
- Show version chains for each node
- Highlight which version is used for current query
- Show timestamps on each version

#### 5. **Statistics Dashboard**
- Number of nodes
- Number of versions
- Memory overhead
- Operation counts
- Snapshot count

#### 6. **Operation History**
- Timeline of operations
- Show insertions, deletions, snapshots
- Replay operations step-by-step

## Technology Stack Recommendation

### Backend:
- **Python Flask or FastAPI** - Simple, works with existing code
- REST API endpoints for operations
- WebSocket for real-time updates (optional)

### Frontend:
- **HTML/CSS/JavaScript** - Standard web technologies
- **D3.js or vis.js** - For tree visualization
- **Bootstrap or Tailwind CSS** - For styling

### Alternative: Streamlit (Easiest)
- **Streamlit** - Python-only, no separate frontend
- Fastest to build
- Built-in widgets and visualization
- Good for prototypes

## Implementation Phases

### Phase 1: Basic Web Interface (Current)
- ✅ CLI interface (done)
- ✅ Core B-Tree implementation (done)

### Phase 2: Simple Web App
- Add Flask backend
- Basic HTML interface
- Simple tree visualization (text-based or simple graphics)

### Phase 3: Enhanced Visualization
- Interactive tree diagram
- Version chain visualization
- Snapshot comparison

### Phase 4: Advanced Features
- Statistics dashboard
- Operation history
- Comparison mode

## Alternative: Desktop GUI

If web app is not preferred, a **desktop GUI** using:
- **Tkinter** (built into Python, simplest)
- **PyQt/PySide** (more professional, better widgets)
- **Kivy** (modern, cross-platform)

## Recommendation

**Start with Streamlit** for fastest development, then optionally migrate to Flask + D3.js for more control.

Streamlit advantages:
- ✅ Pure Python, no HTML/CSS/JS needed
- ✅ Built-in widgets (buttons, inputs, graphs)
- ✅ Can visualize tree with graphviz or plotly
- ✅ Can be deployed easily
- ✅ Perfect for class project scope

## Example Streamlit Structure

```python
# web/app.py
import streamlit as st
from features.base import MultiversionBTree
import graphviz

st.title("Multiversion B-Tree Simulator")

# Initialize tree in session state
if 'tree' not in st.session_state:
    st.session_state.tree = MultiversionBTree()

# Sidebar controls
with st.sidebar:
    st.header("Operations")
    # Insert, Find, Snapshot buttons
    # ...

# Main area
col1, col2 = st.columns(2)
with col1:
    st.subheader("Tree Visualization")
    # Show tree diagram
with col2:
    st.subheader("Statistics")
    # Show stats
```

