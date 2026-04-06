#!/usr/bin/env python3
"""
Comprehensive Report Generator for Greenlight
Generates a single consolidated report with all analysis
"""

import json
from datetime import datetime
from collections import defaultdict


def generate_comprehensive_report(agent_name, strategy, priorities, results_data, org_alias):
    """
    Generate single comprehensive Greenlight report
    
    Args:
        agent_name: Name of the agent being tested
        strategy: User-provided implementation strategy
        priorities: List of test priorities from user
        results_data: Complete test results from Salesforce
        org_alias: Salesforce org alias
        
    Returns:
        Markdown formatted comprehensive report
    """
    
    result = results_data['result']
    test_cases = result['testCases']
    
    # Analyze results
    analysis = analyze_results(test_cases)
    
    # Build report
    report = []
    
    # Header
    report.append(f"# 🚦 Greenlight Report: {agent_name}")
    report.append(f"\n**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    report.append(f"**Org:** {org_alias}")
    report.append(f"**Test Run ID:** {result.get('runId', 'N/A')}")
    report.append(f"**Status:** {result['status']}")
    report.append("\n---\n")
    
    # Executive Summary
    report.append("## 📊 Executive Summary\n")
    report.append(generate_executive_summary(analysis, agent_name))
    
    # Agent Overview
    report.append("\n## 🎯 Agent Overview\n")
    report.append(generate_agent_overview(agent_name, strategy, priorities, analysis))
    
    # Test Plan
    report.append("\n## 📋 Test Plan\n")
    report.append(generate_test_plan(priorities, analysis))
    
    # Overall Performance
    report.append("\n## 📈 Overall Performance\n")
    report.append(generate_performance_section(analysis))
    
    # Topic-Level Analysis
    report.append("\n## 🎯 Topic-Level Analysis\n")
    report.append(generate_topic_analysis(analysis))
    
    # Pass Pattern Analysis
    report.append("\n## ✅ Pass Pattern Analysis\n")
    report.append(generate_pass_patterns(analysis, test_cases))
    
    # Failure Pattern Analysis
    report.append("\n## ❌ Failure Pattern Analysis\n")
    report.append(generate_failure_patterns(analysis, test_cases))
    
    # Recommendations
    report.append("\n## 💡 Recommendations\n")
    report.append(generate_recommendations(analysis))
    
    # Detailed Test Results
    report.append("\n## 📑 Detailed Test Results\n")
    report.append(generate_detailed_results(test_cases))
    
    # Next Steps
    report.append("\n## 🚀 Next Steps\n")
    report.append(generate_next_steps(agent_name, analysis))
    
    # Footer
    report.append("\n---\n")
    report.append(f"\n**Report Generated:** {datetime.now().isoformat()}")
    report.append(f"\n**Tool:** Greenlight v1.0.0 (MVP)")
    report.append(f"\n**Framework:** Agentforce Testing Orchestrator")
    
    return '\n'.join(report)


def analyze_results(test_cases):
    """Analyze test results and extract key metrics"""
    
    analysis = {
        'total_tests': len(test_cases),
        'completed_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'metrics': defaultdict(lambda: {'pass': 0, 'fail': 0, 'total': 0, 'scores': []}),
        'topics': defaultdict(lambda: {'pass': 0, 'fail': 0, 'total': 0}),
        'passed_test_cases': [],
        'failed_test_cases': [],
        'failure_patterns': defaultdict(list),
        'pass_patterns': defaultdict(list)
    }
    
    for tc in test_cases:
        if tc['status'] != 'COMPLETED':
            continue
            
        analysis['completed_tests'] += 1
        
        test_passed = True
        topic = tc['generatedData'].get('topic', 'Unknown')
        analysis['topics'][topic]['total'] += 1
        
        if tc.get('testResults'):
            for tr in tc['testResults']:
                metric = tr.get('metricLabel', tr.get('name', 'unknown'))
                result_status = tr.get('result', 'UNKNOWN')
                score = tr.get('score')
                
                if metric in ['output_validation', 'completeness', 'coherence', 'conciseness']:
                    analysis['metrics'][metric]['total'] += 1
                    
                    if score is not None:
                        analysis['metrics'][metric]['scores'].append(score)
                    
                    if result_status == 'PASS':
                        analysis['metrics'][metric]['pass'] += 1
                    elif result_status in ['FAIL', 'FAILURE']:
                        analysis['metrics'][metric]['fail'] += 1
                        test_passed = False
                        
                        # Record failure pattern
                        analysis['failure_patterns'][metric].append({
                            'test': tc['testNumber'],
                            'utterance': tc['inputs']['utterance'],
                            'topic': topic,
                            'score': score,
                            'explanation': tr.get('metricExplainability', '')
                        })
        
        # Track pass/fail
        if test_passed:
            analysis['passed_tests'] += 1
            analysis['topics'][topic]['pass'] += 1
            analysis['passed_test_cases'].append({
                'number': tc['testNumber'],
                'utterance': tc['inputs']['utterance'],
                'topic': topic
            })
        else:
            analysis['failed_tests'] += 1
            analysis['topics'][topic]['fail'] += 1
            analysis['failed_test_cases'].append({
                'number': tc['testNumber'],
                'utterance': tc['inputs']['utterance'],
                'topic': topic
            })
    
    # Calculate overall pass rate
    total_metrics = sum(m['total'] for m in analysis['metrics'].values())
    total_passed = sum(m['pass'] for m in analysis['metrics'].values())
    analysis['overall_pass_rate'] = (total_passed / total_metrics * 100) if total_metrics > 0 else 0
    
    return analysis


def generate_executive_summary(analysis, agent_name):
    """Generate executive summary section"""
    
    pass_rate = analysis['overall_pass_rate']
    
    # Determine recommendation
    if pass_rate >= 85:
        recommendation = "✅ **READY FOR GO-LIVE**"
        status_icon = "🟢"
    elif pass_rate >= 70:
        recommendation = "⚠️  **CONDITIONAL GO-LIVE**"
        status_icon = "🟡"
    else:
        recommendation = "❌ **NOT READY FOR GO-LIVE**"
        status_icon = "🔴"
    
    summary = []
    summary.append(f"**Overall Pass Rate:** {pass_rate:.1f}%")
    summary.append(f"\n**Recommendation:** {recommendation}")
    summary.append(f"\n**Status:** {status_icon} {get_status_description(pass_rate)}")
    
    # Key findings
    summary.append("\n\n### Key Findings\n")
    
    # Find weakest metric
    weakest_metric = min(analysis['metrics'].items(), 
                        key=lambda x: (x[1]['pass'] / x[1]['total'] * 100) if x[1]['total'] > 0 else 100)
    weakest_rate = (weakest_metric[1]['pass'] / weakest_metric[1]['total'] * 100) if weakest_metric[1]['total'] > 0 else 0
    
    # Find strongest metric
    strongest_metric = max(analysis['metrics'].items(),
                          key=lambda x: (x[1]['pass'] / x[1]['total'] * 100) if x[1]['total'] > 0 else 0)
    strongest_rate = (strongest_metric[1]['pass'] / strongest_metric[1]['total'] * 100) if strongest_metric[1]['total'] > 0 else 0
    
    summary.append(f"- **Weakest Area:** {weakest_metric[0].replace('_', ' ').title()} ({weakest_rate:.1f}% pass rate)")
    summary.append(f"- **Strongest Area:** {strongest_metric[0].replace('_', ' ').title()} ({strongest_rate:.1f}% pass rate)")
    summary.append(f"- **Failed Test Cases:** {analysis['failed_tests']}/{analysis['completed_tests']} ({analysis['failed_tests']/analysis['completed_tests']*100:.0f}%)")
    
    return '\n'.join(summary)


def get_status_description(pass_rate):
    """Get status description based on pass rate"""
    if pass_rate >= 85:
        return "Agent meets quality threshold for production"
    elif pass_rate >= 70:
        return "Agent shows acceptable performance with areas to improve"
    else:
        return "Agent requires significant improvements"


def generate_agent_overview(agent_name, strategy, priorities, analysis):
    """Generate agent overview section"""
    
    overview = []
    overview.append(f"**Agent Name:** {agent_name}")
    overview.append(f"\n**Implementation Strategy:**")
    overview.append(f"\n{strategy}")
    
    overview.append(f"\n\n**Test Priorities:**")
    for i, priority in enumerate(priorities, 1):
        overview.append(f"\n{i}. {priority}")
    
    # Topics covered
    overview.append(f"\n\n**Topics Covered:** {len(analysis['topics'])}")
    for topic, stats in analysis['topics'].items():
        pass_rate = (stats['pass'] / stats['total'] * 100) if stats['total'] > 0 else 0
        overview.append(f"\n- `{topic}`: {stats['total']} tests ({pass_rate:.0f}% pass rate)")
    
    return '\n'.join(overview)


def generate_test_plan(priorities, analysis):
    """Generate test plan section"""
    
    plan = []
    plan.append(f"**Total Test Cases:** {analysis['completed_tests']}")
    plan.append(f"\n**Test Coverage:**")
    
    # Coverage by topic
    for topic, stats in analysis['topics'].items():
        percentage = (stats['total'] / analysis['completed_tests'] * 100) if analysis['completed_tests'] > 0 else 0
        plan.append(f"\n- {topic}: {stats['total']} tests ({percentage:.0f}%)")
    
    return '\n'.join(plan)


def generate_performance_section(analysis):
    """Generate overall performance section"""
    
    perf = []
    perf.append("### Metrics Breakdown\n")
    perf.append("| Metric | Pass Rate | Passed | Failed | Target | Status |")
    perf.append("|--------|-----------|--------|--------|--------|--------|")
    
    for metric, stats in sorted(analysis['metrics'].items()):
        if stats['total'] == 0:
            continue
        pass_rate = (stats['pass'] / stats['total'] * 100)
        target = 85
        status = "✅" if pass_rate >= target else "❌"
        
        perf.append(f"| {metric.replace('_', ' ').title()} | {pass_rate:.1f}% | {stats['pass']} | {stats['fail']} | {target}% | {status} |")
    
    # Visual progress bars
    perf.append("\n### Visual Performance\n")
    for metric, stats in sorted(analysis['metrics'].items()):
        if stats['total'] == 0:
            continue
        pass_rate = (stats['pass'] / stats['total'] * 100)
        bar = create_progress_bar(pass_rate, 85)
        perf.append(f"\n**{metric.replace('_', ' ').title()}**")
        perf.append(f"\n```\n{bar}\n```")
    
    return '\n'.join(perf)


def create_progress_bar(current, target, width=50):
    """Create ASCII progress bar"""
    current_blocks = int((current / 100) * width)
    target_blocks = int((target / 100) * width)
    
    bar = f"Current: {current:5.1f}% [{'█' * current_blocks}{'░' * (width - current_blocks)}]\n"
    bar += f"Target:  {target:5.1f}% [{'█' * target_blocks}{'░' * (width - target_blocks)}]"
    
    return bar


def generate_topic_analysis(analysis):
    """Generate topic-level analysis"""
    
    topic_section = []
    
    for topic, stats in sorted(analysis['topics'].items(), key=lambda x: x[1]['total'], reverse=True):
        pass_rate = (stats['pass'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        topic_section.append(f"\n### {topic}\n")
        topic_section.append(f"**Pass Rate:** {pass_rate:.1f}% ({stats['pass']}/{stats['total']})")
        
        if pass_rate >= 85:
            topic_section.append(f"\n**Status:** ✅ Meets threshold")
            topic_section.append(f"\n**Recommendation:** Topic performing well, maintain current quality")
        elif pass_rate >= 70:
            topic_section.append(f"\n**Status:** ⚠️  Needs improvement")
            topic_section.append(f"\n**Recommendation:** Review failed test cases and refine responses")
        else:
            topic_section.append(f"\n**Status:** ❌ Requires attention")
            topic_section.append(f"\n**Recommendation:** Priority fix - update knowledge base and agent instructions")
    
    return '\n'.join(topic_section)


def generate_pass_patterns(analysis, test_cases):
    """Generate pass pattern analysis"""
    
    patterns = []
    patterns.append("### What's Working Well\n")
    
    # Find metrics with high pass rates
    strong_metrics = [(m, s) for m, s in analysis['metrics'].items() 
                     if s['total'] > 0 and (s['pass'] / s['total'] * 100) >= 80]
    
    if strong_metrics:
        for metric, stats in sorted(strong_metrics, key=lambda x: x[1]['pass']/x[1]['total'], reverse=True):
            pass_rate = (stats['pass'] / stats['total'] * 100)
            patterns.append(f"\n**{metric.replace('_', ' ').title()} ({pass_rate:.1f}%)**")
            patterns.append(f"\n- Agent consistently performs well in this area")
            patterns.append(f"- {stats['pass']} out of {stats['total']} tests passed")
    
    # Show sample passed tests
    patterns.append("\n\n### Sample Successful Test Cases\n")
    for tc in analysis['passed_test_cases'][:5]:
        patterns.append(f"\n- Test #{tc['number']}: {tc['utterance'][:80]}...")
    
    return '\n'.join(patterns)


def generate_failure_patterns(analysis, test_cases):
    """Generate failure pattern analysis"""
    
    patterns = []
    patterns.append("### What's Failing\n")
    
    # Find metrics with low pass rates
    weak_metrics = [(m, s) for m, s in analysis['metrics'].items()
                   if s['total'] > 0 and (s['pass'] / s['total'] * 100) < 80]
    
    if weak_metrics:
        for metric, stats in sorted(weak_metrics, key=lambda x: x[1]['pass']/x[1]['total']):
            pass_rate = (stats['pass'] / stats['total'] * 100)
            patterns.append(f"\n**{metric.replace('_', ' ').title()} ({pass_rate:.1f}%)**")
            patterns.append(f"\n- {stats['fail']} out of {stats['total']} tests failed")
            patterns.append(f"- Gap to target: {85 - pass_rate:.1f}%")
    
    # Show top failure examples
    patterns.append("\n\n### Top 5 Failed Test Cases\n")
    for i, tc in enumerate(analysis['failed_test_cases'][:5], 1):
        patterns.append(f"\n**{i}. Test #{tc['number']}**")
        patterns.append(f"\n- Utterance: {tc['utterance']}")
        patterns.append(f"- Topic: {tc['topic']}")
    
    # Root causes
    patterns.append("\n\n### Common Root Causes\n")
    patterns.append("\n1. **Knowledge Base Issues** - Articles may be incomplete or outdated")
    patterns.append("\n2. **Agent Instructions** - May be too general or lack specific guidance")
    patterns.append("\n3. **Response Quality** - Responses may be too verbose or missing key information")
    
    return '\n'.join(patterns)


def generate_recommendations(analysis):
    """Generate recommendations section"""
    
    recs = []
    
    # Immediate actions
    recs.append("### Immediate Actions (Critical)\n")
    recs.append("\n1. **Address Top Failed Test Cases**")
    recs.append(f"\n   - Review and fix the {min(10, len(analysis['failed_test_cases']))} highest-priority failures")
    recs.append(f"\n   - Focus on tests that failed multiple metrics")
    
    # Find weakest metric
    if analysis['metrics']:
        weakest = min(analysis['metrics'].items(), 
                     key=lambda x: (x[1]['pass'] / x[1]['total']) if x[1]['total'] > 0 else 1)
        weakest_rate = (weakest[1]['pass'] / weakest[1]['total'] * 100) if weakest[1]['total'] > 0 else 0
        
        recs.append(f"\n\n2. **Improve {weakest[0].replace('_', ' ').title()}** (Currently {weakest_rate:.1f}%)")
        recs.append(f"\n   - Target: 85%+ pass rate")
        recs.append(f"\n   - Gap: {85 - weakest_rate:.1f}% improvement needed")
    
    recs.append("\n\n3. **Update Knowledge Base**")
    recs.append("\n   - Review articles for completeness and accuracy")
    recs.append("\n   - Add missing information identified in failed tests")
    
    # Short-term
    recs.append("\n\n### Short-Term Improvements\n")
    recs.append("\n1. **Refine Agent Instructions**")
    recs.append("\n   - Add specific examples of good responses")
    recs.append("\n   - Clarify expected response format")
    
    recs.append("\n\n2. **Expand Test Coverage**")
    recs.append(f"\n   - Current: {len(analysis['topics'])} topics tested")
    recs.append("\n   - Add edge cases and error scenarios")
    
    recs.append("\n\n3. **Re-test After Fixes**")
    recs.append("\n   - Run same test suite to measure improvement")
    recs.append("\n   - Track progress toward 85% threshold")
    
    # Long-term
    recs.append("\n\n### Long-Term Strategy\n")
    recs.append("\n1. **Continuous Testing**")
    recs.append("\n   - Schedule regular test runs (weekly/bi-weekly)")
    recs.append("\n   - Monitor trends over time")
    
    recs.append("\n\n2. **User Feedback Integration**")
    recs.append("\n   - Collect real user feedback")
    recs.append("\n   - Create tests from common issues")
    
    recs.append("\n\n3. **Gradual Rollout**")
    recs.append("\n   - Consider pilot with limited users")
    recs.append("\n   - Expand as metrics improve")
    
    return '\n'.join(recs)


def generate_detailed_results(test_cases):
    """Generate detailed test results table"""
    
    details = []
    details.append("### All Test Cases\n")
    details.append("| Test # | Status | Utterance | Topic | Metrics Passed |")
    details.append("|--------|--------|-----------|-------|----------------|")
    
    for tc in test_cases:
        if tc['status'] != 'COMPLETED':
            continue
        
        status = "✅" if any(tr.get('result') == 'PASS' for tr in tc.get('testResults', [])) else "❌"
        utterance = tc['inputs']['utterance'][:50] + "..." if len(tc['inputs']['utterance']) > 50 else tc['inputs']['utterance']
        topic = tc['generatedData'].get('topic', 'Unknown')[:30]
        
        # Count passed metrics
        passed = sum(1 for tr in tc.get('testResults', []) if tr.get('result') == 'PASS')
        total = len([tr for tr in tc.get('testResults', []) if tr.get('result') in ['PASS', 'FAIL', 'FAILURE']])
        
        details.append(f"| {tc['testNumber']} | {status} | {utterance} | {topic} | {passed}/{total} |")
    
    return '\n'.join(details)


def generate_next_steps(agent_name, analysis):
    """Generate next steps section"""
    
    steps = []
    steps.append("### To Improve Agent Performance\n")
    steps.append("\n1. **Review This Report**")
    steps.append("\n   - Focus on Failure Pattern Analysis section")
    steps.append("\n   - Identify top 5-10 issues to address")
    
    steps.append("\n\n2. **Make Improvements**")
    steps.append("\n   - Update knowledge articles")
    steps.append("\n   - Refine agent instructions")
    steps.append("\n   - Fix identified issues")
    
    steps.append("\n\n3. **Re-run Test**")
    steps.append(f"\n   ```bash")
    steps.append(f"\n   sf agent test run --api-name \"{agent_name}_Test\" --target-org your-org")
    steps.append(f"\n   ```")
    
    steps.append("\n\n4. **Generate New Report**")
    steps.append("\n   - Compare results to this baseline")
    steps.append("\n   - Track improvement trends")
    steps.append(f"\n   - Target: {85 - analysis['overall_pass_rate']:.1f}% improvement needed")
    
    steps.append("\n\n### Timeline Suggestion\n")
    steps.append("\n- **Week 1:** Address critical failures")
    steps.append("\n- **Week 2:** Re-test and validate improvements")
    steps.append("\n- **Week 3:** Expand test coverage")
    steps.append("\n- **Week 4:** Final validation and go-live decision")
    
    return '\n'.join(steps)


if __name__ == '__main__':
    print("Comprehensive Report Generator for Greenlight")
    print("This module generates a single consolidated report.")
    print("\nUsage:")
    print("  from comprehensive_report_generator import generate_comprehensive_report")
    print("  report = generate_comprehensive_report(agent_name, strategy, priorities, results, org)")
