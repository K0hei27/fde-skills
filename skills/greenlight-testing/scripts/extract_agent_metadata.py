#!/usr/bin/env python3
"""
Extract Agent Metadata (Topics, Instructions, Actions)
Parses retrieved Bot and GenAiPlannerBundle metadata files
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

def parse_bot_metadata(bot_file):
    """Parse Bot metadata XML file"""
    try:
        tree = ET.parse(bot_file)
        root = tree.getroot()
        
        bot_info = {
            'api_name': root.findtext('.//{http://soap.sforce.com/2006/04/metadata}fullName', ''),
            'label': root.findtext('.//{http://soap.sforce.com/2006/04/metadata}label', ''),
            'description': root.findtext('.//{http://soap.sforce.com/2006/04/metadata}description', ''),
        }
        return bot_info
    except Exception as e:
        return {'error': str(e)}

def parse_genai_bundle(bundle_file):
    """Parse GenAiPlannerBundle XML file"""
    try:
        tree = ET.parse(bundle_file)
        root = tree.getroot()
        ns = {'md': 'http://soap.sforce.com/2006/04/metadata'}
        
        bundle_info = {
            'topics': [],
            'actions': [],
            'description': root.findtext('.//{http://soap.sforce.com/2006/04/metadata}description', ''),
        }
        
        # Extract local topics
        for topic in root.findall('.//{http://soap.sforce.com/2006/04/metadata}localTopics'):
            topic_name = topic.findtext('.//{http://soap.sforce.com/2006/04/metadata}developerName', '')
            topic_desc = topic.findtext('.//{http://soap.sforce.com/2006/04/metadata}description', '')
            
            # Extract utterances
            utterances = []
            for utterance in topic.findall('.//{http://soap.sforce.com/2006/04/metadata}utterance'):
                utterances.append(utterance.text if utterance.text else '')
            
            bundle_info['topics'].append({
                'name': topic_name,
                'description': topic_desc,
                'utterances': utterances
            })
        
        # Extract local action links
        for action_link in root.findall('.//{http://soap.sforce.com/2006/04/metadata}localActionLinks'):
            action_name = action_link.findtext('.//{http://soap.sforce.com/2006/04/metadata}genAiFunctionName', '')
            bundle_info['actions'].append({
                'name': action_name,
                'type': 'localAction'
            })
        
        # Extract local topic links (referenced topics)
        for topic_link in root.findall('.//{http://soap.sforce.com/2006/04/metadata}localTopicLinks'):
            topic_name = topic_link.findtext('.//{http://soap.sforce.com/2006/04/metadata}genAiPluginName', '')
            bundle_info['topics'].append({
                'name': topic_name,
                'description': 'Referenced topic',
                'utterances': []
            })
        
        return bundle_info
    except Exception as e:
        return {'error': str(e)}

def find_agent_metadata():
    """Find and parse all agent metadata files"""
    base_path = Path('force-app/main/default')
    
    agents = {}
    
    # Find Bot files
    bot_files = list(base_path.glob('bots/*/*.bot-meta.xml'))
    for bot_file in bot_files:
        bot_info = parse_bot_metadata(bot_file)
        agent_name = bot_info.get('api_name', bot_file.parent.name)
        agents[agent_name] = {
            'bot': bot_info,
            'bundle': None
        }
    
    # Find GenAiPlannerBundle files
    bundle_files = list(base_path.glob('genAiPlannerBundles/*/*.genAiPlannerBundle'))
    for bundle_file in bundle_files:
        bundle_info = parse_genai_bundle(bundle_file)
        # Try to match bundle to agent (usually same name)
        agent_name = bundle_file.parent.name
        if agent_name not in agents:
            agents[agent_name] = {'bot': None, 'bundle': None}
        agents[agent_name]['bundle'] = bundle_info
    
    return agents

def main():
    """Main function"""
    print("=" * 70)
    print("Agent Metadata Extractor")
    print("=" * 70)
    print()
    
    agents = find_agent_metadata()
    
    if not agents:
        print("❌ No agent metadata found.")
        print()
        print("💡 First retrieve metadata:")
        print("   ./scripts/get_agent_metadata.sh")
        print("   or")
        print("   sf project retrieve start --metadata \"Bot:*\" --target-org <org>")
        print("   sf project retrieve start --metadata \"GenAiPlannerBundle:*\" --target-org <org>")
        sys.exit(1)
    
    for agent_name, metadata in agents.items():
        print(f"\n{'='*70}")
        print(f"Agent: {agent_name}")
        print(f"{'='*70}")
        
        # Bot info
        if metadata['bot']:
            bot = metadata['bot']
            print(f"\n📋 Bot Information:")
            print(f"   API Name: {bot.get('api_name', 'N/A')}")
            print(f"   Label: {bot.get('label', 'N/A')}")
            print(f"   Description: {bot.get('description', 'N/A')}")
        
        # Bundle info (topics, instructions)
        if metadata['bundle']:
            bundle = metadata['bundle']
            
            if bundle.get('instructions'):
                print(f"\n📝 Instructions:")
                print(f"   {bundle['instructions'][:200]}...")
            
            if bundle.get('system_prompt'):
                print(f"\n💬 System Prompt:")
                print(f"   {bundle['system_prompt'][:200]}...")
            
            if bundle.get('topics'):
                print(f"\n🎯 Topics ({len(bundle['topics'])}):")
                for topic in bundle['topics']:
                    print(f"   • {topic.get('name', 'N/A')}")
                    if topic.get('description'):
                        print(f"     {topic['description'][:100]}...")
            
            if bundle.get('actions'):
                print(f"\n⚡ Actions ({len(bundle['actions'])}):")
                for action in bundle['actions']:
                    print(f"   • {action.get('name', 'N/A')} ({action.get('type', 'N/A')})")
                    if action.get('description'):
                        print(f"     {action['description'][:100]}...")
        else:
            print("\n⚠️  No GenAiPlannerBundle found for this agent")
    
    print("\n" + "=" * 70)
    print("✅ Done!")
    print("=" * 70)

if __name__ == "__main__":
    main()
