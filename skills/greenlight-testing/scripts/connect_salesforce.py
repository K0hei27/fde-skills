#!/usr/bin/env python3
"""
Salesforce Connection Helper
Provides utilities for connecting to Salesforce orgs.
NOTE: This script is for reference only. The skill uses sf CLI directly.
"""

import subprocess
import json
import sys
from typing import Optional, Dict, Tuple


def get_sf_access_token(org_alias: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get access token for an authenticated org using sf CLI.
    
    Args:
        org_alias: The org alias or username
        
    Returns:
        Tuple of (access_token, error_message)
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
        
        if data.get('status') == 0 and 'result' in data:
            return data['result'].get('accessToken'), None
        
        return None, "Could not extract access token"
        
    except subprocess.TimeoutExpired:
        return None, "Command timed out"
    except json.JSONDecodeError as e:
        return None, f"Failed to parse response: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


def get_org_instance_url(org_alias: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get instance URL for an authenticated org.
    
    Args:
        org_alias: The org alias or username
        
    Returns:
        Tuple of (instance_url, error_message)
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
        
        if data.get('status') == 0 and 'result' in data:
            return data['result'].get('instanceUrl'), None
        
        return None, "Could not extract instance URL"
        
    except Exception as e:
        return None, f"Error: {e}"


def verify_org_connection(org_alias: str) -> Tuple[bool, Optional[str]]:
    """
    Verify that we can connect to the specified org.
    
    Args:
        org_alias: The org alias or username
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        result = subprocess.run(
            ['sf', 'org', 'display', '--target-org', org_alias, '--json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return False, f"Connection failed: {result.stderr}"
        
        data = json.loads(result.stdout)
        
        if data.get('status') == 0:
            return True, None
        
        return False, data.get('message', 'Unknown error')
        
    except Exception as e:
        return False, f"Error: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python connect_salesforce.py <org_alias>")
        print("Example: python connect_salesforce.py my-org")
        sys.exit(1)
    
    org_alias = sys.argv[1]
    
    print(f"Verifying connection to: {org_alias}")
    success, error = verify_org_connection(org_alias)
    
    if success:
        print(f"Connected to {org_alias}")
        
        instance_url, _ = get_org_instance_url(org_alias)
        if instance_url:
            print(f"Instance URL: {instance_url}")
    else:
        print(f"Connection failed: {error}")
        sys.exit(1)
