import { LightningElement, track } from 'lwc';

// TEST_RESULTS will be populated by /greenlight-dashboard skill
// This is sample data structure - replace with actual test results
const TEST_RESULTS = {
    agentName: "Your_Agent_Name",
    agentLabel: "Agent Label",
    version: "v1",
    org: "your-org-alias",
    timestamp: new Date().toISOString(),
    goLiveStatus: "CONDITIONAL",
    summary: {
        totalTests: 0,
        passed: 0,
        failed: 0,
        passRate: 0,
        topicAccuracy: 0,
        actionAccuracy: 0,
        avgCompleteness: 0,
        avgCoherence: 0,
        avgConciseness: 0,
        avgLatency: 0
    },
    targets: {
        topicAccuracy: 90,
        actionAccuracy: 85,
        responseQuality: 80
    },
    jobs: [
        // Jobs will be populated from test results
        // Example structure:
        // {
        //     id: "job1",
        //     name: "User Story Name",
        //     priority: "P0",
        //     topic: "Topic_Name",
        //     totalTests: 4,
        //     passed: 3,
        //     failed: 1,
        //     passRate: 75
        // }
    ],
    testCases: [
        // Test cases will be populated from test results
        // Example structure:
        // {
        //     id: "tc1",
        //     jobId: "job1",
        //     jobName: "User Story Name",
        //     priority: "P0",
        //     utterance: "User utterance here",
        //     expectedTopic: "Expected_Topic",
        //     actualTopic: "Actual_Topic",
        //     topicPass: true,
        //     expectedActions: ["Action_Name"],
        //     actualActions: ["Action_Name"],
        //     actionPass: true,
        //     outputScore: 4,
        //     completenessScore: 5,
        //     coherenceScore: 5,
        //     concisenessScore: 5,
        //     latency: 42,
        //     explainability: "LLM reasoning for the score...",
        //     outcome: "Agent response text...",
        //     status: "PASS"
        // }
    ],
    recommendations: {
        immediate: [
            // {
            //     title: "Recommendation Title",
            //     description: "Description of the recommendation",
            //     impact: "High",
            //     effort: "Low"
            // }
        ],
        shortTerm: [
            // "Short-term improvement items"
        ],
        longTerm: [
            // "Long-term strategy items"
        ]
    }
};

export default class GreenlightDashboard extends LightningElement {
    @track activeTab = 'overview';
    @track expandedRows = {};
    @track activeFilter = 'all';
    @track activeJobFilter = 'all';
    @track searchTerm = '';
    @track copyFeedback = '';

    get data() {
        return TEST_RESULTS;
    }

    get jobOptions() {
        return TEST_RESULTS.jobs.map(job => ({
            id: job.id,
            name: `${job.priority} - ${job.name}`
        }));
    }

