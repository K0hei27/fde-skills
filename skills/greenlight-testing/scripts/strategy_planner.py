#!/usr/bin/env python3
"""
Strategy Planner for Greenlight
Gathers user input and generates comprehensive test strategy
"""

import json
from datetime import datetime, timedelta


def gather_test_strategy_input(agent_metadata):
    """
    Gather test strategy information from user through guided questions
    
    Args:
        agent_metadata: Agent metadata dict with topics, actions
    
    Returns:
        Dict with strategy information
    """
    
    strategy_input = {}
    
    print("\n📋 Let's build your test strategy!\n")
    
    # Question 1: Accuracy goal
    print("1️⃣  What's your accuracy goal?")
    print("   Purpose: Defines 'ready' benchmark")
    print("   Example: '95% topic, 90% action, 85% response'\n")
    accuracy_goal = input("   → ").strip()
    strategy_input['accuracy_goal'] = accuracy_goal if accuracy_goal else "95% topic, 90% action, 85% response"
    
    # Question 2: User stories with priorities
    print("\n2️⃣  What are your user stories?")
    print("   Purpose: Maps requirements to topics")
    print("   Example: P0: Order status, Returns / P1: FAQ, Account / P2: Escalation")
    print("   Enter stories (one per line, empty line to finish):\n")
    
    user_stories = []
    while True:
        story = input("   → ").strip()
        if not story:
            break
        user_stories.append(story)
    
    strategy_input['user_stories'] = user_stories
    
    # Question 3: Focus areas
    print("\n3️⃣  Any focus areas?")
    print("   Purpose: Drives test weighting")
    print("   Example: 'Returns topic — had issues in UAT'\n")
    focus_areas = input("   → ").strip()
    strategy_input['focus_areas'] = focus_areas if focus_areas else None
    
    # Question 4: Go-live date (optional)
    print("\n4️⃣  Go-live date? (optional)")
    print("   Purpose: Timeline context")
    print("   Example: 'March 1'\n")
    timeline = input("   → ").strip()
    strategy_input['timeline'] = timeline if timeline else None
    
    # Auto-calculate test cases based on number of topics
    num_topics = len(agent_metadata.get('topics', []))
    default_tests = num_topics * 50 if num_topics > 0 else 100
    strategy_input['total_test_cases'] = default_tests
    
    # Set goal for strategy document
    strategy_input['goal'] = f"Validate readiness for go-live" + (f" ({timeline})" if timeline else "")
    
    return strategy_input


def parse_user_stories(user_stories_list):
    """
    Parse user stories from list of strings
    
    Args:
        user_stories_list: List of strings like "P0: Check order status"
        
    Returns:
        List of dicts with priority, description
    """
    
    import re
    
    stories = []
    pattern = r'^-?\s*(P[0-2]):\s*(.+)$'
    
    for story_text in user_stories_list:
        match = re.match(pattern, story_text.strip())
        if match:
            stories.append({
                'priority': match.group(1),
                'description': match.group(2).strip()
            })
    
    return stories


def generate_test_strategy(agent_name, agent_metadata, strategy_input):
    """
    Generate comprehensive test strategy using AI reasoning
    
    Args:
        agent_name: Name of the agent
        agent_metadata: Agent topics, actions, etc.
        strategy_input: User input from gather_test_strategy_input()
        
    Returns:
        Complete test strategy dict
    """
    
    # Get agent description from metadata
    topics = agent_metadata.get('topics', [])
    agent_description = f"Agent with {len(topics)} topics"
    if topics:
        topic_names = [t.get('name', '') for t in topics[:3]]
        agent_description = f"Agent covering: {', '.join(topic_names)}"
        if len(topics) > 3:
            agent_description += f" and {len(topics) - 3} more topics"
    
    # Parse user stories
    user_stories = parse_user_stories(strategy_input['user_stories'])
    
    # Count by priority
    priority_counts = {'P0': 0, 'P1': 0, 'P2': 0}
    for story in user_stories:
        priority_counts[story['priority']] += 1
    
    # Calculate weight distribution (P0: 50%, P1: 30%, P2: 20%)
    total_tests = strategy_input['total_test_cases']
    
    # Allocate tests by priority
    p0_tests = int(total_tests * 0.5)
    p1_tests = int(total_tests * 0.3)
    p2_tests = int(total_tests * 0.2)
    
    # Distribute within each priority
    p0_per_story = p0_tests // priority_counts['P0'] if priority_counts['P0'] > 0 else 0
    p1_per_story = p1_tests // priority_counts['P1'] if priority_counts['P1'] > 0 else 0
    p2_per_story = p2_tests // priority_counts['P2'] if priority_counts['P2'] > 0 else 0
    
    # Generate jobs
    jobs = []
    job_id = 1
    
    for story in user_stories:
        # Find matching topic
        matched_topic = match_story_to_topic(story['description'], topics)
        matched_actions = get_actions_for_topic(matched_topic, agent_metadata.get('actions', []))
        
        # Determine test count
        if story['priority'] == 'P0':
            test_count = p0_per_story
            accuracy_targets = {'topic': 95, 'action': 90, 'response': 85}
        elif story['priority'] == 'P1':
            test_count = p1_per_story
            accuracy_targets = {'topic': 90, 'action': 85, 'response': 80}
        else:  # P2
            test_count = p2_per_story
            accuracy_targets = {'topic': 85, 'action': 80, 'response': 75}
        
        job = {
            'job_id': job_id,
            'job_name': f"{agent_name}_Job{job_id}_{story['description'][:30].replace(' ', '_')}",
            'priority': story['priority'],
            'user_story': story['description'],
            'topic': matched_topic,
            'actions': matched_actions,
            'test_count': test_count,
            'accuracy_targets': accuracy_targets,
            'estimated_credits': test_count * 0.5
        }
        
        jobs.append(job)
        job_id += 1
    
    # Add combo/edge case job if total > 100
    if total_tests >= 100:
        combo_tests = total_tests - sum(j['test_count'] for j in jobs)
        if combo_tests > 0:
            jobs.append({
                'job_id': job_id,
                'job_name': f"{agent_name}_Job{job_id}_Combo_EdgeCases",
                'priority': 'P0',
                'user_story': 'Combination scenarios and edge cases',
                'topic': 'Multi',
                'actions': [],
                'test_count': combo_tests,
                'accuracy_targets': {'topic': 90, 'action': 85, 'response': 80},
                'estimated_credits': combo_tests * 0.5
            })
    
    # Build complete strategy
    strategy = {
        'agent_name': agent_name,
        'goal': strategy_input['goal'],
        'description': agent_description,  # From metadata
        'timeline': strategy_input.get('timeline'),
        'focus_areas': strategy_input.get('focus_areas'),
        'total_test_cases': total_tests,
        'total_jobs': len(jobs),
        'total_estimated_credits': sum(j['estimated_credits'] for j in jobs),
        'estimated_duration_minutes': int(total_tests * 0.12),  # ~0.12 min per test case
        'jobs': jobs,
        'user_stories': user_stories,
        'generated_at': datetime.now().isoformat()
    }
    
    return strategy


