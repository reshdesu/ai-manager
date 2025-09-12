#!/usr/bin/env python3
"""
Self-Maintenance Script for AI Context Manager
The AI Context Manager maintains its own context using its own tools.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path


def maintain_self_context():
    """Maintain the AI Context Manager's own context using its own tools."""

    print(" AI Context Manager maintaining itself...")

    context_dir = Path("ai_context_self")

    if not context_dir.exists():
        print(" Self-hosted context not found. Run self_hosted_ai_context.py first.")
        return

    # 1. Check for changes in context files
    version_file = context_dir / "version_history.json"

    if version_file.exists():
        with open(version_file) as f:
            version_history = json.load(f)
    else:
        version_history = {"versions": [], "current_version": 0}

    # Get current file hashes
    current_hashes = {}
    changes_detected = False

    for file_path in context_dir.glob("*.json"):
        if file_path.name == "version_history.json":
            continue

        current_hash = get_file_hash(file_path)
        current_hashes[file_path.name] = current_hash

        # Check if file has changed
        last_version = (
            version_history["versions"][-1] if version_history["versions"] else {}
        )
        if (
            file_path.name not in last_version.get("file_hashes", {})
            or last_version["file_hashes"][file_path.name] != current_hash
        ):
            changes_detected = True

    # Create new version if changes detected
    if changes_detected:
        new_version = {
            "version": version_history["current_version"] + 1,
            "timestamp": datetime.now().isoformat(),
            "file_hashes": current_hashes,
            "project": "AI Context Manager",
            "changes": "Self-maintenance: Context files updated",
            "meta_note": "AI Context Manager maintaining its own context",
        }

        version_history["versions"].append(new_version)
        version_history["current_version"] = new_version["version"]

        with open(version_file, "w") as f:
            json.dump(version_history, f, indent=2)

        print(
            f" Version {new_version['version']} created - AI Context Manager updated its own context"
        )
    else:
        print(" No changes detected - AI Context Manager's context is up to date")

    # 2. Analyze learning patterns
    learning_file = context_dir / "learning_history.json"
    if learning_file.exists():
        with open(learning_file) as f:
            learning_data = json.load(f)

        # Count learning entries
        learnings = learning_data.get("conversation_learnings", {})
        print(
            f" AI Context Manager has documented {len(learnings)} development learnings"
        )

        # Show recent learnings
        recent_keys = list(learnings.keys())[-3:]
        print(" Recent development learnings:")
        for key in recent_keys:
            learning = learnings[key]
            print(f"  - {learning.get('issue', 'Unknown issue')}")

    # 3. Check file sizes and suggest optimizations
    large_files = []
    for file_path in context_dir.glob("*.json"):
        size = file_path.stat().st_size
        if size > 10000:  # 10KB
            large_files.append((file_path.name, size))

    if large_files:
        print("  Large context files detected:")
        for filename, size in large_files:
            print(f"  - {filename}: {size} bytes")
        print(" Consider splitting large files or optimizing content")
    else:
        print(" All context files are appropriately sized")

    # 4. Update maintenance log
    maintenance_log = {
        "last_maintenance": datetime.now().isoformat(),
        "maintained_by": "AI Context Manager (self)",
        "files_checked": len(list(context_dir.glob("*.json"))),
        "changes_detected": changes_detected,
        "version": version_history["current_version"],
        "meta_note": "AI Context Manager successfully maintained its own context",
    }

    log_file = context_dir / "maintenance_log.json"
    with open(log_file, "w") as f:
        json.dump(maintenance_log, f, indent=2)

    print(f" Self-maintenance completed - Version {version_history['current_version']}")
    print(" AI Context Manager successfully maintained itself!")


def get_file_hash(file_path):
    """Get MD5 hash of a file."""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def demonstrate_meta_maintenance():
    """Demonstrate the meta-nature of self-maintenance."""

    print("\n" + "=" * 70)
    print("META-MAINTENANCE DEMONSTRATION")
    print("=" * 70)
    print("The AI Context Manager just maintained its own context!")
    print()
    print("This demonstrates:")
    print(" Self-referential maintenance - the system maintains itself")
    print(" Version control - tracks changes to its own context")
    print(" Learning analysis - analyzes its own development patterns")
    print(" Optimization suggestions - suggests improvements to itself")
    print(" Maintenance logging - logs its own maintenance activities")
    print()
    print("Meta-meta-meta: The AI Context Manager maintained the context")
    print("for developing the AI Context Manager that maintains context!")
    print("=" * 70)


if __name__ == "__main__":
    maintain_self_context()
    demonstrate_meta_maintenance()
