#!/usr/bin/env python3
"""
Org Selector - Helper for selecting Salesforce orgs
Returns data for the Cursor agent to present via AskQuestion tool.
Does NOT prompt users directly - all interaction happens through the agent.
"""

import json
import subprocess
import sys
from typing import List, Dict, Optional, Tuple


def get_available_orgs() -> Tuple[List[Dict], Optional[str]]:
    """
    Get list of authenticated Salesforce orgs.
    
    Returns:
        Tuple of (list of org dictionaries, error message or None)
        
    Each org dict contains:
        - alias: Org alias or username
        - username: Full username
        - orgId: Salesforce org ID
        - instanceUrl: Instance URL
        - type: 'Production/Sandbox' or 'Scratch Org'
        - isDefault: Whether this is the default org
    """
    try:
        result = subprocess.run(
            ['sf', 'org', 'list', '--json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return [], f"sf org list failed: {result.stderr}"
        
        data = json.loads(result.stdout)
        
        if data.get('status') != 0:
            return [], f"sf org list returned error status: {data.get('message', 'Unknown error')}"
        
        orgs = []
        
        # Add non-scratch orgs (Production/Sandbox)
        non_scratch = data.get('result', {}).get('nonScratchOrgs', [])
        for org in non_scratch:
            orgs.append({
                'alias': org.get('alias') or org.get('username', 'Unknown'),
                'username': org.get('username', ''),
                'orgId': org.get('orgId', ''),
                'instanceUrl': org.get('instanceUrl', ''),
                'type': 'Production/Sandbox',
                'isDefault': org.get('isDefaultUsername', False),
                'isDevHub': org.get('isDefaultDevHubUsername', False)
            })
        
        # Add scratch orgs
        scratch = data.get('result', {}).get('scratchOrgs', [])
        for org in scratch:
            orgs.append({
                'alias': org.get('alias') or org.get('username', 'Unknown'),
                'username': org.get('username', ''),
                'orgId': org.get('orgId', ''),
                'instanceUrl': org.get('instanceUrl', ''),
                'type': 'Scratch Org',
                'expirationDate': org.get('expirationDate', ''),
                'isDefault': org.get('isDefaultUsername', False),
                'isDevHub': False
            })
        
        return orgs, None
        
    except subprocess.TimeoutExpired:
        return [], "sf org list timed out after 30 seconds"
    except json.JSONDecodeError as e:
        return [], f"Failed to parse sf org list output: {e}"
    except FileNotFoundError:
        return [], "Salesforce CLI (sf) not found. Please install it first."
    except Exception as e:
        return [], f"Unexpected error: {e}"


def format_orgs_for_display(orgs: List[Dict]) -> List[Dict]:
    """
    Format orgs for display in AskQuestion options.
    
    Args:
        orgs: List of org dictionaries from get_available_orgs()
        
    Returns:
        List of option dictionaries with 'id' and 'label' keys
    """
    options = []
    for org in orgs:
        alias = org.get('alias', 'Unknown')
        username = org.get('username', '')
        org_type = org.get('type', '')
        is_default = org.get('isDefault', False)
        
        # Build label
        label = f"{alias}"
        if username and username != alias:
            label += f" ({username})"
        if org_type:
            label += f" - {org_type}"
        if is_default:
            label += " [DEFAULT]"
        
        options.append({
            'id': alias,
            'label': label
        })
    
    return options


def get_org_info(org_alias: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Get detailed info about a specific org.
    
    Args:
        org_alias: Org alias or username
        
    Returns:
        Tuple of (org info dict, error message or None)
    """
    try:
        result = subprocess.run(
            ['sf', 'org', 'display', '--target-org', org_alias, '--json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return None, f"sf org display failed: {result.stderr}"
        
        data = json.loads(result.stdout)
        
        if data.get('status') == 0 and 'result' in data:
            return data['result'], None
        
        return None, f"sf org display returned error: {data.get('message', 'Unknown error')}"
        
    except subprocess.TimeoutExpired:
        return None, "sf org display timed out"
    except json.JSONDecodeError as e:
        return None, f"Failed to parse output: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


def get_default_org(orgs: List[Dict]) -> Optional[str]:
    """
    Find the default org from a list of orgs.
    
    Args:
        orgs: List of org dictionaries
        
    Returns:
        Alias of the default org, or None if no default
    """
    for org in orgs:
        if org.get('isDefault'):
            return org.get('alias')
    return None


def validate_org_connection(org_alias: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that we can connect to the specified org.
    
    Args:
        org_alias: Org alias to validate
        
    Returns:
        Tuple of (success boolean, error message or None)
    """
    info, error = get_org_info(org_alias)
    if error:
        return False, error
    if info:
        return True, None
    return False, "Could not retrieve org information"


# Convenience function for agent to get org data
def get_org_selection_data() -> Dict:
    """
    Get all data needed for org selection.
    Returns a dictionary that the agent can use to present options.
    
    Returns:
        {
            'success': bool,
            'orgs': List of org dicts,
            'options': List of formatted options for AskQuestion,
            'default_org': Alias of default org or None,
            'error': Error message or None
        }
    """
    orgs, error = get_available_orgs()
    
    if error:
        return {
            'success': False,
            'orgs': [],
            'options': [],
            'default_org': None,
            'error': error
        }
    
    if not orgs:
        return {
            'success': False,
            'orgs': [],
            'options': [],
            'default_org': None,
            'error': 'No authenticated orgs found. Run: sf org login web --alias my-org'
        }
    
    return {
        'success': True,
        'orgs': orgs,
        'options': format_orgs_for_display(orgs),
        'default_org': get_default_org(orgs),
        'error': None
    }


if __name__ == "__main__":
    # Test the functions
    print("Testing org selector...")
    data = get_org_selection_data()
    print(json.dumps(data, indent=2))