def match_story_to_topic(story_description, topics):
    """
    Match user story to agent topic using keyword matching
    
    Args:
        story_description: User story description
        topics: List of topic dicts from agent metadata
        
    Returns:
        Matched topic name or None
    """
    
    # Simple keyword matching for MVP
    story_lower = story_description.lower()
    
    for topic in topics:
        topic_name = topic.get('name', '')
        topic_desc = topic.get('description', '')
        
        # Check if any words match
        topic_keywords = topic_name.lower().replace('_', ' ').split()
        
        for keyword in topic_keywords:
            if len(keyword) > 3 and keyword in story_lower:
                return topic_name
    
    # If no match, return first topic
    return topics[0].get('name') if topics else None


def get_actions_for_topic(topic_name, actions):
    """
    Get actions associated with a topic
    
    Args:
        topic_name: Topic name
        actions: List of action dicts
        
    Returns:
        List of action names
    """
    
    if not topic_name:
        return []
    
    matched_actions = []
    for action in actions:
        if action.get('topic') == topic_name:
            matched_actions.append(action.get('name'))
    
    return matched_actions


def format_test_strategy_document(strategy):
    """
    Format test strategy as markdown document for review
    
    Args:
        strategy: Strategy dict from generate_test_strategy()
        
    Returns:
        Markdown formatted strategy document
    """
    
    doc = []
    
    # Header
    doc.append(f"# Test Strategy: {strategy['agent_name']}")
    doc.append(f"\n*Go-Live Readiness Assessment*\n")
    doc.append("\n---\n")
    
    # Scope
    doc.append("## Scope\n")
    doc.append("| | |")
    doc.append("|---|---|")
    doc.append(f"| **Goal** | {strategy['goal']} |")
    doc.append(f"| **Test Cases** | {strategy['total_test_cases']} |")
    doc.append(f"| **Est. Credits** | ~{strategy['total_estimated_credits']:.0f} |")
    doc.append(f"| **Est. Duration** | {strategy['estimated_duration_minutes']} min |")
    
    if strategy.get('timeline'):
        doc.append(f"| **Timeline** | {strategy['timeline']} |")
    
    doc.append("\n---\n")
    
    # Coverage Matrix
    doc.append("## Coverage Matrix\n")
    doc.append("| User Story | Priority | Topic(s) | Weight | Test Cases |")
    doc.append("|------------|----------|----------|--------|------------|")
    
    for job in strategy['jobs']:
        if job['user_story'] == 'Combination scenarios and edge cases':
            continue
        weight = (job['test_count'] / strategy['total_test_cases'] * 100)
        topic_display = job['topic'] if job['topic'] else 'N/A'
        doc.append(f"| {job['user_story']} | {job['priority']} | {topic_display} | {weight:.0f}% | {job['test_count']} |")
    
    # Add combo/edge if exists
    combo_job = [j for j in strategy['jobs'] if 'Combo' in j['job_name']]
    if combo_job:
        job = combo_job[0]
        doc.append(f"| Combo / Edge | — | Multi | — | {job['test_count']} |")
    
    doc.append("\n---\n")
    
    # Accuracy Targets
    doc.append("## Accuracy Targets\n")
    doc.append("| Topic | Topic % | Action % | Response % |")
    doc.append("|-------|---------|----------|------------|")
    
    # Get unique topics
    unique_topics = {}
    for job in strategy['jobs']:
        if job['topic'] and job['topic'] != 'Multi':
            if job['topic'] not in unique_topics:
                unique_topics[job['topic']] = job['accuracy_targets']
    
    for topic, targets in unique_topics.items():
        doc.append(f"| {topic} | ≥{targets['topic']} | ≥{targets['action']} | ≥{targets['response']} |")
    
    doc.append("\n---\n")
    
    # Job Plan
    doc.append("## Job Plan\n")
    doc.append("| Job | Scope | Test Cases |")
    doc.append("|-----|-------|------------|")
    
    for job in strategy['jobs']:
        scope = job['user_story']
        if job['topic'] and job['topic'] != 'Multi':
            scope += f" ({job['topic']})"
        doc.append(f"| {job['job_id']} | {scope} | {job['test_count']} |")
    
    doc.append("\n---\n")
    
    # Readiness Criteria
    doc.append("## Readiness Criteria\n")
    doc.append("| Status | Criteria |")
    doc.append("|--------|----------|")
    doc.append("| ✅ **Ready** | All P0 at target, action accuracy ≥90% |")
    doc.append("| ⚠️ **Conditional** | P0 at threshold, gaps documented |")
    doc.append("| 🚫 **Not Ready** | Any P0 below threshold |")
    
    doc.append("\n---\n")
    
    # Summary
    doc.append("## Summary\n")
    doc.append(f"- **Total Jobs:** {strategy['total_jobs']}")
    doc.append(f"\n- **Total Test Cases:** {strategy['total_test_cases']}")
    doc.append(f"\n- **Estimated Credits:** ~{strategy['total_estimated_credits']:.0f}")
    doc.append(f"\n- **Estimated Duration:** ~{strategy['estimated_duration_minutes']} minutes")
    
    p0_jobs = [j for j in strategy['jobs'] if j['priority'] == 'P0']
    p1_jobs = [j for j in strategy['jobs'] if j['priority'] == 'P1']
    p2_jobs = [j for j in strategy['jobs'] if j['priority'] == 'P2']
    
    doc.append(f"\n- **P0 Coverage:** {sum(j['test_count'] for j in p0_jobs)} test cases ({len(p0_jobs)} jobs)")
    doc.append(f"\n- **P1 Coverage:** {sum(j['test_count'] for j in p1_jobs)} test cases ({len(p1_jobs)} jobs)")
    doc.append(f"\n- **P2 Coverage:** {sum(j['test_count'] for j in p2_jobs)} test cases ({len(p2_jobs)} jobs)")
    
    return '\n'.join(doc)