    get formattedTimestamp() {
        const date = new Date(TEST_RESULTS.timestamp);
        return date.toLocaleDateString('en-US', {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    get goLiveStatusClass() {
        const status = TEST_RESULTS.goLiveStatus;
        if (status === 'READY') return 'status-badge status-ready';
        if (status === 'CONDITIONAL') return 'status-badge status-conditional';
        return 'status-badge status-not-ready';
    }

    get goLiveStatusIcon() {
        const status = TEST_RESULTS.goLiveStatus;
        if (status === 'READY') return '✅';
        if (status === 'CONDITIONAL') return '⚠️';
        return '🚫';
    }

    get passRateStyle() {
        return `width: ${TEST_RESULTS.summary.passRate}%`;
    }

    get passRateStatus() {
        return TEST_RESULTS.summary.passRate >= 80 ? 'pass' : TEST_RESULTS.summary.passRate >= 60 ? 'warning' : 'fail';
    }

    get topicAccuracyStyle() {
        return `width: ${TEST_RESULTS.summary.topicAccuracy}%`;
    }

    get actionAccuracyStyle() {
        return `width: ${TEST_RESULTS.summary.actionAccuracy}%`;
    }

    get topicAccuracyStatus() {
        return TEST_RESULTS.summary.topicAccuracy >= TEST_RESULTS.targets.topicAccuracy ? 'pass' : 'fail';
    }

    get actionAccuracyStatus() {
        return TEST_RESULTS.summary.actionAccuracy >= TEST_RESULTS.targets.actionAccuracy ? 'pass' : 'fail';
    }

    get showOverview() {
        return this.activeTab === 'overview';
    }

    get showJobs() {
        return this.activeTab === 'jobs';
    }

    get showDetails() {
        return this.activeTab === 'details';
    }

    get showRecommendations() {
        return this.activeTab === 'recommendations';
    }

    get jobsForDisplay() {
        return TEST_RESULTS.jobs.map(job => {
            const passRateStatus = job.passRate === 100 ? 'pass' : job.passRate >= 60 ? 'warning' : 'fail';
            return {
                ...job,
                passRateStyle: `width: ${job.passRate}%`,
                passRateStatus,
                priorityClass: `priority-tag priority-${job.priority.toLowerCase()}`,
                rowClass: job.passRate < 60 ? 'job-row warning-row' : 'job-row'
            };
        });
    }

    get filteredTestCases() {
        let results = TEST_RESULTS.testCases;
        
        if (this.activeFilter === 'pass') {
            results = results.filter(tc => tc.status === 'PASS');
        } else if (this.activeFilter === 'fail') {
            results = results.filter(tc => tc.status === 'FAIL');
        }
        
        if (this.activeJobFilter !== 'all') {
            results = results.filter(tc => tc.jobId === this.activeJobFilter);
        }
        
        if (this.searchTerm) {
            const term = this.searchTerm.toLowerCase();
            results = results.filter(tc => 
                tc.utterance.toLowerCase().includes(term) ||
                tc.expectedTopic.toLowerCase().includes(term) ||
                tc.jobName.toLowerCase().includes(term)
            );
        }
        
        return results;
    }

    get filteredCount() {
        return this.filteredTestCases.length;
    }

    get testCasesForDisplay() {
        return this.filteredTestCases.map(tc => {
            const key = tc.id;
            const isExpanded = !!this.expandedRows[key];
            const statusClass = tc.status === 'PASS' ? 'status-pass' : 'status-fail';
            const topicClass = tc.topicPass ? 'check-pass' : 'check-fail';
            const actionClass = tc.actionPass ? 'check-pass' : 'check-fail';
            const outputClass = tc.outputScore >= 4 ? 'score-good' : tc.outputScore >= 3 ? 'score-ok' : 'score-low';

            return {
                ...tc,
                key,
                expandedKey: `${key}-expanded`,
                isExpanded,
                rowClass: `test-row ${tc.status === 'PASS' ? 'row-pass' : 'row-fail'}`,
                statusClass,
                statusIcon: tc.status === 'PASS' ? '✓' : '✗',
                topicClass,
                topicIcon: tc.topicPass ? '✓' : '✗',
                actionClass,
                actionIcon: tc.actionPass ? '✓' : '✗',
                outputClass,
                chevron: isExpanded ? '▼' : '▶',
                expectedActionsStr: tc.expectedActions.length > 0 ? tc.expectedActions.join(', ') : '(none)',
                actualActionsStr: tc.actualActions.length > 0 ? tc.actualActions.join(', ') : '(none)',
                outcomeHtml: tc.outcome,
                priorityClass: `priority-tag priority-${tc.priority.toLowerCase()}`
            };
        });
    }

    get filterAllClass() {
        return this.activeFilter === 'all' ? 'filter-btn active' : 'filter-btn';
    }

    get filterPassClass() {
        return this.activeFilter === 'pass' ? 'filter-btn pass active' : 'filter-btn pass';
    }

    get filterFailClass() {
        return this.activeFilter === 'fail' ? 'filter-btn fail active' : 'filter-btn fail';
    }

    handleTabClick(event) {
        this.activeTab = event.currentTarget.dataset.tab;
    }

    handleRowToggle(event) {
        const key = event.currentTarget.dataset.key;
        this.expandedRows = { ...this.expandedRows, [key]: !this.expandedRows[key] };
    }

    handleFilterClick(event) {
        this.activeFilter = event.currentTarget.dataset.filter;
    }

    handleJobFilterChange(event) {
        this.activeJobFilter = event.target.value;
    }

    handleSearchInput(event) {
        this.searchTerm = event.target.value;
    }

    handleClearSearch() {
        this.searchTerm = '';
    }

    handleExpandAll() {
        const newExpanded = {};
        this.filteredTestCases.forEach(tc => {
            newExpanded[tc.id] = true;
        });
        this.expandedRows = newExpanded;
    }

    handleCollapseAll() {
        this.expandedRows = {};
    }

    handleCopyUtterance(event) {
        event.stopPropagation();
        const utterance = event.currentTarget.dataset.utterance;
        
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(utterance).then(() => {
                this.showCopyToast('Copied to clipboard!');
            }).catch(() => {
                this.fallbackCopy(utterance);
            });
        } else {
            this.fallbackCopy(utterance);
        }
    }

    fallbackCopy(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            this.showCopyToast('Copied to clipboard!');
        } catch (err) {
            this.showCopyToast('Copy failed');
        }
        document.body.removeChild(textArea);
    }

    showCopyToast(message) {
        const toast = this.template.querySelector('.copy-toast');
        if (toast) {
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 2000);
        }
    }

    get overviewTabClass() {
        return this.activeTab === 'overview' ? 'tab active' : 'tab';
    }

    get jobsTabClass() {
        return this.activeTab === 'jobs' ? 'tab active' : 'tab';
    }

    get detailsTabClass() {
        return this.activeTab === 'details' ? 'tab active' : 'tab';
    }

    get recommendationsTabClass() {
        return this.activeTab === 'recommendations' ? 'tab active' : 'tab';
    }
}
