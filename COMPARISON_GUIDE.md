# Comparison Mode Guide

## Overview

The **Comparison Mode** demonstrates why the Multiversion B-Tree from the PACT 2022 paper is better than a regular B-Tree. This visualization helps you understand the improvements and design decisions made in the paper.

## How to Enable

Check the **"⚖️ Comparison Mode"** checkbox at the top of the application.

## What You'll See

### Side-by-Side Comparison

When Comparison Mode is enabled, you'll see:

1. **Multiversion B-Tree (Left)** - The paper's implementation
   - Shows all features: versioning, snapshots, version chains
   - Displays capabilities and advantages

2. **Regular B-Tree (Right)** - Traditional B-Tree
   - Shows limitations: no snapshots, no history
   - Highlights what it cannot do

### Key Improvements Demonstrated

#### 1. Historical Queries

**Problem Regular B-Tree Can't Solve:**
- Cannot query past states
- Once data is updated, old state is lost forever
- No way to compare current vs historical data

**Multiversion B-Tree Solution:**
- ✅ Can query any snapshot
- ✅ Preserves historical states
- ✅ Time-travel queries enabled

**How to Demonstrate:**
1. Insert keys: 10, 20, 30
2. Take a snapshot
3. Insert keys: 40, 50
4. Query the snapshot - see only original keys!
5. Regular B-Tree cannot do this!

#### 2. Concurrent Operations Safety

**Problem:**
- Regular B-Tree: Queries during updates can see inconsistent state
- Mixing of old and new data violates correctness

**Multiversion B-Tree Solution:**
- ✅ Linearizable operations
- ✅ Consistent snapshot views
- ✅ No interference between updates and queries

#### 3. Why Versioning?

The comparison shows three critical problems the paper solved:

1. **Concurrent Multipoint Queries**
   - Regular: Inconsistent range queries
   - Multiversion: Consistent via snapshots

2. **Historical Data Access**
   - Regular: Cannot access past states
   - Multiversion: Full history via snapshots

3. **GPU Database Requirements**
   - Regular: Not suitable for time-travel queries
   - Multiversion: Designed for GPU databases

## Comparison Table

The app shows a detailed comparison table with:

| Feature | Regular B-Tree | Multiversion B-Tree |
|---------|---------------|---------------------|
| Historical Queries | ❌ No | ✅ Yes |
| Snapshot Support | ❌ No | ✅ Yes |
| Linearizability | ❌ No guarantee | ✅ Guaranteed |
| Concurrent Safety | ⚠️ Limited | ✅ Safe |
| Time-Travel Queries | ❌ No | ✅ Yes |
| Memory Overhead | ✅ Low | ⚠️ Moderate |
| Update Speed (no snapshots) | ✅ Fast | ✅ Fast |
| Update Speed (with snapshots) | N/A | ⚠️ Slower |

## Key Insights

### Trade-offs

The multiversion B-Tree makes these trade-offs:

**Costs:**
- Higher memory usage (storing versions)
- Slower updates when snapshots are active (copy-on-write)

**Benefits:**
- ✅ Correctness (linearizable operations)
- ✅ Functionality (historical queries)
- ✅ Safety (concurrent operation guarantees)

### Why the Paper Chose This Design

1. **Correctness First**: Linearizability is critical for databases
2. **Functionality**: Historical queries are essential for analytics
3. **GPU Optimization**: Designed for GPU databases needing these features
4. **Memory Efficiency**: Only versions what's needed (lazy versioning)

## Demonstration Scenarios

### Scenario 1: Historical Analysis

**Use Case:** "What was the database state last week?"

- **Regular B-Tree**: ❌ Impossible - data is lost
- **Multiversion B-Tree**: ✅ Query snapshot from last week

### Scenario 2: Concurrent Operations

**Use Case:** Query while updates are happening

- **Regular B-Tree**: ⚠️ Might see inconsistent state
- **Multiversion B-Tree**: ✅ Consistent snapshot view

### Scenario 3: Time-Travel Queries

**Use Case:** Compare current state with past state

- **Regular B-Tree**: ❌ Cannot access past
- **Multiversion B-Tree**: ✅ Compare any two snapshots

## Paper's Motivation

From the paper:

> "The baseline GPU B-Tree structure provides no guarantees on the linearizability
> of concurrent range queries and updates."

The multiversion B-Tree solves this by:
- Using snapshots for consistent views
- Versioning nodes to preserve history
- Enabling linearizable multipoint queries

## Visual Learning

The comparison mode helps you understand:

1. **What problems exist** with regular B-Trees
2. **How the paper solved them** with versioning
3. **Why the design choices** were made
4. **What trade-offs** were accepted

## For Presentations

Use Comparison Mode to:

- Show clear advantages of multiversion approach
- Demonstrate real-world scenarios
- Explain design decisions
- Highlight paper's contributions

## Tips

1. **Enable both modes**: Use Education Mode + Comparison Mode together
2. **Follow scenarios**: Try the demonstration scenarios
3. **Compare metrics**: Look at the comparison table
4. **Read explanations**: Each tab explains a different advantage
5. **Experiment**: Insert keys, take snapshots, see the difference

