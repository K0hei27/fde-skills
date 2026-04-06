#!/usr/bin/env python3
"""
List Agentforce Agents
Lists available agents in a Salesforce org.
"""

import subprocess
import json
import sys
from typing import List, Dict, Tuple, Optional


def run_sf_command(cmd: List[str], org_alias: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Run a Salesforce CLI command and return parsed JSON result.
    
    Args:
        cmd: Command parts (without --target-org)
        org_alias: Org alias to run against
        
    Returns:
        Tuple of (result_dict, error_message)
    """
    full_cmd = cmd + ['--target-org', org_alias, '--json']
    
    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return None, f"Command failed: {result.stderr}"
        
        data = json.loads(result.stdout)
        return data, None
        
    except subprocess.TimeoutExpired:
        return None, "Command timed out"
    except json.JSONDecodeError as e:
        return None, f"Failed to parse JSON: {e}"
    except Exception as e:
        return None, f"Error: {e}"


def list_agents(org_alias: str) -> Tuple[List[Dict], Optional[str]]:
    """
    List all agents (BotDefinition) in the org.
    
    Args:
        org_alias: Org alias
        
    Returns:
        Tuple of (list of agents, error_message)
    """
    data, error = run_sf_command(
        ['sf', 'data', 'query', '--query', 
         'SELECT Id, DeveloperName, MasterLabel FROM BotDefinition'],
        org_alias
    )
    
    if error:
        return [], error
    
    if data.get('status') != 0:
        return [], data.get('message', 'Query failed')
    
    records = data.get('result', {}).get('records', [])
    
    agents = []
    for record in records:
        agents.append({
            'id': record.get('Id', ''),
            'api_name': record.get('DeveloperName', ''),
            'label': record.get('MasterLabel', '')
        })
    
    return agents, None


def list_agent_tests(org_alias: str) -> Tuple[List[Dict], Optional[str]]:
    """
    List all agent tests in the org.
    
    Args:
        org_alias: Org alias
        
    Returns:
        Tuple of (list of tests, error_message)
    """
    data, error = run_sf_command(
        ['sf', 'agent', 'test', 'list'],
        org_alias
    )
    
    if error:
        return [], error
    
    # sf agent test list returns array directly in result
    tests = data.get('result', [])
    
    return tests, None


def print_agents(agents: List[Dict]) -> None:
    """Print agents in a formatted table."""
    if not agents:
        print("No agents found.")
        return
    
    print("\nAvailable Agents:")
    print("-" * 60)
    print(f"{'#':<4} {'Label':<30} {'API Name':<25}")
    print("-" * 60)
    
    for i, agent in enumerate(agents, 1):
        label = agent.get('label', 'Unknown')[:29]
        api_name = agent.get('api_name', 'Unknown')[:24]
        print(f"{i:<4} {label:<30} {api_name:<25}")
    
    print("-" * 60)
    print(f"Total: {len(agents)} agent(s)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python list_agents.py <org_alias>")
        print("Example: python list_agents.py my-org")
        sys.exit(1)
    
    org_alias = sys.argv[1]
    
    print(f"Querying agents from: {org_alias}")
    
    agents, error = list_agents(org_alias)
    
    if error:
        print(f"Error: {error}")
        sys.exit(1)
    
    print_agents(agents)


if __name__ == "__main__":
    main()
