#!/usr/bin/env python3
"""
Agent Metadata Extractor
Extracts agent metadata including topics, actions, and versions.
Returns data for the Cursor agent to present via AskQuestion tool.
Does NOT prompt users directly - all interaction happens through the agent.
"""

import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TopicInfo:
    """Represents an agent topic"""
    name: str
    description: str
    utterances: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ActionInfo:
    """Represents an agent action"""
    name: str
    type: str
    description: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AgentVersion:
    """Represents an agent version"""
    id: str
    version_number: str
    status: str
    is_active: bool
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AgentMetadata:
    """Complete agent metadata"""
    api_name: str
    label: str
    description: str
    topics: List[TopicInfo]
    actions: List[ActionInfo]
    versions: List[AgentVersion]
    
    def to_dict(self) -> Dict:
        return {
            'api_name': self.api_name,
            'label': self.label,
            'description': self.description,
            'topics': [t.to_dict() for t in self.topics],
            'actions': [a.to_dict() for a in self.actions],
            'versions': [v.to_dict() for v in self.versions]
        }


def query_agents(org_alias: str) -> Tuple[List[Dict], Optional[str]]:
    """
    Query available agents from the org.
    
    Args:
        org_alias: Salesforce org alias
        
    Returns:
        Tuple of (list of agent dicts, error message or None)
    """
    try:
        result = subprocess.run(
            ['sf', 'data', 'query',
             '--query', 'SELECT Id, DeveloperName, MasterLabel FROM BotDefinition',
             '--target-org', org_alias,
             '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return [], f"Query failed: {result.stderr}"
        
        data = json.loads(result.stdout)
        
        if data.get('status') != 0:
            return [], f"Query error: {data.get('message', 'Unknown')}"
        
        records = data.get('result', {}).get('records', [])
        
        agents = []
        for record in records:
            agents.append({
                'id': record.get('Id', ''),
                'api_name': record.get('DeveloperName', ''),
                'label': record.get('MasterLabel', ''),
            })
        
        return agents, None
        
    except subprocess.TimeoutExpired:
        return [], "Query timed out"
    except json.JSONDecodeError as e:
        return [], f"Failed to parse response: {e}"
    except Exception as e:
        return [], f"Unexpected error: {e}"


def query_agent_versions(org_alias: str, agent_api_name: str) -> Tuple[List[AgentVersion], Optional[str]]:
    """
    Query available versions for an agent.
    
    Args:
        org_alias: Salesforce org alias
        agent_api_name: Agent API name (DeveloperName)
        
    Returns:
        Tuple of (list of AgentVersion, error message or None)
    """
    try:
        query = f"SELECT Id, VersionNumber, Status FROM BotVersion WHERE BotDefinition.DeveloperName = '{agent_api_name}' ORDER BY VersionNumber DESC"
        
        result = subprocess.run(
            ['sf', 'data', 'query',
             '--query', query,
             '--target-org', org_alias,
             '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return [], f"Query failed: {result.stderr}"
        
        data = json.loads(result.stdout)
        
        if data.get('status') != 0:
            return [], f"Query error: {data.get('message', 'Unknown')}"
        
        records = data.get('result', {}).get('records', [])
        
        versions = []
        for record in records:
            status = record.get('Status', '')
            versions.append(AgentVersion(
                id=record.get('Id', ''),
                version_number=record.get('VersionNumber', ''),
                status=status,
                is_active=(status == 'Active')
            ))
        
        return versions, None
        
    except subprocess.TimeoutExpired:
        return [], "Query timed out"
    except json.JSONDecodeError as e:
        return [], f"Failed to parse response: {e}"
    except Exception as e:
        return [], f"Unexpected error: {e}"


def format_agents_for_display(agents: List[Dict]) -> List[Dict]:
    """
    Format agents for display in AskQuestion options.
    
    Args:
        agents: List of agent dictionaries
        
    Returns:
        List of option dictionaries with 'id' and 'label' keys
    """
    options = []
    for agent in agents:
        api_name = agent.get('api_name', 'Unknown')
        label = agent.get('label', api_name)
        
        options.append({
            'id': api_name,
            'label': f"{label} ({api_name})"
        })
    
    return options


def format_versions_for_display(versions: List[AgentVersion]) -> List[Dict]:
    """
    Format versions for display in AskQuestion options.
    
    Args:
        versions: List of AgentVersion objects
        
    Returns:
        List of option dictionaries with 'id' and 'label' keys
    """
    options = []
    for version in versions:
        label = f"v{version.version_number}"
        if version.is_active:
            label += " - ACTIVE (recommended)"
        else:
            label += f" - {version.status}"
        
        options.append({
            'id': f"v{version.version_number}",
            'label': label
        })
    
    return options


def get_active_version(versions: List[AgentVersion]) -> Optional[str]:
    """
    Get the active version from a list of versions.
    
    Args:
        versions: List of AgentVersion objects
        
    Returns:
        Version string (e.g., 'v2') of active version, or None
    """
    for version in versions:
        if version.is_active:
            return f"v{version.version_number}"
    return None


def retrieve_agent_metadata(org_alias: str, agent_name: str, version: str = None) -> Tuple[bool, Optional[str]]:
    """
    Retrieve agent metadata files from org.
    
    Args:
        org_alias: Salesforce org alias
        agent_name: Agent API name
        version: Version suffix (e.g., 'v2'). If None, retrieves bot only.
        
    Returns:
        Tuple of (success boolean, error message or None)
    """
    try:
        # Retrieve bot definition
        result = subprocess.run(
            ['sf', 'project', 'retrieve', 'start',
             '--metadata', f'Bot:{agent_name}',
             '--target-org', org_alias],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            return False, f"Failed to retrieve Bot: {result.stderr}"
        
        # Retrieve GenAiPlannerBundle if version specified
        if version:
            bundle_name = f"{agent_name}_{version}"
            result = subprocess.run(
                ['sf', 'project', 'retrieve', 'start',
                 '--metadata', f'GenAiPlannerBundle:{bundle_name}',
                 '--target-org', org_alias],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                return False, f"Failed to retrieve GenAiPlannerBundle: {result.stderr}"
        
        return True, None
        
    except subprocess.TimeoutExpired:
        return False, "Metadata retrieval timed out"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def parse_bot_metadata(bot_file: Path) -> Dict:
    """Parse Bot metadata XML file"""
    try:
        tree = ET.parse(bot_file)
        root = tree.getroot()
        
        ns = '{http://soap.sforce.com/2006/04/metadata}'
        
        return {
            'api_name': root.findtext(f'.//{ns}fullName', ''),
            'label': root.findtext(f'.//{ns}label', ''),
            'description': root.findtext(f'.//{ns}description', ''),
        }
    except Exception as e:
        return {'error': str(e)}


def parse_genai_bundle(bundle_file: Path) -> Dict:
    """Parse GenAiPlannerBundle XML file"""
    try:
        tree = ET.parse(bundle_file)
        root = tree.getroot()
        
        ns = '{http://soap.sforce.com/2006/04/metadata}'
        
        bundle_info = {
            'topics': [],
            'actions': [],
            'description': root.findtext(f'.//{ns}description', ''),
        }
        
        # Extract local topics
        for topic in root.findall(f'.//{ns}localTopics'):
            topic_name = topic.findtext(f'.//{ns}localDeveloperName', '') or topic.findtext(f'.//{ns}developerName', '')
            topic_desc = topic.findtext(f'.//{ns}description', '')
            
            # Extract utterances
            utterances = []
            for utterance in topic.findall(f'.//{ns}utterance'):
                if utterance.text:
                    utterances.append(utterance.text)
            
            if topic_name:
                bundle_info['topics'].append({
                    'name': topic_name,
                    'description': topic_desc,
                    'utterances': utterances
                })
        
        # Extract local action links
        for action_link in root.findall(f'.//{ns}localActionLinks'):
            action_name = action_link.findtext(f'.//{ns}genAiFunctionName', '')
            if action_name:
                bundle_info['actions'].append({
                    'name': action_name,
                    'type': 'localAction',
                    'description': ''
                })
        
        # Extract referenced topics (localTopicLinks)
        for topic_link in root.findall(f'.//{ns}localTopicLinks'):
            topic_name = topic_link.findtext(f'.//{ns}genAiPluginName', '')
            if topic_name:
                bundle_info['topics'].append({
                    'name': topic_name,
                    'description': 'Referenced topic',
                    'utterances': []
                })
        
        return bundle_info
    except Exception as e:
        return {'error': str(e)}


def extract_metadata_from_files(agent_name: str, version: str = None, base_path: str = "force-app/main/default") -> Tuple[Optional[AgentMetadata], Optional[str]]:
    """
    Extract agent metadata from retrieved files.
    
    Args:
        agent_name: Agent API name
        version: Version suffix (e.g., 'v2')
        base_path: Base path to metadata files
        
    Returns:
        Tuple of (AgentMetadata or None, error message or None)
    """
    base = Path(base_path)
    
    # Find and parse bot file
    bot_files = list(base.glob(f'bots/{agent_name}/*.bot-meta.xml'))
    if not bot_files:
        return None, f"Bot metadata not found for {agent_name}"
    
    bot_info = parse_bot_metadata(bot_files[0])
    if 'error' in bot_info:
        return None, f"Failed to parse bot metadata: {bot_info['error']}"
    
    # Find and parse GenAiPlannerBundle
    topics = []
    actions = []
    
    if version:
        bundle_name = f"{agent_name}_{version}"
        bundle_files = list(base.glob(f'genAiPlannerBundles/{bundle_name}/*.genAiPlannerBundle'))
        
        if bundle_files:
            bundle_info = parse_genai_bundle(bundle_files[0])
            if 'error' not in bundle_info:
                topics = [TopicInfo(**t) for t in bundle_info.get('topics', [])]
                actions = [ActionInfo(**a) for a in bundle_info.get('actions', [])]
    
    metadata = AgentMetadata(
        api_name=bot_info.get('api_name', agent_name),
        label=bot_info.get('label', ''),
        description=bot_info.get('description', ''),
        topics=topics,
        actions=actions,
        versions=[]
    )
    
    return metadata, None


def format_topics_for_display(topics: List[TopicInfo]) -> List[Dict]:
    """
    Format topics for display in AskQuestion options.
    
    Args:
        topics: List of TopicInfo objects
        
    Returns:
        List of option dictionaries with 'id' and 'label' keys
    """
    options = []
    for topic in topics:
        label = topic.name
        if topic.description:
            label += f": {topic.description[:50]}..."
        
        options.append({
            'id': topic.name,
            'label': label
        })
    
    return options


def format_actions_for_display(actions: List[ActionInfo]) -> List[Dict]:
    """
    Format actions for display in AskQuestion options.
    
    Args:
        actions: List of ActionInfo objects
        
    Returns:
        List of option dictionaries with 'id' and 'label' keys
    """
    options = []
    for action in actions:
        options.append({
            'id': action.name,
            'label': action.name
        })
    
    return options


# Convenience functions for agent to get data

def get_agent_selection_data(org_alias: str) -> Dict:
    """
    Get all data needed for agent selection.
    
    Returns:
        {
            'success': bool,
            'agents': List of agent dicts,
            'options': List of formatted options for AskQuestion,
            'error': Error message or None
        }
    """
    agents, error = query_agents(org_alias)
    
    if error:
        return {
            'success': False,
            'agents': [],
            'options': [],
            'error': error
        }
    
    if not agents:
        return {
            'success': False,
            'agents': [],
            'options': [],
            'error': f'No agents found in org {org_alias}'
        }
    
    return {
        'success': True,
        'agents': agents,
        'options': format_agents_for_display(agents),
        'error': None
    }


def get_version_selection_data(org_alias: str, agent_api_name: str) -> Dict:
    """
    Get all data needed for version selection.
    
    Returns:
        {
            'success': bool,
            'versions': List of version dicts,
            'options': List of formatted options for AskQuestion,
            'active_version': Active version string or None,
            'error': Error message or None
        }
    """
    versions, error = query_agent_versions(org_alias, agent_api_name)
    
    if error:
        return {
            'success': False,
            'versions': [],
            'options': [],
            'active_version': None,
            'error': error
        }
    
    if not versions:
        return {
            'success': False,
            'versions': [],
            'options': [],
            'active_version': None,
            'error': f'No versions found for agent {agent_api_name}'
        }
    
    return {
        'success': True,
        'versions': [v.to_dict() for v in versions],
        'options': format_versions_for_display(versions),
        'active_version': get_active_version(versions),
        'error': None
    }


def get_metadata_data(org_alias: str, agent_name: str, version: str) -> Dict:
    """
    Retrieve and extract all metadata for an agent.
    
    Returns:
        {
            'success': bool,
            'metadata': AgentMetadata dict or None,
            'topics_options': List of topic options for AskQuestion,
            'actions_options': List of action options for AskQuestion,
            'error': Error message or None
        }
    """
    # First retrieve the metadata
    success, error = retrieve_agent_metadata(org_alias, agent_name, version)
    if not success:
        return {
            'success': False,
            'metadata': None,
            'topics_options': [],
            'actions_options': [],
            'error': error
        }
    
    # Then extract from files
    metadata, error = extract_metadata_from_files(agent_name, version)
    if error:
        return {
            'success': False,
            'metadata': None,
            'topics_options': [],
            'actions_options': [],
            'error': error
        }
    
    return {
        'success': True,
        'metadata': metadata.to_dict(),
        'topics_options': format_topics_for_display(metadata.topics),
        'actions_options': format_actions_for_display(metadata.actions),
        'error': None
    }


if __name__ == "__main__":
    # Test the functions
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python metadata_extractor.py <org_alias> [agent_name]")
        sys.exit(1)
    
    org_alias = sys.argv[1]
    
    print(f"Querying agents from {org_alias}...")
    data = get_agent_selection_data(org_alias)
    print(json.dumps(data, indent=2))
    
    if len(sys.argv) >= 3 and data['success']:
        agent_name = sys.argv[2]
        print(f"\nQuerying versions for {agent_name}...")
        version_data = get_version_selection_data(org_alias, agent_name)
        print(json.dumps(version_data, indent=2))
