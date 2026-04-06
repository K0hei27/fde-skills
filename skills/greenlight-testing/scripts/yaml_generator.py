#!/usr/bin/env python3
"""
YAML Test Spec Generator
Generates Salesforce Testing Center YAML test spec files
"""

import yaml
from typing import Dict, List
from pathlib import Path


def generate_utterances(story_description: str, topic_info: Dict, count: int = 10) -> List[str]:
    """
    Generate test utterances for a user story and topic
    
    For MVP, generates simple variations. Future: use LLM for better quality.
    
    Args:
        story_description: User story description
        topic_info: Topic metadata (name, description, utterances)
        count: Number of utterances to generate
        
    Returns:
        List of utterance strings
    """
    utterances = []
    
    # Use existing topic utterances if available
    existing = topic_info.get('utterances', [])
    utterances.extend(existing[:count])
    
    # If we need more, generate simple variations
    base_phrases = [
        story_description,
        f"Can you help me {story_description.lower()}",
        f"I need to {story_description.lower()}",
        f"How do I {story_description.lower()}",
        f"Please {story_description.lower()}",
    ]
    
    # Add variations
    for phrase in base_phrases:
        if len(utterances) >= count:
            break
        if phrase not in utterances:
            utterances.append(phrase)
    
    # Pad with question variations if still need more
    while len(utterances) < count:
        utterances.append(f"{story_description}?")
        if len(utterances) >= count:
            break
        utterances.append(f"Help with {story_description.lower()}")
        if len(utterances) >= count:
            break
        utterances.append(f"Question about {story_description.lower()}")
    
    return utterances[:count]


def generate_expected_outcome(story_description: str, topic_info: Dict) -> str:
    """
    Generate expected outcome for a test case
    
    Args:
        story_description: User story description
        topic_info: Topic metadata
        
    Returns:
        Expected outcome string
    """
    topic_desc = topic_info.get('description', '')
    
    if topic_desc:
        return f"Agent successfully handles the request using {topic_info.get('name')} topic. {topic_desc}"
    else:
        return f"Agent successfully handles: {story_description}"


def generate_test_spec_yaml(
    agent_name: str,
    job_name: str,
    story: Dict,
    topic_info: Dict,
    actions: List[str],
    test_case_count: int,
    metrics: List[str] = None
) -> str:
    """
    Generate YAML test spec for a single job
    
    Args:
        agent_name: Agent API name
        job_name: Job identifier (e.g., "Job1_OrderStatus")
        story: User story dictionary
        topic_info: Topic metadata dictionary
        actions: List of action names for this topic
        test_case_count: Number of test cases to generate
        metrics: List of metrics to include
        
    Returns:
        YAML string
    """
    if metrics is None:
        metrics = ["completeness", "coherence", "conciseness", "latency"]
    
    # Generate utterances
    utterances = generate_utterances(story['description'], topic_info, test_case_count)
    
    # Generate expected outcome
    expected_outcome = generate_expected_outcome(story['description'], topic_info)
    
    # Build test cases
    test_cases = []
    for utterance in utterances:
        test_case = {
            'utterance': utterance,
            'expectedTopic': topic_info.get('name', 'Unknown'),
            'expectedActions': actions if actions else [],
            'expectedOutcome': expected_outcome,
            'metrics': metrics
        }
        test_cases.append(test_case)
    
    # Build spec structure
    spec = {
        'name': job_name,
        'description': f"Test {story['description']} - {story['priority']} priority",
        'agent': agent_name,
        'testCases': test_cases
    }
    
    # Convert to YAML
    yaml_str = yaml.dump(spec, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return yaml_str


def generate_test_specs_from_strategy(strategy: Dict, output_dir: str = ".") -> List[Dict]:
    """
    Generate YAML test spec files from strategy
    
    Args:
        strategy: Strategy dictionary from strategy_generator
        output_dir: Directory to write YAML files
        
    Returns:
        List of job info dictionaries
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    agent_name = strategy['agent_name']
    topics_map = {t['name']: t for t in strategy['topics']}
    
    jobs = []
    job_num = 1
    
    for story in strategy['user_stories']:
        # For MVP: Create one job per story
        # Skip if no test cases
        if story['test_cases'] == 0:
            continue
        
        # Get first topic (for MVP, assume one topic per story)
        topic_name = story['topics'][0] if story['topics'] else 'Unknown'
        topic_info = topics_map.get(topic_name, {'name': topic_name, 'description': '', 'utterances': []})
        
        # Get actions for this topic (simplified - in reality would need to map actions to topics)
        actions = []  # For MVP, leave empty - user can fill in
        
        # Generate job name
        job_name = f"Job{job_num}_{topic_name.replace(' ', '_')}"
        
        # Generate YAML
        yaml_content = generate_test_spec_yaml(
            agent_name=agent_name,
            job_name=job_name,
            story=story,
            topic_info=topic_info,
            actions=actions,
            test_case_count=story['test_cases'],
            metrics=strategy['config']['metrics']
        )
        
        # Write to file
        output_file = output_path / f"{job_name.lower()}.yaml"
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        
        jobs.append({
            'job_num': job_num,
            'job_name': job_name,
            'file': str(output_file),
            'story': story['description'],
            'priority': story['priority'],
            'test_cases': story['test_cases'],
            'topic': topic_name
        })
        
        job_num += 1
    
    return jobs


if __name__ == "__main__":
    # Test YAML generation
    test_story = {
        'priority': 'P0',
        'description': 'Check order status',
        'topics': ['Order_Lookup'],
        'test_cases': 5
    }
    
    test_topic = {
        'name': 'Order_Lookup',
        'description': 'Look up customer order status',
        'utterances': ['What is my order status?', 'Check my order']
    }
    
    yaml_content = generate_test_spec_yaml(
        agent_name='Resort_Manager',
        job_name='Job1_OrderLookup',
        story=test_story,
        topic_info=test_topic,
        actions=['Check_Order_Status'],
        test_case_count=5
    )
    
    print(yaml_content)
