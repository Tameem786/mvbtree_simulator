#!/usr/bin/env python3
"""
CLI interface for the Multiversion B-Tree Simulator.

This provides a simple command-line interface to test the basic functionality
of the multiversion B-Tree implementation.
"""

from features.base import MultiversionBTree


def print_menu():
    """Print the main menu."""
    print("\n" + "="*50)
    print("Multiversion B-Tree Simulator")
    print("="*50)
    print("1. Insert key-value pair")
    print("2. Find key")
    print("3. Take snapshot")
    print("4. Find key in snapshot")
    print("5. List all keys")
    print("6. List all keys in snapshot")
    print("7. Print tree structure")
    print("8. Print tree structure at snapshot")
    print("9. Show snapshots")
    print("0. Exit")
    print("="*50)


def main():
    """Main CLI loop."""
    tree = MultiversionBTree(branching_factor=4)
    
    print("Multiversion B-Tree Simulator")
    print("Initialized with branching factor: 4")
    print("\nNote: This is a simplified implementation for demonstration.")
    
    while True:
        print_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        
        elif choice == "1":
            try:
                key = int(input("Enter key (integer): "))
                value = int(input("Enter value (integer): "))
                success = tree.insert(key, value)
                if success:
                    print(f"✓ Inserted key={key}, value={value}")
                else:
                    print(f"✗ Failed to insert key={key}")
            except ValueError:
                print("✗ Invalid input. Please enter integers.")
        
        elif choice == "2":
            try:
                key = int(input("Enter key to find: "))
                value = tree.find(key)
                if value is not None:
                    print(f"✓ Found key={key}, value={value}")
                else:
                    print(f"✗ Key {key} not found")
            except ValueError:
                print("✗ Invalid input. Please enter an integer.")
        
        elif choice == "3":
            snapshot_id = tree.take_snapshot()
            print(f"✓ Snapshot #{snapshot_id} created (timestamp: {tree.snapshots[snapshot_id]})")
        
        elif choice == "4":
            try:
                snapshot_id = int(input("Enter snapshot ID: "))
                key = int(input("Enter key to find: "))
                value = tree.find(key, snapshot_id=snapshot_id)
                if value is not None:
                    print(f"✓ Found key={key}, value={value} in snapshot #{snapshot_id}")
                else:
                    print(f"✗ Key {key} not found in snapshot #{snapshot_id}")
            except ValueError:
                print("✗ Invalid input. Please enter integers.")
            except KeyError:
                print(f"✗ Snapshot #{snapshot_id} does not exist")
        
        elif choice == "5":
            keys = tree.get_all_keys()
            if keys:
                print(f"✓ All keys (current state): {sorted(set(keys))}")
            else:
                print("(empty tree)")
        
        elif choice == "6":
            try:
                snapshot_id = int(input("Enter snapshot ID: "))
                keys = tree.get_all_keys(snapshot_id=snapshot_id)
                if keys:
                    print(f"✓ All keys in snapshot #{snapshot_id}: {sorted(set(keys))}")
                else:
                    print(f"(empty tree at snapshot #{snapshot_id})")
            except ValueError:
                print("✗ Invalid input. Please enter an integer.")
            except KeyError:
                print(f"✗ Snapshot #{snapshot_id} does not exist")
        
        elif choice == "7":
            print("\nTree structure (current state):")
            tree.print_tree()
        
        elif choice == "8":
            try:
                snapshot_id = int(input("Enter snapshot ID: "))
                print(f"\nTree structure at snapshot #{snapshot_id}:")
                tree.print_tree(snapshot_id=snapshot_id)
            except ValueError:
                print("✗ Invalid input. Please enter an integer.")
            except KeyError:
                print(f"✗ Snapshot #{snapshot_id} does not exist")
        
        elif choice == "9":
            if tree.snapshots:
                print("Snapshots:")
                for snap_id, timestamp in tree.snapshots.items():
                    print(f"  Snapshot #{snap_id}: timestamp {timestamp}")
            else:
                print("No snapshots taken yet.")
        
        else:
            print("✗ Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

