#!/usr/bin/env python3
"""
Multi-Job Analyzer for Greenlight
Analyzes results across multiple test jobs holistically
"""

import json
from collections import defaultdict
from datetime import datetime


def load_multiple_results(result_files):
    """
    Load results from multiple test jobs
    
    Args:
        result_files: List of file paths to result JSON files
        
    Returns:
        List of result dicts
    """
    results = []
    
    for file_path in result_files:
        with open(file_path, 'r') as f:
            data = json.load(f)
            results.append(data['result'])
    
    return results


def aggregate_results(results_list, test_jobs):
    """
    Aggregate results from multiple test jobs
    
    Args:
        results_list: List of result dicts from different jobs
        test_jobs: List of test job specs (with priorities)
        
    Returns:
        Aggregated analysis dict
    """
    
    aggregated = {
        'total_jobs': len(results_list),
        'total_tests': 0,
        'completed_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'metrics': defaultdict(lambda: {'pass': 0, 'fail': 0, 'total': 0, 'scores': []}),
        'by_priority': defaultdict(lambda: {
            'tests': 0,
            'passed': 0,
            'failed': 0,
            'metrics': defaultdict(lambda: {'pass': 0, 'fail': 0, 'total': 0})
        }),
        'by_topic': defaultdict(lambda: {'pass': 0, 'fail': 0, 'total': 0}),
        'all_test_cases': [],
        'job_summaries': []
    }
    
    # Process each job
    for i, result in enumerate(results_list):
        job_info = test_jobs[i] if i < len(test_jobs) else {'priority': f'Job {i+1}', 'job_name': f'Job{i+1}'}
        priority = job_info['priority']
        
        job_summary = {
            'job_id': i + 1,
            'job_name': job_info.get('job_name', f'Job{i+1}'),
            'priority': priority,
            'total': 0,
            'passed': 0,
            'failed': 0,
            'pass_rate': 0
        }
        
        # Process test cases in this job
        for tc in result['testCases']:
            if tc['status'] != 'COMPLETED':
                continue
            
            aggregated['total_tests'] += 1
            aggregated['completed_tests'] += 1
            aggregated['by_priority'][priority]['tests'] += 1
            job_summary['total'] += 1
            
            topic = tc['generatedData'].get('topic', 'Unknown')
            aggregated['by_topic'][topic]['total'] += 1
            
            test_passed = True
            
            # Analyze metrics
            if tc.get('testResults'):
                for tr in tc['testResults']:
                    metric = tr.get('metricLabel', tr.get('name', 'unknown'))
                    result_status = tr.get('result', 'UNKNOWN')
                    score = tr.get('score')
                    
                    if metric in ['output_validation', 'completeness', 'coherence', 'conciseness']:
                        # Overall metrics
                        aggregated['metrics'][metric]['total'] += 1
                        
                        # By-priority metrics
                        aggregated['by_priority'][priority]['metrics'][metric]['total'] += 1
                        
                        if score is not None:
                            aggregated['metrics'][metric]['scores'].append(score)
                        
                        if result_status == 'PASS':
                            aggregated['metrics'][metric]['pass'] += 1
                            aggregated['by_priority'][priority]['metrics'][metric]['pass'] += 1
                        elif result_status in ['FAIL', 'FAILURE']:
                            aggregated['metrics'][metric]['fail'] += 1
                            aggregated['by_priority'][priority]['metrics'][metric]['fail'] += 1
                            test_passed = False
            
            # Track test case pass/fail
            if test_passed:
                aggregated['passed_tests'] += 1
                aggregated['by_priority'][priority]['passed'] += 1
                aggregated['by_topic'][topic]['pass'] += 1
                job_summary['passed'] += 1
            else:
                aggregated['failed_tests'] += 1
                aggregated['by_priority'][priority]['failed'] += 1
                aggregated['by_topic'][topic]['fail'] += 1
                job_summary['failed'] += 1
            
            # Store test case
            aggregated['all_test_cases'].append({
                'job_id': i + 1,
                'job_name': job_info.get('job_name'),
                'priority': priority,
                'test_number': tc['testNumber'],
                'utterance': tc['inputs']['utterance'],
                'topic': topic,
                'passed': test_passed,
                'results': tc.get('testResults', [])
            })
        
        # Calculate job pass rate
        if job_summary['total'] > 0:
            job_summary['pass_rate'] = (job_summary['passed'] / job_summary['total']) * 100
        
        aggregated['job_summaries'].append(job_summary)
    
    # Calculate overall pass rate
    total_metrics = sum(m['total'] for m in aggregated['metrics'].values())
    total_passed = sum(m['pass'] for m in aggregated['metrics'].values())
    aggregated['overall_pass_rate'] = (total_passed / total_metrics * 100) if total_metrics > 0 else 0
    
    return aggregated


