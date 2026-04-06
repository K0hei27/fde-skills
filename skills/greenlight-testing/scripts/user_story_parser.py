"""
User Story Parser for Greenlight Skill
Parses markdown user stories with priorities and weights
"""

import re
import json
from typing import List, Dict, Optional


def parse_user_stories(markdown_text: str) -> List[Dict]:
    """
    Parse user stories from markdown format.
    
    Expected format:
    - P0: Story description (60%)
    - P1: Another story (40%)
    - P2: Third story
    
    Args:
        markdown_text: Markdown text with user stories
        
    Returns:
        List of dicts with priority, description, and weight
    """
    stories = []
    lines = markdown_text.strip().split('\n')
    
    # Pattern: - P0: Description (optional weight%)
    pattern = r'^-\s*(P[0-2]):\s*(.+?)(?:\s*\((\d+)%\))?$'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = re.match(pattern, line)
        if match:
            priority = match.group(1)
            description = match.group(2).strip()
            weight_str = match.group(3)
            
            story = {
                'priority': priority,
                'description': description,
                'weight': float(weight_str) / 100 if weight_str else None
            }
            stories.append(story)
    
    return stories


def auto_calculate_weights(stories: List[Dict]) -> List[Dict]:
    """
    Auto-calculate weights if not provided.
    Uses priority_weights from config: P0=50%, P1=30%, P2=20%
    
    Args:
        stories: List of story dicts
        
    Returns:
        Stories with weights calculated
    """
    # Load default weights
    default_weights = {
        'P0': 0.5,
        'P1': 0.3,
        'P2': 0.2
    }
    
    # Check if any weights are missing
    has_missing = any(s['weight'] is None for s in stories)
    has_provided = any(s['weight'] is not None for s in stories)
    
    if has_missing and not has_provided:
        # All weights missing - use auto-calculation
        priority_counts = {'P0': 0, 'P1': 0, 'P2': 0}
        for story in stories:
            priority_counts[story['priority']] += 1
        
        # Calculate weight per story for each priority
        total_weight = 0
        for story in stories:
            priority = story['priority']
            count = priority_counts[priority]
            if count > 0:
                story['weight'] = default_weights[priority] / count
                total_weight += story['weight']
        
        # Normalize to ensure sum = 1.0
        if total_weight > 0:
            for story in stories:
                story['weight'] = story['weight'] / total_weight
                
    elif has_missing and has_provided:
        # Some weights provided, some missing - distribute remaining
        provided_total = sum(s['weight'] for s in stories if s['weight'] is not None)
        remaining = 1.0 - provided_total
        missing_count = sum(1 for s in stories if s['weight'] is None)
        
        if missing_count > 0:
            weight_per_missing = remaining / missing_count
            for story in stories:
                if story['weight'] is None:
                    story['weight'] = weight_per_missing
    
    return stories


def validate_weights(stories: List[Dict]) -> bool:
    """
    Validate that weights sum to approximately 1.0 (100%)
    
    Args:
        stories: List of story dicts with weights
        
    Returns:
        True if valid, False otherwise
    """
    total = sum(s['weight'] for s in stories if s['weight'] is not None)
    return abs(total - 1.0) < 0.01  # Allow 1% tolerance


if __name__ == '__main__':
    # Test the parser
    test_input = """
    - P0: Check order status (60%)
    - P1: Answer FAQs (40%)
    """
    
    print("Testing User Story Parser")
    print("=" * 50)
    
    stories = parse_user_stories(test_input)
    print(f"\nParsed {len(stories)} stories:")
    print(json.dumps(stories, indent=2))
    
    print(f"\nWeights valid: {validate_weights(stories)}")
    
    # Test auto-calculation
    test_input_no_weights = """
    - P0: Critical task
    - P1: Important task
    - P2: Nice to have
    """
    
    print("\n" + "=" * 50)
    print("Testing Auto-Weight Calculation")
    print("=" * 50)
    
    stories2 = parse_user_stories(test_input_no_weights)
    stories2 = auto_calculate_weights(stories2)
    print(f"\nParsed {len(stories2)} stories with auto-weights:")
    print(json.dumps(stories2, indent=2))
    
    print(f"\nWeights valid: {validate_weights(stories2)}")
    print(f"Total weight: {sum(s['weight'] for s in stories2):.2f}")
