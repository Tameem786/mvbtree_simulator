# Operations Guide

## Overview

The Multiversion B-Tree simulator supports all the key operations from the PACT 2022 paper. This guide explains each operation and how they demonstrate the paper's concepts.

## Supported Operations

### 1. Insert / Update ✅

**What it does:**
- Inserts a new key-value pair into the tree
- If the key already exists, **updates** the value (this is how "update" works)

**How it works:**
- Finds the appropriate leaf node
- Creates new version if versioning is enabled (out-of-place)
- Or modifies directly if versioning is disabled (in-place)
- Updates timestamp

**Paper Reference:**
- Supports both in-place (ViB-Tree) and out-of-place (VoB-Tree) strategies
- From the paper: "Insert num_keys pairs {keys, values} into the data structure"

**Note on "Update":**
- The paper doesn't have a separate "update" operation
- **Update = Insert with existing key**
- When you insert a key that already exists, it updates the value
- This is standard B-Tree behavior

### 2. Find (Point Query) ✅

**What it does:**
- Finds a specific key in the tree
- Returns the associated value
- Can query current state or a specific snapshot

**How it works:**
- Traverses the tree from root to leaf
- For each node, finds the correct version (if snapshot specified)
- Returns the value if found, None otherwise

**Paper Reference:**
- "Find num_keys keys from the data structure"
- Supports snapshot-based queries: "Looks up the keys in the given timestamp"

**Key Feature:**
- Can query historical states via snapshots
- Regular B-Tree cannot do this!

### 3. Erase (Delete) ✅

**What it does:**
- Removes a key from the tree
- Supports versioning (out-of-place) or direct deletion (in-place)

**How it works:**
- Finds the leaf node containing the key
- Creates new version if versioning enabled
- Removes key-value pair
- Historical queries can still see the key in old snapshots

**Paper Reference:**
- "Erases num_keys keys from the data structure"
- Supports concurrent erase operations
- Can use out-of-place technique with memory reclaimer

**Key Feature:**
- When versioning is used, erased keys still exist in old snapshots
- This enables time-travel queries even after deletion

### 4. Range Query ✅

**What it does:**
- Finds all keys in a range [lower_bound, upper_bound)
- Returns all key-value pairs in that range
- Can query current state or a specific snapshot

**How it works:**
- Traverses the tree
- For each node, finds correct version (if snapshot specified)
- Collects all keys in the specified range
- Returns sorted results

**Paper Reference:**
- "Performs num_keys range queries defined by [lower_bound, upper_bound)"
- This is the **key feature** that motivated the paper!
- "Linearizable multipoint queries" - all results from same point in time

**Why This Matters:**
- Regular B-Tree: Range queries during updates can see inconsistent state
- Multiversion B-Tree: Range queries on snapshots see consistent state
- This is the main problem the paper solved!

### 5. Snapshot ✅

**What it does:**
- Captures the current state of the tree
- Returns a snapshot ID for future queries

**How it works:**
- Atomically increments global timestamp
- Stores snapshot ID → timestamp mapping
- No copying of tree structure (lightweight)

**Paper Reference:**
- "Takes a snapshot from on the given stream. Returns the snapshot handle."
- Snapshots enable historical queries
- Critical for linearizability

## Operation Comparison

| Operation | Regular B-Tree | Multiversion B-Tree | Key Difference |
|-----------|---------------|---------------------|----------------|
| Insert | ✅ Yes | ✅ Yes | Multiversion supports versioning |
| Find | ✅ Yes (current only) | ✅ Yes (current + snapshots) | **Can query history!** |
| Erase | ✅ Yes | ✅ Yes | Multiversion preserves history |
| Range Query | ✅ Yes (inconsistent) | ✅ Yes (consistent) | **Linearizable!** |
| Snapshot | ❌ No | ✅ Yes | **Unique to multiversion!** |

## Why These Operations Matter

### The Paper's Main Contribution

The paper's main contribution is enabling **linearizable multipoint queries** (range queries) in a concurrent environment.

**Problem:**
- Regular B-Tree: Range queries during updates can see inconsistent state
- Example: Query might see some old keys and some new keys (not linearizable)

**Solution:**
- Multiversion B-Tree: Range queries on snapshots see consistent state
- All results from the same point in time (linearizable)

### How Operations Demonstrate This

1. **Insert + Snapshot + Range Query:**
   - Insert keys: 10, 20, 30
   - Take snapshot
   - Insert keys: 40, 50
   - Range query on snapshot → only sees 10, 20, 30 (consistent!)
   - Range query on current → sees 10, 20, 30, 40, 50 (consistent!)

2. **Erase + Snapshot + Find:**
   - Insert key: 10
   - Take snapshot
   - Erase key: 10
   - Find key 10 in snapshot → found! (historical query)
   - Find key 10 in current → not found (current state)

3. **Concurrent Operations Simulation:**
   - Thread 1: Takes snapshot, then range query
   - Thread 2: Inserts new keys
   - Thread 1's range query → consistent results (doesn't see Thread 2's inserts)

## Update vs Insert

**Important:** The paper doesn't have a separate "update" operation.

**How Update Works:**
- Update = Insert with existing key
- When you insert a key that already exists, it updates the value
- This is standard B-Tree behavior

**Example:**
1. Insert key=10, value=100
2. Insert key=10, value=200 (update!)
3. Find key=10 → returns 200

## Complete Operation Set

The simulator now supports **all major operations** from the paper:

✅ **Insert** - Add/update key-value pairs
✅ **Find** - Point queries (current + snapshots)
✅ **Erase** - Delete keys (with versioning)
✅ **Range Query** - Multipoint queries (current + snapshots)
✅ **Snapshot** - Capture tree state

This matches the paper's API:
- `insert()` - ✅ Implemented
- `find()` - ✅ Implemented
- `erase()` - ✅ Implemented
- `range_query()` - ✅ Implemented
- `take_snapshot()` - ✅ Implemented

## Using Operations in the Simulator

### Basic Workflow

1. **Insert** some keys
2. **Take Snapshot** to capture state
3. **Insert/Erase** more keys
4. **Find** or **Range Query** on snapshot to see historical state
5. **Find** or **Range Query** on current to see latest state

### Demonstrating Paper Concepts

**Linearizability:**
- Take snapshot
- Insert keys
- Range query on snapshot → consistent results

**Historical Queries:**
- Insert keys
- Take snapshot
- Erase keys
- Find in snapshot → still finds erased keys!

**Versioning:**
- Insert with versioning enabled
- Check version chain information
- See how versions are created

## Summary

The simulator now includes **all key operations** from the paper:
- ✅ Insert (handles updates too)
- ✅ Find (point queries)
- ✅ Erase (delete)
- ✅ Range Query (multipoint queries)
- ✅ Snapshot (state capture)

These operations together demonstrate:
- **Versioning** - How nodes maintain multiple versions
- **Snapshots** - How historical states are captured
- **Linearizability** - How consistent queries are guaranteed
- **Concurrent Safety** - How operations don't interfere

This complete operation set makes the simulator a comprehensive demonstration of the paper's implementation!