def generate_holistic_report(agent_name, strategy, priorities, aggregated_analysis, org_alias):
    """
    Generate comprehensive report analyzing all test jobs holistically
    
    Args:
        agent_name: Name of the agent
        strategy: Implementation strategy
        priorities: List of test priorities
        aggregated_analysis: Aggregated results from all jobs
        org_alias: Salesforce org alias
        
    Returns:
        Markdown formatted comprehensive report
    """
    
    report = []
    
    # Header
    report.append(f"# 🚦 Greenlight Report: {agent_name}\n")
    report.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    report.append(f"\n**Org:** {org_alias}")
    report.append(f"\n**Total Test Jobs:** {aggregated_analysis['total_jobs']}")
    report.append(f"\n**Total Test Cases:** {aggregated_analysis['total_tests']}")
    report.append(f"\n**Status:** COMPLETED\n")
    report.append("\n---\n")
    
    # Executive Summary
    report.append(generate_executive_summary_multi(aggregated_analysis))
    
    # Agent Overview
    report.append("\n## 🎯 Agent Overview\n")
    report.append(f"**Agent Name:** {agent_name}\n")
    report.append(f"\n**Implementation Strategy:**\n{strategy}\n")
    report.append(f"\n**Test Priorities:**")
    for i, p in enumerate(priorities, 1):
        report.append(f"\n{i}. {p}")
    
    # Test Plan
    report.append("\n\n## 📋 Test Plan Execution\n")
    report.append(generate_test_plan_section(aggregated_analysis))
    
    # Overall Performance
    report.append("\n## 📈 Overall Performance (All Jobs)\n")
    report.append(generate_overall_performance(aggregated_analysis))
    
    # Per-Priority Analysis
    report.append("\n## 🎯 Performance by Priority\n")
    report.append(generate_priority_analysis(aggregated_analysis))
    
    # Topic Analysis
    report.append("\n## 🏷️ Performance by Topic\n")
    report.append(generate_topic_performance(aggregated_analysis))
    
    # Pass Patterns
    report.append("\n## ✅ Pass Pattern Analysis\n")
    report.append(generate_pass_patterns_multi(aggregated_analysis))
    
    # Failure Patterns
    report.append("\n## ❌ Failure Pattern Analysis\n")
    report.append(generate_failure_patterns_multi(aggregated_analysis))
    
    # Recommendations
    report.append("\n## 💡 Recommendations\n")
    report.append(generate_recommendations_multi(aggregated_analysis))
    
    # Detailed Results
    report.append("\n## 📑 Detailed Test Results (All Jobs)\n")
    report.append(generate_detailed_results_multi(aggregated_analysis))
    
    # Next Steps
    report.append("\n## 🚀 Next Steps\n")
    report.append(generate_next_steps_multi(agent_name, aggregated_analysis))
    
    # Footer
    report.append("\n---\n")
    report.append(f"\n**Report Generated:** {datetime.now().isoformat()}")
    report.append(f"\n**Tool:** Greenlight v1.1.0 (MVP)")
    report.append(f"\n**Jobs Analyzed:** {aggregated_analysis['total_jobs']}")
    
    return '\n'.join(report)


