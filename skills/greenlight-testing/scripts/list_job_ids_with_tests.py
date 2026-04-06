#!/usr/bin/env python3
"""
List Job IDs with Agent Tests
Utility to track and list test job IDs.
"""

import subprocess
import json
import sys
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime


# Local history file for tracking job IDs
HISTORY_FILE = os.path.expanduser("~/.greenlight-job-history.json")


def get_org_info(org_alias: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Get org information.
    
    Args:
        org_alias: Org alias
        
    Returns:
        Tuple of (org_info, error_message)
    """
    try:
        result = subprocess.run(
            ['sf', 'org', 'display', '--target-org', org_alias, '--json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return None, f"Failed to get org info: {result.stderr}"
        
        data = json.loads(result.stdout)
        
        if data.get('status') == 0:
            return data.get('result', {}), None
        
        return None, data.get('message', 'Unknown error')
        
    except Exception as e:
        return None, f"Error: {e}"


def load_job_history() -> List[Dict]:
    """Load job history from local file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []


def save_job_history(history: List[Dict]) -> None:
    """Save job history to local file."""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save history: {e}")


def add_job_to_history(test_api_name: str, job_id: str, org_alias: str) -> None:
    """Add a job to the history."""
    history = load_job_history()
    
    history.append({
        'test_api_name': test_api_name,
        'job_id': job_id,
        'org_alias': org_alias,
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last 100 entries
    if len(history) > 100:
        history = history[-100:]
    
    save_job_history(history)


def list_jobs_for_org(org_alias: str) -> List[Dict]:
    """Get jobs for a specific org from history."""
    history = load_job_history()
    return [j for j in history if j.get('org_alias') == org_alias]


def print_job_history(org_alias: str) -> None:
    """Print job history for an org."""
    jobs = list_jobs_for_org(org_alias)
    
    if not jobs:
        print(f"\nNo job history found for org: {org_alias}")
        print("Jobs are tracked when you run tests using this skill.")
        return
    
    print(f"\nJob History for: {org_alias}")
    print("-" * 80)
    print(f"{'Test API Name':<30} {'Job ID':<25} {'Timestamp':<25}")
    print("-" * 80)
    
    for job in reversed(jobs[-20:]):  # Show last 20
        test_name = job.get('test_api_name', 'Unknown')[:29]
        job_id = job.get('job_id', 'Unknown')[:24]
        timestamp = job.get('timestamp', '')[:24]
        print(f"{test_name:<30} {job_id:<25} {timestamp:<25}")
    
    print("-" * 80)
    print(f"Showing last {min(20, len(jobs))} of {len(jobs)} jobs")


def main():
    if len(sys.argv) < 2:
        print("Usage: python list_job_ids_with_tests.py <org_alias>")
        print("Example: python list_job_ids_with_tests.py my-org")
        sys.exit(1)
    
    org_alias = sys.argv[1]
    
    # Verify org connection
    org_info, error = get_org_info(org_alias)
    
    if error:
        print(f"Error connecting to org: {error}")
        sys.exit(1)
    
    print(f"Org: {org_alias}")
    print(f"Username: {org_info.get('username', 'Unknown')}")
    
    print_job_history(org_alias)


if __name__ == "__main__":
    main()
