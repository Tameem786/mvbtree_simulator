# Quick Start Guide

## Running the Tests

```bash
python tests/test_basic.py
```

## Running the CLI Interface

```bash
python main.py
```

## Example Session

1. Start the CLI: `python main.py`
2. Insert some keys:
   - Choose option 1
   - Insert key=10, value=100
   - Insert key=20, value=200
   - Insert key=30, value=300
3. Take a snapshot:
   - Choose option 3 (creates snapshot #1)
4. Insert more keys:
   - Insert key=40, value=400
   - Insert key=50, value=500
5. Query current state:
   - Choose option 5 (should show keys: 10, 20, 30, 40, 50)
6. Query snapshot #1:
   - Choose option 6, enter snapshot ID: 1
   - Should show keys: 10, 20, 30 (keys 40 and 50 weren't inserted yet)
7. Find a key in snapshot:
   - Choose option 4, snapshot ID: 1, key: 10
   - Should find value=100
   - Try key: 40 (should not be found in snapshot #1)

## Project Structure

```
mvbtree_simulator/
├── features/
│   └── base.py          # Core multiversion B-Tree implementation
├── tests/
│   └── test_basic.py    # Basic functionality tests
├── main.py              # CLI interface
├── README.md
└── requirements.txt
```

## What's Implemented

✅ Basic B-Tree structure with versioning
✅ Insert operations (with versioning)
✅ Find operations (current and snapshot-based)
✅ Snapshot functionality
✅ Version chain traversal
✅ CLI interface for testing

## Next Steps (Future Enhancements)

- Range queries
- Delete operations
- Tree visualization (graphical)
- Comparison with regular B-Tree
- Statistics and metrics
- Concurrent operations simulation

