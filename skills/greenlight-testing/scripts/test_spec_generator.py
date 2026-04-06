#!/usr/bin/env python3
"""
Test Spec Generator for Greenlight
Generates Salesforce Agent test spec YAML files based on test plan
"""

import yaml
import os
from datetime import datetime


def generate_test_spec_yaml(agent_name, topic_name, actions, test_cases, description):
    """
    Generate a test spec YAML file for Salesforce Agent testing
    
    Args:
        agent_name: API name of the agent
        topic_name: Expected topic for these test cases
        actions: List of expected action names
        test_cases: List of test case dicts with 'utterance' and 'expected_outcome'
        description: Description of what this test covers
        
    Returns:
        YAML string in Salesforce format
    """
    
    spec = {
        'subject': {
            'type': 'AGENT',
            'developerName': agent_name
        },
        'description': description,
        'testCases': []
    }
    
    # Add each test case
    for tc in test_cases:
        test_case = {
            'utterance': tc['utterance'],
            'expectedTopics': [topic_name] if topic_name else [],
            'expectedActions': actions if actions else [],
            'expectedOutcome': tc.get('expected_outcome', 'Agent should provide accurate and complete response')
        }
        
        # Add custom evaluations if provided
        if tc.get('custom_evaluations'):
            test_case['customEvaluations'] = tc['custom_evaluations']
        
        spec['testCases'].append(test_case)
    
    # Add metrics section (standard metrics)
    spec['metrics'] = [
        'output_validation',
        'completeness',
        'coherence',
        'conciseness'
    ]
    
    return yaml.dump(spec, default_flow_style=False, sort_keys=False, allow_unicode=True)


def generate_salesforce_test_spec_from_job(agent_name, job_name, topic, actions, test_count, user_story):
    """
    Generate Salesforce CLI-compatible YAML spec from greenlight job format.
    Uses correct format: name, subjectType, subjectName, subjectVersion,
    expectedTopic (singular), expectedActions, contextVariables, customEvaluations, metrics.
    """
    test_cases = generate_test_utterances(user_story, topic or 'General', test_count)
    
    spec = {
        'name': job_name,
        'subjectType': 'AGENT',
        'subjectName': agent_name,
        'subjectVersion': 'v2',
        'testCases': []
    }
    
    for tc in test_cases:
        test_case = {
            'utterance': tc['utterance'],
            'contextVariables': [],
            'customEvaluations': [],
            'expectedTopic': topic if topic else 'General',
            'expectedActions': actions if actions else [],
            'expectedOutcome': tc.get('expected_outcome', 'Agent should provide accurate and complete response'),
            'metrics': ['completeness', 'coherence', 'conciseness', 'output_latency_milliseconds']
        }
        spec['testCases'].append(test_case)
    
    return yaml.dump(spec, default_flow_style=False, sort_keys=False, allow_unicode=True)


def generate_test_utterances(priority_description, topic_name, num_cases=5):
    """
    Generate test utterances for a given priority/scenario
    This is a template - in production, you'd use an LLM to generate realistic utterances
    
    Args:
        priority_description: Description of what to test (e.g., "Answer benefits questions")
        topic_name: Topic this relates to
        num_cases: Number of test cases to generate
        
    Returns:
        List of test case dicts with utterances and expected outcomes
    """
    
    # Template utterances - in production, use LLM to generate based on:
    # - Agent metadata (topics, actions)
    # - Priority description
    # - Knowledge base content
    
    test_cases = []
    
    # Generate variations
    templates = [
        f"Can you help me with {priority_description.lower()}?",
        f"I need information about {priority_description.lower()}",
        f"What can you tell me about {priority_description.lower()}?",
        f"How do I {priority_description.lower()}?",
        f"Please explain {priority_description.lower()}",
    ]
    
    for i in range(min(num_cases, len(templates))):
        test_cases.append({
            'utterance': templates[i],
            'expected_outcome': f"Agent should provide accurate information about {priority_description.lower()}"
        })
    
    # If need more cases, add numbered variations
    if num_cases > len(templates):
        for i in range(num_cases - len(templates)):
            test_cases.append({
                'utterance': f"Question {i+1} about {priority_description.lower()}",
                'expected_outcome': f"Agent should respond appropriately to {priority_description.lower()}"
            })
    
    return test_cases


def create_test_plan_from_priorities(agent_name, priorities, agent_metadata, total_test_cases=30):
    """
    Create a test plan with multiple test jobs based on priorities
    
    Args:
        agent_name: Name of the agent
        priorities: List of priority descriptions from user
        agent_metadata: Dict with topics and actions from agent
        total_test_cases: Total number of test cases to generate
        
    Returns:
        List of test job specs
    """
    
    test_jobs = []
    cases_per_priority = total_test_cases // len(priorities)
    
    # Get topics and actions from metadata
    topics = agent_metadata.get('topics', [])
    actions = agent_metadata.get('actions', [])
    
    for i, priority in enumerate(priorities, 1):
        # Match priority to most relevant topic (simple matching for MVP)
        matched_topic = None
        matched_actions = []
        
        if topics:
            # Simple keyword matching - in production, use semantic matching
            for topic in topics:
                topic_name = topic.get('name', '')
                if any(word.lower() in topic_name.lower() for word in priority.split()):
                    matched_topic = topic_name
                    # Get actions for this topic
                    matched_actions = [a.get('name') for a in actions if a.get('topic') == topic_name]
                    break
            
            # If no match, use first topic
            if not matched_topic and topics:
                matched_topic = topics[0].get('name')
                matched_actions = [a.get('name') for a in actions if a.get('topic') == matched_topic]
        
        # Generate test cases for this priority
        test_cases = generate_test_utterances(priority, matched_topic, cases_per_priority)
        
        # Create test job spec
        job = {
            'job_id': i,
            'job_name': f"{agent_name}_Job{i}_{priority[:30].replace(' ', '_')}",
            'priority': priority,
            'topic': matched_topic,
            'actions': matched_actions,
            'test_cases': test_cases,
            'num_cases': len(test_cases)
        }
        
        test_jobs.append(job)
    
    return test_jobs