def generate_executive_summary_multi(analysis):
    """Generate executive summary for multi-job analysis"""
    
    pass_rate = analysis['overall_pass_rate']
    
    if pass_rate >= 85:
        recommendation = "✅ **READY FOR GO-LIVE**"
        status = "🟢 Agent meets quality threshold"
    elif pass_rate >= 70:
        recommendation = "⚠️  **CONDITIONAL GO-LIVE**"
        status = "🟡 Agent shows acceptable performance with improvements needed"
    else:
        recommendation = "❌ **NOT READY FOR GO-LIVE**"
        status = "🔴 Agent requires significant improvements"
    
    summary = [
        "## 📊 Executive Summary\n",
        f"**Overall Pass Rate:** {pass_rate:.1f}%\n",
        f"\n**Recommendation:** {recommendation}\n",
        f"\n**Status:** {status}\n",
        "\n### Key Findings\n"
    ]
    
    # Find weakest and strongest metrics
    if analysis['metrics']:
        weakest = min(analysis['metrics'].items(), 
                     key=lambda x: (x[1]['pass'] / x[1]['total']) if x[1]['total'] > 0 else 1)
        strongest = max(analysis['metrics'].items(),
                       key=lambda x: (x[1]['pass'] / x[1]['total']) if x[1]['total'] > 0 else 0)
        
        weakest_rate = (weakest[1]['pass'] / weakest[1]['total'] * 100) if weakest[1]['total'] > 0 else 0
        strongest_rate = (strongest[1]['pass'] / strongest[1]['total'] * 100) if strongest[1]['total'] > 0 else 0
        
        summary.append(f"\n- **Weakest Area:** {weakest[0].replace('_', ' ').title()} ({weakest_rate:.1f}% pass rate)")
        summary.append(f"\n- **Strongest Area:** {strongest[0].replace('_', ' ').title()} ({strongest_rate:.1f}% pass rate)")
    
    summary.append(f"\n- **Test Jobs Completed:** {analysis['total_jobs']}")
    summary.append(f"\n- **Failed Test Cases:** {analysis['failed_tests']}/{analysis['completed_tests']} ({analysis['failed_tests']/analysis['completed_tests']*100:.0f}%)")
    
    return ''.join(summary)


def generate_test_plan_section(analysis):
    """Generate test plan execution section"""
    
    section = []
    section.append("### Jobs Executed\n")
    section.append("| Job | Priority | Test Cases | Passed | Failed | Pass Rate |")
    section.append("|-----|----------|------------|--------|--------|-----------|")
    
    for job in analysis['job_summaries']:
        status = "✅" if job['pass_rate'] >= 80 else "⚠️" if job['pass_rate'] >= 60 else "❌"
        section.append(f"| {job['job_id']} | {job['priority']} | {job['total']} | {job['passed']} | {job['failed']} | {status} {job['pass_rate']:.1f}% |")
    
    return '\n'.join(section)


def generate_overall_performance(analysis):
    """Generate overall performance section"""
    
    perf = []
    perf.append("### Aggregated Metrics (All Jobs)\n")
    perf.append("| Metric | Pass Rate | Passed | Failed | Target | Gap | Status |")
    perf.append("|--------|-----------|--------|--------|--------|-----|--------|")
    
    for metric, stats in sorted(analysis['metrics'].items()):
        if stats['total'] == 0:
            continue
        pass_rate = (stats['pass'] / stats['total'] * 100)
        target = 85
        gap = pass_rate - target
        status = "✅" if pass_rate >= target else "❌"
        
        perf.append(f"| {metric.replace('_', ' ').title()} | {pass_rate:.1f}% | {stats['pass']} | {stats['fail']} | {target}% | {gap:+.1f}% | {status} |")
    
    return '\n'.join(perf)


def generate_priority_analysis(analysis):
    """Generate per-priority analysis"""
    
    section = []
    
    for priority, stats in sorted(analysis['by_priority'].items()):
        section.append(f"\n### {priority}\n")
        section.append(f"**Test Cases:** {stats['tests']}")
        section.append(f"\n**Passed:** {stats['passed']} ({stats['passed']/stats['tests']*100:.0f}%)")
        section.append(f"\n**Failed:** {stats['failed']} ({stats['failed']/stats['tests']*100:.0f}%)\n")
        
        # Metrics for this priority
        section.append("\n**Metrics:**")
        section.append("\n| Metric | Pass Rate | Status |")
        section.append("|--------|-----------|--------|")
        
        for metric, m_stats in sorted(stats['metrics'].items()):
            if m_stats['total'] == 0:
                continue
            pass_rate = (m_stats['pass'] / m_stats['total'] * 100)
            status = "✅" if pass_rate >= 80 else "❌"
            section.append(f"| {metric.replace('_', ' ').title()} | {pass_rate:.1f}% | {status} |")
    
    return '\n'.join(section)


