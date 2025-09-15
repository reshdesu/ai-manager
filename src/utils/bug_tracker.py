#!/usr/bin/env python3
"""
Bug Tracking System - Bug Information Only
Simple bug logging and tracking system
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class BugTracker:
    def __init__(self, log_file: str = "logs/bug_tracker.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
        self.bugs = self.load_bugs()
        
    def load_bugs(self) -> List[Dict[str, Any]]:
        """Load existing bug log"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_bugs(self):
        """Save bug log to file"""
        with open(self.log_file, 'w') as f:
            json.dump(self.bugs, f, indent=2)
    
    def log_bug(self, bug_type: str, description: str, severity: str = "medium", 
                component: str = "unknown", fix_time_minutes: float = 0):
        """Log a new bug"""
        bug = {
            "id": f"bug_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "bug_type": bug_type,
            "description": description,
            "severity": severity,
            "component": component,
            "fix_time_minutes": fix_time_minutes,
            "status": "fixed"
        }
        self.bugs.append(bug)
        self.save_bugs()
        return bug["id"]
    
    def get_bug_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get bug statistics for the last N hours"""
        cutoff_time = time.time() - (hours * 3600)
        
        recent_bugs = [
            bug for bug in self.bugs 
            if time.mktime(datetime.fromisoformat(bug["timestamp"]).timetuple()) > cutoff_time
        ]
        
        if not recent_bugs:
            return {
                "total_bugs": 0,
                "bugs_per_hour": 0,
                "avg_fix_time": 0,
                "severity_breakdown": {},
                "component_breakdown": {},
                "bug_types": {}
            }
        
        total_bugs = len(recent_bugs)
        bugs_per_hour = total_bugs / hours
        
        fix_times = [bug["fix_time_minutes"] for bug in recent_bugs if bug["fix_time_minutes"] > 0]
        avg_fix_time = sum(fix_times) / len(fix_times) if fix_times else 0
        
        severity_breakdown = {}
        for bug in recent_bugs:
            severity = bug["severity"]
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
        
        component_breakdown = {}
        for bug in recent_bugs:
            component = bug["component"]
            component_breakdown[component] = component_breakdown.get(component, 0) + 1
        
        bug_types = {}
        for bug in recent_bugs:
            bug_type = bug["bug_type"]
            bug_types[bug_type] = bug_types.get(bug_type, 0) + 1
        
        return {
            "total_bugs": total_bugs,
            "bugs_per_hour": bugs_per_hour,
            "avg_fix_time": avg_fix_time,
            "severity_breakdown": severity_breakdown,
            "component_breakdown": component_breakdown,
            "bug_types": bug_types,
            "hours_analyzed": hours
        }
    
    def print_report(self, hours: int = 24):
        """Print a formatted bug report"""
        stats = self.get_bug_stats(hours)
        
        print(f"\n{'='*60}")
        print(f"BUG TRACKING REPORT - Last {hours} hours")
        print(f"{'='*60}")
        
        print(f"Total Bugs: {stats['total_bugs']}")
        print(f"Bugs per Hour: {stats['bugs_per_hour']:.2f}")
        print(f"Average Fix Time: {stats['avg_fix_time']:.1f} minutes")
        
        print(f"\nSeverity Breakdown:")
        for severity, count in stats['severity_breakdown'].items():
            print(f"  {severity.capitalize()}: {count}")
        
        print(f"\nComponent Breakdown:")
        for component, count in stats['component_breakdown'].items():
            print(f"  {component}: {count}")
        
        print(f"\nBug Types:")
        for bug_type, count in stats['bug_types'].items():
            print(f"  {bug_type}: {count}")
        
        print(f"{'='*60}\n")
    
    def list_recent_bugs(self, hours: int = 24):
        """List recent bugs with details"""
        cutoff_time = time.time() - (hours * 3600)
        
        recent_bugs = [
            bug for bug in self.bugs 
            if time.mktime(datetime.fromisoformat(bug["timestamp"]).timetuple()) > cutoff_time
        ]
        
        print(f"\n{'='*80}")
        print(f"RECENT BUGS - Last {hours} hours")
        print(f"{'='*80}")
        
        for bug in recent_bugs:
            print(f"\nID: {bug['id']}")
            print(f"Time: {bug['timestamp']}")
            print(f"Type: {bug['bug_type']}")
            print(f"Severity: {bug['severity']}")
            print(f"Component: {bug['component']}")
            print(f"Description: {bug['description']}")
            print(f"Fix Time: {bug['fix_time_minutes']} minutes")
            print(f"Status: {bug['status']}")
            print("-" * 40)

# Global bug tracker instance
bug_tracker = BugTracker()

def log_bug(bug_type: str, description: str, severity: str = "medium", 
            component: str = "unknown", fix_time_minutes: float = 0):
    """Convenience function to log bugs"""
    return bug_tracker.log_bug(bug_type, description, severity, component, fix_time_minutes)

def get_bug_report(hours: int = 24):
    """Convenience function to get bug report"""
    bug_tracker.print_report(hours)

def list_bugs(hours: int = 24):
    """Convenience function to list recent bugs"""
    bug_tracker.list_recent_bugs(hours)

if __name__ == "__main__":
    bug_tracker.print_report(24)