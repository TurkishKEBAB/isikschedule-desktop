"""
HTML Report Generator for Test Results
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import base64


class HTMLReportGenerator:
    """Generate visual HTML reports with screenshots"""

    def __init__(self, test_logger):
        self.logger = test_logger

    def generate(self, output_path: Path) -> Path:
        """Generate comprehensive HTML report"""
        html = self._generate_html()

        report_file = output_path / "test_report.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)

        return report_file

    def _generate_html(self) -> str:
        """Build HTML content"""
        summary = self.logger.get_summary()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SchedularV3 Test Report - {self.logger.test_name}</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧪 SchedularV3 Automated Test Report</h1>
            <div class="test-info">
                <div><strong>Test Name:</strong> {self.logger.test_name}</div>
                <div><strong>Started:</strong> {self.logger.start_time.strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div><strong>Duration:</strong> {summary['duration']}</div>
            </div>
        </header>
        
        <section class="summary">
            <h2>📊 Summary</h2>
            <div class="stats-grid">
                <div class="stat-box success">
                    <div class="stat-value">{summary['success']}</div>
                    <div class="stat-label">Success</div>
                </div>
                <div class="stat-box failed">
                    <div class="stat-value">{summary['failed']}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-box warning">
                    <div class="stat-value">{summary['warnings']}</div>
                    <div class="stat-label">Warnings</div>
                </div>
                <div class="stat-box total">
                    <div class="stat-value">{summary['total_actions']}</div>
                    <div class="stat-label">Total Actions</div>
                </div>
            </div>
            <div class="success-rate">
                <strong>Success Rate:</strong> {summary['success_rate']}
            </div>
        </section>
        
        {self._generate_issues_section()}
        
        {self._generate_timeline_section()}
        
        {self._generate_snapshots_section()}
        
        <footer>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Log file: <code>{self.logger.log_file}</code></p>
        </footer>
    </div>
</body>
</html>
"""
        return html

    def _get_css(self) -> str:
        """CSS styles for report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        
        .test-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .test-info div {
            background: rgba(255,255,255,0.1);
            padding: 10px 15px;
            border-radius: 6px;
        }
        
        section {
            padding: 40px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        section:last-of-type {
            border-bottom: none;
        }
        
        h2 {
            font-size: 2em;
            margin-bottom: 25px;
            color: #667eea;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-box {
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .stat-box.success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        
        .stat-box.failed {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        
        .stat-box.warning {
            background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
            color: white;
        }
        
        .stat-box.total {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .stat-value {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stat-label {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .success-rate {
            font-size: 1.5em;
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .issues-list {
            list-style: none;
        }
        
        .issue-item {
            background: #fff3cd;
            border-left: 4px solid #ff6b6b;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        
        .issue-item.critical {
            background: #f8d7da;
            border-color: #dc3545;
        }
        
        .timeline {
            position: relative;
        }
        
        .timeline-item {
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            background: #f8f9fa;
            position: relative;
            padding-left: 60px;
        }
        
        .timeline-item.success {
            border-left: 4px solid #38ef7d;
        }
        
        .timeline-item.failed {
            border-left: 4px solid #eb3349;
        }
        
        .timeline-item.warning {
            border-left: 4px solid #f2c94c;
        }
        
        .timeline-icon {
            position: absolute;
            left: 20px;
            top: 20px;
            font-size: 1.5em;
        }
        
        .timeline-content h3 {
            margin-bottom: 10px;
            color: #333;
        }
        
        .timeline-meta {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }
        
        .screenshot-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .screenshot {
            border: 2px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .screenshot img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .screenshot-label {
            padding: 10px;
            background: #f8f9fa;
            text-align: center;
            font-size: 0.9em;
            color: #666;
        }
        
        .snapshot-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .snapshot-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .snapshot-field {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 3px solid #667eea;
        }
        
        .field-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        
        .field-value {
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }
        
        .inconsistency-alert {
            background: #f8d7da;
            border: 2px solid #dc3545;
            border-radius: 6px;
            padding: 15px;
            margin-top: 15px;
        }
        
        .inconsistency-alert h4 {
            color: #dc3545;
            margin-bottom: 10px;
        }
        
        footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
        }
        
        code {
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        
        .no-data {
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }
        """

    def _generate_issues_section(self) -> str:
        """Generate issues section"""
        if not self.logger.issues:
            return """
        <section class="issues">
            <h2>🎉 Issues</h2>
            <div class="no-data">No issues detected! All tests passed successfully.</div>
        </section>
            """

        issues_html = []
        for issue in self.logger.issues:
            css_class = "critical" if "CRITICAL" in issue else "warning"
            issues_html.append(f'<li class="issue-item {css_class}">{issue}</li>')

        return f"""
        <section class="issues">
            <h2>⚠️ Issues ({len(self.logger.issues)})</h2>
            <ul class="issues-list">
                {''.join(issues_html)}
            </ul>
        </section>
        """

    def _generate_timeline_section(self) -> str:
        """Generate action timeline"""
        if not self.logger.actions:
            return """
        <section class="timeline-section">
            <h2>⏱️ Timeline</h2>
            <div class="no-data">No actions recorded.</div>
        </section>
            """

        timeline_html = []
        for action in self.logger.actions:
            icon = {"SUCCESS": "✅", "FAILED": "❌", "WARNING": "⚠️"}.get(action.status, "❓")

            screenshots = ""
            if action.screenshot_before or action.screenshot_after:
                screenshots = '<div class="screenshot-grid">'
                if action.screenshot_before:
                    screenshots += f'''
                    <div class="screenshot">
                        <img src="{action.screenshot_before}" alt="Before">
                        <div class="screenshot-label">Before</div>
                    </div>
                    '''
                if action.screenshot_after:
                    screenshots += f'''
                    <div class="screenshot">
                        <img src="{action.screenshot_after}" alt="After">
                        <div class="screenshot-label">After</div>
                    </div>
                    '''
                screenshots += '</div>'

            timeline_html.append(f'''
            <div class="timeline-item {action.status.lower()}">
                <div class="timeline-icon">{icon}</div>
                <div class="timeline-content">
                    <h3>{action.action_type.upper()}: {action.element}</h3>
                    <div class="timeline-meta">
                        <strong>Time:</strong> {action.timestamp} | 
                        <strong>Duration:</strong> {action.duration_ms:.2f}ms | 
                        <strong>Phase:</strong> {action.phase.upper()}
                    </div>
                    <p><strong>Expected:</strong> {action.expected}</p>
                    <p><strong>Actual:</strong> {action.actual}</p>
                    <p><strong>Details:</strong> {action.details}</p>
                    {screenshots}
                </div>
            </div>
            ''')

        return f"""
        <section class="timeline-section">
            <h2>⏱️ Action Timeline ({len(self.logger.actions)} actions)</h2>
            <div class="timeline">
                {''.join(timeline_html)}
            </div>
        </section>
        """

    def _generate_snapshots_section(self) -> str:
        """Generate state snapshots section"""
        if not self.logger.snapshots:
            return """
        <section class="snapshots">
            <h2>📸 State Snapshots</h2>
            <div class="no-data">No state snapshots captured.</div>
        </section>
            """

        snapshots_html = []
        for i, snapshot in enumerate(self.logger.snapshots, 1):
            inconsistencies = ""
            if snapshot.inconsistencies:
                issues_list = "".join(f"<li>{issue}</li>" for issue in snapshot.inconsistencies)
                inconsistencies = f'''
                <div class="inconsistency-alert">
                    <h4>⚠️ Inconsistencies Detected</h4>
                    <ul>{issues_list}</ul>
                </div>
                '''

            snapshots_html.append(f'''
            <div class="snapshot-card">
                <h3>Snapshot #{i} - {snapshot.timestamp}</h3>
                <div class="snapshot-grid">
                    <div class="snapshot-field">
                        <div class="field-label">GPA</div>
                        <div class="field-value">{snapshot.gpa:.2f}</div>
                    </div>
                    <div class="snapshot-field">
                        <div class="field-label">Selected ECTS</div>
                        <div class="field-value">{snapshot.selected_credits}</div>
                    </div>
                    <div class="snapshot-field">
                        <div class="field-label">Max ECTS (Internal)</div>
                        <div class="field-value">{snapshot.max_credits_internal}</div>
                    </div>
                    <div class="snapshot-field">
                        <div class="field-label">Max ECTS (UI)</div>
                        <div class="field-value">{snapshot.max_credits_ui}</div>
                    </div>
                    <div class="snapshot-field">
                        <div class="field-label">Courses</div>
                        <div class="field-value">{len(snapshot.selected_courses)}</div>
                    </div>
                    <div class="snapshot-field">
                        <div class="field-label">Conflicts</div>
                        <div class="field-value">{snapshot.conflicts}</div>
                    </div>
                    <div class="snapshot-field">
                        <div class="field-label">Free Days</div>
                        <div class="field-value">{snapshot.free_days}</div>
                    </div>
                </div>
                {inconsistencies}
            </div>
            ''')

        return f"""
        <section class="snapshots">
            <h2>📸 State Snapshots ({len(self.logger.snapshots)})</h2>
            {''.join(snapshots_html)}
        </section>
        """