def generate_topic_performance(analysis):
    """Generate per-topic performance"""
    
    section = []
    
    for topic, stats in sorted(analysis['by_topic'].items(), key=lambda x: x[1]['total'], reverse=True):
        pass_rate = (stats['pass'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status = "✅" if pass_rate >= 80 else "⚠️" if pass_rate >= 60 else "❌"
        
        section.append(f"\n### {topic}\n")
        section.append(f"**Pass Rate:** {status} {pass_rate:.1f}% ({stats['pass']}/{stats['total']})")
        
        if pass_rate >= 85:
            section.append(f"\n**Recommendation:** Performing well, maintain quality")
        elif pass_rate >= 70:
            section.append(f"\n**Recommendation:** Review failed cases and improve")
        else:
            section.append(f"\n**Recommendation:** Priority fix - update knowledge base and instructions")
    
    return '\n'.join(section)


def generate_pass_patterns_multi(analysis):
    """Generate pass patterns across all jobs"""
    
    patterns = []
    patterns.append("### What's Working Well Across All Jobs\n")
    
    # Find strong metrics
    strong_metrics = [(m, s) for m, s in analysis['metrics'].items()
                     if s['total'] > 0 and (s['pass'] / s['total'] * 100) >= 80]
    
    if strong_metrics:
        for metric, stats in sorted(strong_metrics, key=lambda x: x[1]['pass']/x[1]['total'], reverse=True):
            pass_rate = (stats['pass'] / stats['total'] * 100)
            patterns.append(f"\n**{metric.replace('_', ' ').title()} ({pass_rate:.1f}%)**")
            patterns.append(f"\n- Consistently strong across all test jobs")
            patterns.append(f"\n- {stats['pass']} out of {stats['total']} tests passed")
    
    # Sample passed tests
    passed_tests = [tc for tc in analysis['all_test_cases'] if tc['passed']]
    if passed_tests:
        patterns.append("\n\n### Sample Successful Test Cases\n")
        for tc in passed_tests[:5]:
            patterns.append(f"\n- **Job {tc['job_id']}** ({tc['priority']}): {tc['utterance'][:80]}...")
    
    return '\n'.join(patterns)


def generate_failure_patterns_multi(analysis):
    """Generate failure patterns across all jobs"""
    
    patterns = []
    patterns.append("### What's Failing Across Jobs\n")
    
    # Find weak metrics
    weak_metrics = [(m, s) for m, s in analysis['metrics'].items()
                   if s['total'] > 0 and (s['pass'] / s['total'] * 100) < 80]
    
    if weak_metrics:
        for metric, stats in sorted(weak_metrics, key=lambda x: x[1]['pass']/x[1]['total']):
            pass_rate = (stats['pass'] / stats['total'] * 100)
            patterns.append(f"\n**{metric.replace('_', ' ').title()} ({pass_rate:.1f}%)**")
            patterns.append(f"\n- {stats['fail']} out of {stats['total']} tests failed")
            patterns.append(f"\n- Gap to target: {85 - pass_rate:.1f}%")
    
    # Top failures across all jobs
    failed_tests = [tc for tc in analysis['all_test_cases'] if not tc['passed']]
    if failed_tests:
        patterns.append("\n\n### Top Failed Test Cases (Across All Jobs)\n")
        for i, tc in enumerate(failed_tests[:10], 1):
            patterns.append(f"\n**{i}. Job {tc['job_id']}** ({tc['priority']})")
            patterns.append(f"\n- Utterance: {tc['utterance']}")
            patterns.append(f"\n- Topic: {tc['topic']}")
    
    # Cross-job patterns
    patterns.append("\n\n### Cross-Job Patterns\n")
    
    # Check if certain priorities perform worse
    if analysis['by_priority']:
        patterns.append("\n**Performance by Priority:**")
        for priority, stats in sorted(analysis['by_priority'].items(), 
                                     key=lambda x: x[1]['passed']/x[1]['tests'] if x[1]['tests'] > 0 else 0):
            pass_rate = (stats['passed'] / stats['tests'] * 100) if stats['tests'] > 0 else 0
            patterns.append(f"\n- {priority}: {pass_rate:.1f}% pass rate")
    
    return '\n'.join(patterns)


def generate_recommendations_multi(analysis):
    """Generate recommendations based on multi-job analysis"""
    
    recs = []
    recs.append("### Immediate Actions (Critical)\n")
    
    # Find top issues
    if analysis['metrics']:
        weakest = min(analysis['metrics'].items(),
                     key=lambda x: (x[1]['pass'] / x[1]['total']) if x[1]['total'] > 0 else 1)
        weakest_rate = (weakest[1]['pass'] / weakest[1]['total'] * 100) if weakest[1]['total'] > 0 else 0
        
        recs.append(f"\n1. **Fix {weakest[0].replace('_', ' ').title()}** (Currently {weakest_rate:.1f}%)")
        recs.append(f"\n   - This is the weakest metric across all test jobs")
        recs.append(f"\n   - Need {85 - weakest_rate:.1f}% improvement to reach threshold")
    
    recs.append(f"\n\n2. **Address Top {min(10, analysis['failed_tests'])} Failed Test Cases**")
    recs.append(f"\n   - Focus on failures that appear across multiple jobs")
    recs.append(f"\n   - These indicate systemic issues")
    
    recs.append("\n\n3. **Update Knowledge Base**")
    recs.append("\n   - Review articles for completeness")
    recs.append("\n   - Add missing information from failed tests")
    
    # Priority-specific recommendations
    if analysis['by_priority']:
        worst_priority = min(analysis['by_priority'].items(),
                           key=lambda x: x[1]['passed']/x[1]['tests'] if x[1]['tests'] > 0 else 1)
        worst_rate = (worst_priority[1]['passed'] / worst_priority[1]['tests'] * 100) if worst_priority[1]['tests'] > 0 else 0
        
        if worst_rate < 70:
            recs.append(f"\n\n4. **Focus on '{worst_priority[0]}' Priority**")
            recs.append(f"\n   - This priority has the lowest pass rate ({worst_rate:.1f}%)")
            recs.append(f"\n   - Review agent instructions for this use case")
    
    # Timeline
    recs.append("\n\n### Recommended Timeline\n")
    recs.append("\n- **Week 1:** Fix critical failures and update knowledge base")
    recs.append("\n- **Week 2:** Re-run all test jobs and validate improvements")
    recs.append("\n- **Week 3:** Expand test coverage and add edge cases")
    recs.append("\n- **Week 4:** Final validation and go-live decision")
    
    return '\n'.join(recs)


def generate_detailed_results_multi(analysis):
    """Generate detailed results table for all jobs"""
    
    details = []
    details.append("### All Test Cases (Grouped by Job)\n")
    
    # Group by job
    by_job = defaultdict(list)
    for tc in analysis['all_test_cases']:
        by_job[tc['job_id']].append(tc)
    
    for job_id in sorted(by_job.keys()):
        test_cases = by_job[job_id]
        job_name = test_cases[0]['job_name'] if test_cases else f'Job {job_id}'
        priority = test_cases[0]['priority'] if test_cases else 'N/A'
        
        details.append(f"\n#### Job {job_id}: {priority}\n")
        details.append("| Test # | Status | Utterance | Topic |")
        details.append("|--------|--------|-----------|-------|")
        
        for tc in test_cases:
            status = "✅" if tc['passed'] else "❌"
            utterance = tc['utterance'][:60] + "..." if len(tc['utterance']) > 60 else tc['utterance']
            topic = tc['topic'][:30]
            
            details.append(f"| {tc['test_number']} | {status} | {utterance} | {topic} |")
    
    return '\n'.join(details)


def generate_next_steps_multi(agent_name, analysis):
    """Generate next steps for multi-job testing"""
    
    steps = []
    steps.append("### To Improve Agent Performance\n")
    steps.append("\n1. **Review Failure Patterns**")
    steps.append("\n   - Focus on issues appearing across multiple jobs")
    steps.append("\n   - These indicate systemic problems")
    
    steps.append("\n\n2. **Make Targeted Improvements**")
    steps.append(f"\n   - Address the {min(10, analysis['failed_tests'])} highest-priority failures")
    steps.append("\n   - Update knowledge base and agent instructions")
    
    steps.append("\n\n3. **Re-run All Test Jobs**")
    steps.append("\n   ```bash")
    
    for job in analysis['job_summaries']:
        steps.append(f"\n   sf agent test run --api-name \"{job['job_name']}\" --target-org your-org --json &")
    
    steps.append("\n   wait")
    steps.append("\n   ```")
    
    steps.append("\n\n4. **Compare Results**")
    steps.append("\n   - Generate new Greenlight report")
    steps.append("\n   - Compare to this baseline")
    steps.append(f"\n   - Target: {85 - analysis['overall_pass_rate']:.1f}% improvement")
    
    return '\n'.join(steps)


if __name__ == '__main__':
    print("Multi-Job Analyzer for Greenlight")
    print("\nUsage:")
    print("  from multi_job_analyzer import aggregate_results, generate_holistic_report")
    print("  analysis = aggregate_results(results_list, test_jobs)")
    print("  report = generate_holistic_report(agent, strategy, priorities, analysis, org)")
