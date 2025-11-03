from typing import List
import numpy as np
import matplotlib.pyplot as plt
from data_loader import DataLoader
from model import Issue
import config
from pdf_report_exporter import PDFReportExporter


class ResponseResolutionAnalyzer:
    def __init__(self):
        self.USER = config.get_parameter('user')
        self.LABEL = config.get_parameter('label')
        self.report_data = {}
        self.chart_paths = []

    def run(self):
        issues: List[Issue] = DataLoader().get_issues()

        response_times = self.get_first_response_times(issues)
        resolution_times = self.get_resolution_times(issues)

        self.print_summary_statistics(response_times, resolution_times)
        self.plot_response_time_histogram(response_times)
        self.plot_response_vs_resolution_scatter(response_times, resolution_times)

    def get_first_response_times(self, issues):
        response_times = {}
        for issue in issues:
            if not hasattr(issue, "events") or not issue.events:
                continue
            created_time = getattr(issue, "created_date", None)
            if not created_time:
                continue
            comment_times = [
                e.event_date for e in issue.events
                if hasattr(e, "event_type") and e.event_type.lower() == "commented"
            ]
            if comment_times:
                first_response = min(comment_times)
                delta = first_response - created_time
                response_times[issue.number] = delta.total_seconds() / 3600
        return response_times

    def get_resolution_times(self, issues):
        resolution_times = {}
        for issue in issues:
            created_time = getattr(issue, "created_date", None)
            updated_time = getattr(issue, "updated_date", None)
            state = getattr(issue, "state", "").lower()
            if created_time and updated_time and state == "closed":
                delta = updated_time - created_time
                resolution_times[issue.number] = delta.total_seconds() / 3600
        return resolution_times

    def print_summary_statistics(self, response_times, resolution_times):
        def summary(title, data):
            stats_dict = {}
            print(f"\n--- {title} ---")
            if not data:
                print("No data available.")
                stats_dict["Info"] = "No data available."
                return stats_dict

            arr = np.array(list(data.values()))
            count = len(arr)
            mean = np.mean(arr)
            median = np.median(arr)
            min_val = np.min(arr)
            max_val = np.max(arr)

            print(f"Count: {count}")
            print(f"Mean: {mean:.2f} hrs")
            print(f"Median: {median:.2f} hrs")
            print(f"Min: {min_val:.2f} hrs")
            print(f"Max: {max_val:.2f} hrs")

            stats_dict["Count"] = int(count)
            stats_dict["Mean (hrs)"] = round(float(mean), 2)
            stats_dict["Median (hrs)"] = round(float(median), 2)
            stats_dict["Min (hrs)"] = round(float(min_val), 2)
            stats_dict["Max (hrs)"] = round(float(max_val), 2)

            return stats_dict

        self.report_data["Response Time Summary"] = summary("Response Time Summary", response_times)
        self.report_data["Resolution Time Summary"] = summary("Resolution Time Summary", resolution_times)


    def plot_response_time_histogram(self, response_times, bins=None):
        if not response_times:
            print("No response time data to plot.")
            return
        bins = bins or [1, 6, 24, 72, 168, 336, 720]
        plt.figure(figsize=(8, 5))
        plt.hist(list(response_times.values()), bins=bins, edgecolor='black')
        plt.title("Distribution of First Response Times (hours)")
        plt.xlabel("Response Time (hours)")
        plt.ylabel("Number of Issues")
        plt.grid(axis='y', alpha=0.6)
        plt.tight_layout()
        path = "chart_response_time_histogram.png"
        plt.savefig(path, bbox_inches="tight")
        plt.show()
        self.chart_paths.append(path)

    def plot_response_vs_resolution_scatter(self, response_times, resolution_times):
        common = set(response_times.keys()) & set(resolution_times.keys())
        if not common:
            print("No overlapping data for scatter plot.")
            return
        x = [response_times[i] for i in common]
        y = [resolution_times[i] for i in common]
        plt.figure(figsize=(7, 5))
        plt.scatter(x, y, alpha=0.7)
        plt.title("Response Time vs Resolution Time")
        plt.xlabel("First Response Time (hours)")
        plt.ylabel("Resolution Time (hours)")
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        path = "chart_response_vs_resolution.png"
        plt.savefig(path, bbox_inches="tight")
        plt.show()
        self.chart_paths.append(path)

    def export_report_pdf(self, filename="response_resolution_report.pdf"):
        PDFReportExporter("Response & Resolution Analysis Report").export(
            self.report_data,
            chart_paths=self.chart_paths,
            filename=filename
        )