def prompt_for_strategy_approval(strategy_doc):
    """
    Show strategy to user and get approval
    
    Args:
        strategy_doc: Formatted strategy document
        
    Returns:
        'approved', 'edit', or 'cancel'
    """
    
    print("\n" + "="*70)
    print("📋 PROPOSED TEST STRATEGY")
    print("="*70 + "\n")
    print(strategy_doc)
    print("\n" + "="*70)
    print("\n✅ Do you approve this test strategy?")
    print("   1. Yes, proceed")
    print("   2. No, let me edit")
    print("   3. Cancel\n")
    
    choice = input("   → ").strip()
    
    if choice == '1':
        return 'approved'
    elif choice == '2':
        return 'edit'
    else:
        return 'cancel'


def edit_strategy(strategy):
    """
    Allow user to edit strategy
    
    Args:
        strategy: Strategy dict
        
    Returns:
        Updated strategy dict
    """
    
    print("\n📝 What would you like to edit?\n")
    print("1. Test case counts")
    print("2. Add/remove jobs")
    print("3. Change priorities")
    print("4. Other\n")
    
    choice = input("   → ").strip()
    
    if choice == '1':
        print("\nCurrent test counts:")
        for job in strategy['jobs']:
            print(f"  Job {job['job_id']}: {job['test_count']} tests")
        
        print("\nEnter new counts (comma-separated):")
        new_counts = input("   → ").strip().split(',')
        
        for i, count in enumerate(new_counts):
            if i < len(strategy['jobs']):
                strategy['jobs'][i]['test_count'] = int(count.strip())
        
        # Recalculate totals
        strategy['total_test_cases'] = sum(j['test_count'] for j in strategy['jobs'])
        strategy['total_estimated_credits'] = strategy['total_test_cases'] * 0.5
        strategy['estimated_duration_minutes'] = int(strategy['total_test_cases'] * 0.12)
    
    return strategy


if __name__ == '__main__':
    print("Strategy Planner for Greenlight")
    print("\nThis module handles user input and test strategy generation")
    print("\nUsage:")
    print("  from strategy_planner import gather_test_strategy_input, generate_test_strategy")
    print("  input_data = gather_test_strategy_input()")
    print("  strategy = generate_test_strategy(agent, metadata, input_data)")
