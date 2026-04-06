#!/usr/bin/env python3
"""
Test Strategy Generator
Parses user stories and generates test strategy
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from metadata_extractor import extract_agent_metadata


class UserStory:
    """Represents a user story"""
    
    def __init__(self, priority: str, description: str, weight: float = 0.0):
        self.priority = priority.upper()  # P0, P1, P2
        self.description = description
        self.weight = weight  # Utterance weight (0-1)
        self.topics: List[str] = []
        self.test_cases = 0
        
    def __repr__(self):
        return f"UserStory({self.priority}, {self.description}, weight={self.weight})"


def parse_user_stories(markdown_text: str) -> List[UserStory]:
    """
    Parse user stories from markdown format
    
    Expected format:
    - P0: Story description (60%)
    - P1: Another story (25%)
    - P2: Third story
    
    Weight is optional. If not provided, will be auto-calculated from priority.
    
    Args:
        markdown_text: Markdown text with user stories
        
    Returns:
        List of UserStory objects
    """
    stories = []
    
    # Pattern: - P0: Description (optional weight%)
    pattern = r'^[-*]\s*(P[012]):\s*(.+?)(?:\s*\((\d+(?:\.\d+)?)%?\))?$'
    
    for line in markdown_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            priority = match.group(1).upper()
            description = match.group(2).strip()
            weight_str = match.group(3)
            
            weight = float(weight_str) / 100 if weight_str else 0.0
            
            stories.append(UserStory(priority, description, weight))
    
    return stories


def auto_calculate_weights(stories: List[UserStory], priority_weights: Dict[str, float]) -> List[UserStory]:
    """
    Auto-calculate weights for stories that don't have explicit weights
    Uses priority-based distribution
    
    Args:
        stories: List of user stories
        priority_weights: Priority weight config (e.g., {"P0": 0.5, "P1": 0.3, "P2": 0.2})
        
    Returns:
        Updated list of user stories with weights
    """
    # Separate stories with and without weights
    with_weights = [s for s in stories if s.weight > 0]
    without_weights = [s for s in stories if s.weight == 0]
    
    if not without_weights:
        return stories
    
    # Calculate remaining weight
    used_weight = sum(s.weight for s in with_weights)
    remaining_weight = 1.0 - used_weight
    
    if remaining_weight <= 0:
        # All weight is used, distribute evenly among remaining
        remaining_weight = 0.1 * len(without_weights)
    
    # Count stories by priority
    priority_counts = {}
    for story in without_weights:
        priority_counts[story.priority] = priority_counts.get(story.priority, 0) + 1
    
    # Calculate weight per priority
    total_priority_weight = sum(priority_weights.get(p, 0.1) * count 
                                for p, count in priority_counts.items())
    
    # Distribute weights
    for story in without_weights:
        priority_weight = priority_weights.get(story.priority, 0.1)
        story_count = priority_counts[story.priority]
        story.weight = (priority_weight / story_count) * remaining_weight / total_priority_weight
    
    return stories


def map_stories_to_topics(stories: List[UserStory], agent_topics: List[Dict]) -> List[UserStory]:
    """
    Map user stories to agent topics using keyword matching
    
    Args:
        stories: List of user stories
        agent_topics: List of agent topic dictionaries
        
    Returns:
        Updated stories with topic mappings
    """
    for story in stories:
        story_lower = story.description.lower()
        
        # Try to match story description to topic names/descriptions
        for topic in agent_topics:
            topic_name = topic.get('name', '').lower()
            topic_desc = topic.get('description', '').lower()
            
            # Simple keyword matching
            if topic_name in story_lower or any(word in topic_name for word in story_lower.split()):
                story.topics.append(topic.get('name'))
            elif topic_desc and any(word in topic_desc for word in story_lower.split() if len(word) > 3):
                story.topics.append(topic.get('name'))
        
        # If no topics matched, mark as "Unknown" for manual mapping
        if not story.topics:
            story.topics.append("Unknown")
    
    return stories


def calculate_test_distribution(stories: List[UserStory], total_budget: int = 200) -> List[UserStory]:
    """
    Calculate number of test cases per story based on weights
    
    Args:
        stories: List of user stories with weights
        total_budget: Total number of test cases to distribute
        
    Returns:
        Updated stories with test case counts
    """
    for story in stories:
        story.test_cases = int(total_budget * story.weight)
    
    # Adjust rounding to match total budget
    total_assigned = sum(s.test_cases for s in stories)
    diff = total_budget - total_assigned
    
    if diff > 0:
        # Add remaining to highest priority stories
        sorted_stories = sorted(stories, key=lambda s: (s.priority, -s.weight))
        for i in range(diff):
            sorted_stories[i % len(sorted_stories)].test_cases += 1
    
    return stories


def generate_strategy(
    agent_name: str,
    user_stories_markdown: str,
    config_path: str = None,
    total_test_cases: int = 200,
    base_path: str = "force-app/main/default"
) -> Dict:
    """
    Generate test strategy from user stories and agent metadata
    
    Args:
        agent_name: Agent API name
        user_stories_markdown: Markdown text with user stories
        config_path: Path to config directory
        total_test_cases: Total test cases to generate
        base_path: Base path to metadata files
        
    Returns:
        Strategy dictionary
    """
    # Load config
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config"
    else:
        config_path = Path(config_path)
    
    with open(config_path / "targets.json") as f:
        config = json.load(f)
    
    # Extract agent metadata
    agents = extract_agent_metadata(agent_name, base_path)
    if agent_name not in agents:
        raise ValueError(f"Agent '{agent_name}' not found in metadata")
    
    agent = agents[agent_name]
    
    # Parse user stories
    stories = parse_user_stories(user_stories_markdown)
    
    # Auto-calculate weights if needed
    stories = auto_calculate_weights(stories, config['priority_weights'])
    
    # Map stories to topics
    stories = map_stories_to_topics(stories, agent.topics)
    
    # Calculate test distribution
    stories = calculate_test_distribution(stories, total_test_cases)
    
    # Generate strategy data
    strategy = {
        'agent_name': agent_name,
        'agent_label': agent.label,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_test_cases': total_test_cases,
        'estimated_credits': int(total_test_cases * config['credit_per_test']),
        'estimated_duration': int(total_test_cases * 0.5),  # ~30 sec per test
        'user_stories': [
            {
                'priority': s.priority,
                'description': s.description,
                'topics': s.topics,
                'weight': f"{s.weight * 100:.1f}%",
                'test_cases': s.test_cases
            }
            for s in stories
        ],
        'topics': agent.topics,
        'accuracy_targets': config['accuracy_targets'],
        'config': config
    }
    
    return strategy


if __name__ == "__main__":
    # Test strategy generation
    test_stories = """
    - P0: Check order status (60%)
    - P1: Answer FAQs (40%)
    """
    
    strategy = generate_strategy("Resort_Manager", test_stories, total_test_cases=50)
    print(json.dumps(strategy, indent=2))
