import json
import csv
from datetime import datetime
from typing import List, Dict
import os

class Reporter:
    """
    Handles report generation for the scanned results.
    Supported formats: JSON, TXT, HTML.
    """
    def __init__(self, target: str, format_type: str, results: List[Dict]):
        self.target = target
        self.format_type = format_type
        self.results = results
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = f"report_{self.target.replace('/', '_')}_{self.timestamp}.{self.format_type}"
        os.makedirs("reports", exist_ok=True)
        self.filepath = os.path.join("reports", self.filename)

    def generate(self) -> str:
        """Generates the report file and returns its path."""
        if self.format_type == 'json':
            self._generate_json()
        elif self.format_type == 'txt':
            self._generate_txt()
        elif self.format_type == 'html':
            self._generate_html()
        else:
            raise ValueError(f"Unsupported format: {self.format_type}")
        return self.filepath

    def _generate_json(self):
        data = {
            "target": self.target,
            "timestamp": self.timestamp,
            "results": self.results
        }
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def _generate_txt(self):
        with open(self.filepath, 'w') as f:
            f.write(f"PyScan Pro Report\n")
            f.write(f"{'-'*50}\n")
            f.write(f"Target: {self.target}\n")
            f.write(f"Scan Time: {self.timestamp}\n")
            f.write(f"{'-'*50}\n\n")
            
            f.write(f"{'IP':<15} | {'PORT':<8} | {'STATUS':<10} | {'SERVICE':<15} | {'BANNER'}\n")
            f.write(f"{'-'*75}\n")
            
            for r in self.results:
                f.write(f"{r['ip']:<15} | {r['port']:<8} | {r['status']:<10} | {r['service']:<15} | {r['banner']}\n")

    def _generate_html(self):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PyScan Pro Report - {self.target}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a1a2e; color: #e0e0e0; margin: 40px; }}
                h1 {{ color: #4ecca3; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, ... td {{ border: 1px solid #333; padding: 12px; text-align: left; }}
                th {{ background-color: #232931; color: #4ecca3; }}
                tr:nth-child(even) {{ background-color: #2a313c; }}
                .status-open {{ color: #4ecca3; font-weight: bold; }}
                .status-filtered {{ color: #f39c12; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>PyScan Pro - Scan Report</h1>
            <p><strong>Target:</strong> {self.target}</p>
            <p><strong>Timestamp:</strong> {self.timestamp}</p>
            
            <table>
                <tr>
                    <th>IP Address</th>
                    <th>Port</th>
                    <th>Status</th>
                    <th>Service</th>
                    <th>Banner</th>
                </tr>
        """
        for r in self.results:
            status_class = 'status-open' if r['status'] == 'OPEN' else 'status-filtered'
            html_content += f"""
                <tr>
                    <td>{r['ip']}</td>
                    <td>{r['port']}</td>
                    <td class="{status_class}">{r['status']}</td>
                    <td>{r['service']}</td>
                    <td>{r['banner']}</td>
                </tr>
            """
        html_content += """
            </table>
        </body>
        </html>
        """
        
        with open(self.filepath, 'w') as f:
            f.write(html_content)
