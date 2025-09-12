#!/usr/bin/env python3
"""
Pre-commit hook to validate self-hosting functionality.
This ensures the AI Context Manager can maintain its own context.
"""

import json
import sys
from pathlib import Path


def validate_self_hosting():
    """Validate that self-hosting functionality is working."""

    print("Validating AI Context Manager self-hosting...")

    # Check if self-maintenance script exists and works
    self_maintenance_script = Path("self_maintenance.py")
    if not self_maintenance_script.exists():
        print("ERROR: Self-maintenance script not found!")
        return False

    # Check if self-hosted context creation script exists
    self_context_script = Path("self_hosted_ai_context.py")
    if not self_context_script.exists():
        print("ERROR: Self-hosted context creation script not found!")
        return False

    # Validate self-hosted context structure
    self_context_dir = Path("ai_context_self")
    if not self_context_dir.exists():
        print("ERROR: Self-hosted context directory not found!")
        print("Run: python3 self_hosted_ai_context.py")
        return False

    # Check if context files are properly structured
    core_file = self_context_dir / "core.json"
    if core_file.exists():
        try:
            with open(core_file) as f:
                core_data = json.load(f)

            # Check for self-hosting indicators
            ai_context = core_data.get("ai_context", {})
            if not ai_context.get("self_hosted"):
                print("ERROR: Self-hosting not properly configured!")
                return False

            if (
                ai_context.get("meta_context")
                != "This AI context system is used to develop itself - ultimate dogfooding"
            ):
                print("WARNING: Meta-context not properly set for self-hosting")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"ERROR: Invalid self-hosted core.json: {e}")
            return False

    # Check for self-hosting rules in core.json
    try:
        with open(core_file) as f:
            core_data = json.load(f)

        ai_assistant_rules = core_data.get("ai_assistant_rules", {})
        self_hosting_rules = ai_assistant_rules.get("self_hosting_rules", [])

        if len(self_hosting_rules) == 0:
            print("ERROR: No self-hosting rules found!")
            return False

        required_rules = [
            "Always use the AI Context Manager's own context when developing it",
            "Test new features by using them on this project first",
            "Validate that the system works by using it on itself",
        ]

        for required_rule in required_rules:
            if not any(required_rule in rule for rule in self_hosting_rules):
                print(f"WARNING: Missing self-hosting rule: {required_rule}")

    except (json.JSONDecodeError, KeyError) as e:
        print(f"ERROR: Cannot validate self-hosting rules: {e}")
        return False

    print("Self-hosting validation passed!")
    return True


def check_self_maintenance_capability():
    """Check if the system can maintain itself."""

    print("Checking self-maintenance capability...")

    # Check if maintenance log exists
    maintenance_log = Path("ai_context_self/maintenance_log.json")
    if maintenance_log.exists():
        try:
            with open(maintenance_log) as f:
                log_data = json.load(f)

            last_maintenance = log_data.get("last_maintenance")
            if last_maintenance:
                print(f"Last self-maintenance: {last_maintenance}")
            else:
                print("WARNING: No maintenance history found")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"WARNING: Invalid maintenance log: {e}")

    # Check version history
    version_history = Path("ai_context_self/version_history.json")
    if version_history.exists():
        try:
            with open(version_history) as f:
                version_data = json.load(f)

            current_version = version_data.get("current_version", 0)
            versions = version_data.get("versions", [])

            print(f"Current version: {current_version}")
            print(f"Version history: {len(versions)} entries")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"WARNING: Invalid version history: {e}")

    print("Self-maintenance capability validated!")
    return True


def main():
    """Main function for self-hosting validation."""

    print("=" * 60)
    print("AI CONTEXT MANAGER SELF-HOSTING VALIDATION")
    print("=" * 60)

    # Validate self-hosting
    self_hosting_valid = validate_self_hosting()

    # Check self-maintenance capability
    maintenance_valid = check_self_maintenance_capability()

    print("=" * 60)

    if self_hosting_valid and maintenance_valid:
        print("SUCCESS: Self-hosting functionality is properly configured!")
        print("The AI Context Manager can maintain its own context.")
        return 0
    else:
        print("FAILURE: Self-hosting validation failed!")
        print()
        print("To fix:")
        print("1. Ensure self_hosted_ai_context.py exists and works")
        print("2. Run: python3 self_hosted_ai_context.py")
        print("3. Run: python3 self_maintenance.py")
        print("4. Verify self-hosting rules in ai_context_self/core.json")
        return 1


if __name__ == "__main__":
    sys.exit(main())