def save_test_spec_files(test_jobs, agent_name, output_dir='test-specs'):
    """
    Save test spec YAML files for each job
    
    Args:
        test_jobs: List of test job specs
        agent_name: Name of the agent
        output_dir: Directory to save files
        
    Returns:
        List of generated file paths
    """
    
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []
    
    for job in test_jobs:
        # Generate YAML content
        yaml_content = generate_test_spec_yaml(
            agent_name=agent_name,
            topic_name=job['topic'],
            actions=job['actions'],
            test_cases=job['test_cases'],
            description=f"Test job for: {job['priority']}"
        )
        
        # Save to file
        filename = f"{job['job_name']}.yaml"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(yaml_content)
        
        generated_files.append(filepath)
        print(f"✅ Generated: {filepath} ({job['num_cases']} test cases)")
    
    return generated_files


def generate_test_plan_summary(test_jobs, agent_name, strategy):
    """
    Generate a test plan summary document
    
    Args:
        test_jobs: List of test job specs
        agent_name: Name of the agent
        strategy: Implementation strategy from user
        
    Returns:
        Markdown formatted test plan
    """
    
    total_cases = sum(job['num_cases'] for job in test_jobs)
    
    plan = []
    plan.append(f"# Test Plan: {agent_name}\n")
    plan.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    plan.append(f"\n**Strategy:** {strategy}\n")
    plan.append(f"**Total Test Jobs:** {len(test_jobs)}")
    plan.append(f"\n**Total Test Cases:** {total_cases}\n")
    plan.append("\n---\n")
    
    # Summary table
    plan.append("## Test Jobs Summary\n")
    plan.append("| Job | Priority | Topic | Test Cases | File |")
    plan.append("|-----|----------|-------|------------|------|")
    
    for job in test_jobs:
        plan.append(f"| {job['job_id']} | {job['priority']} | {job['topic'] or 'N/A'} | {job['num_cases']} | {job['job_name']}.yaml |")
    
    plan.append("\n---\n")
    
    # Detailed breakdown
    plan.append("## Test Jobs Detail\n")
    
    for job in test_jobs:
        plan.append(f"\n### Job {job['job_id']}: {job['priority']}\n")
        plan.append(f"**Topic:** {job['topic'] or 'N/A'}")
        plan.append(f"\n**Actions:** {', '.join(job['actions']) if job['actions'] else 'N/A'}")
        plan.append(f"\n**Test Cases:** {job['num_cases']}\n")
        plan.append("\n**Sample Test Cases:**")
        
        for i, tc in enumerate(job['test_cases'][:3], 1):
            plan.append(f"\n{i}. {tc['utterance']}")
        
        if len(job['test_cases']) > 3:
            plan.append(f"\n... and {len(job['test_cases']) - 3} more")
    
    plan.append("\n\n---\n")
    
    # Execution commands
    plan.append("## Execution Commands\n")
    plan.append("\n### Step 1: Create Tests\n")
    
    for job in test_jobs:
        plan.append(f"\n```bash")
        plan.append(f"\nsf agent test create --api-name \"{job['job_name']}\" \\")
        plan.append(f"\n  --spec test-specs/{job['job_name']}.yaml \\")
        plan.append(f"\n  --target-org your-org")
        plan.append(f"\n```\n")
    
    plan.append("\n### Step 2: Run Tests (Parallel)\n")
    plan.append("\n```bash")
    plan.append("# Run all tests in parallel")
    
    for job in test_jobs:
        plan.append(f"\nsf agent test run --api-name \"{job['job_name']}\" --target-org your-org --json &")
    
    plan.append("\nwait  # Wait for all to complete")
    plan.append("\n```\n")
    
    plan.append("\n### Step 3: Collect Results\n")
    plan.append("\n```bash")
    plan.append("# Get job IDs from test list")
    plan.append("\nsf agent test list --target-org your-org")
    plan.append("\n\n# Get results for each job")
    
    for job in test_jobs:
        plan.append(f"\nsf agent test results --job-id <JOB_ID_{job['job_id']}> --target-org your-org --json > results_{job['job_id']}.json")
    
    plan.append("\n```\n")
    
    return '\n'.join(plan)


if __name__ == '__main__':
    print("Test Spec Generator for Greenlight")
    print("\nUsage:")
    print("  from test_spec_generator import create_test_plan_from_priorities")
    print("  test_jobs = create_test_plan_from_priorities(agent, priorities, metadata, 30)")
    print("  files = save_test_spec_files(test_jobs, agent, 'test-specs')")
