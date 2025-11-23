"""
Basic tests for the Multiversion B-Tree simulator.

Run with: python -m pytest tests/test_basic.py
Or: python tests/test_basic.py
"""

import sys
import os

# Add parent directory to path to import features
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.base import MultiversionBTree


def test_basic_insert_and_find():
    """Test basic insert and find operations."""
    tree = MultiversionBTree()
    
    # Insert some keys
    tree.insert(10, 100)
    tree.insert(20, 200)
    tree.insert(30, 300)
    
    # Find them
    assert tree.find(10) == 100
    assert tree.find(20) == 200
    assert tree.find(30) == 300
    assert tree.find(40) is None  # Non-existent key
    
    print("✓ Basic insert and find test passed")


def test_snapshot_functionality():
    """Test snapshot functionality."""
    tree = MultiversionBTree()
    
    # Insert initial keys
    tree.insert(10, 100)
    tree.insert(20, 200)
    
    # Take snapshot
    snapshot1 = tree.take_snapshot()
    
    # Insert more keys
    tree.insert(30, 300)
    tree.insert(40, 400)
    
    # Query current state
    current_keys = tree.get_all_keys()
    assert 10 in current_keys
    assert 20 in current_keys
    assert 30 in current_keys
    assert 40 in current_keys
    
    # Query snapshot 1
    snapshot1_keys = tree.get_all_keys(snapshot_id=snapshot1)
    assert 10 in snapshot1_keys
    assert 20 in snapshot1_keys
    assert 30 not in snapshot1_keys  # Wasn't inserted yet
    assert 40 not in snapshot1_keys  # Wasn't inserted yet
    
    print("✓ Snapshot functionality test passed")


def test_find_in_snapshot():
    """Test finding keys in specific snapshots."""
    tree = MultiversionBTree()
    
    # Insert and take snapshot
    tree.insert(10, 100)
    snapshot1 = tree.take_snapshot()
    
    # Insert more
    tree.insert(20, 200)
    snapshot2 = tree.take_snapshot()
    
    # Insert even more
    tree.insert(30, 300)
    
    # Test finds
    assert tree.find(10, snapshot_id=snapshot1) == 100
    assert tree.find(20, snapshot_id=snapshot1) is None  # Not in snapshot1
    assert tree.find(10, snapshot_id=snapshot2) == 100
    assert tree.find(20, snapshot_id=snapshot2) == 200
    assert tree.find(30, snapshot_id=snapshot2) is None  # Not in snapshot2
    
    # Current state
    assert tree.find(10) == 100
    assert tree.find(20) == 200
    assert tree.find(30) == 300
    
    print("✓ Find in snapshot test passed")


def test_versioning():
    """Test that versioning creates new node versions."""
    tree = MultiversionBTree()
    
    # Insert key
    tree.insert(10, 100)
    initial_timestamp = tree.global_timestamp
    
    # Take snapshot
    snapshot1 = tree.take_snapshot()
    
    # Insert another key (should create new version)
    tree.insert(20, 200)
    
    # Check that timestamp increased
    assert tree.global_timestamp > initial_timestamp
    
    # Verify we can still query snapshot1
    assert tree.find(10, snapshot_id=snapshot1) == 100
    assert tree.find(20, snapshot_id=snapshot1) is None
    
    print("✓ Versioning test passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*50)
    print("Running Basic Tests")
    print("="*50)
    
    test_basic_insert_and_find()
    test_snapshot_functionality()
    test_find_in_snapshot()
    test_versioning()
    
    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50)


if __name__ == "__main__":
    run_all_tests()

