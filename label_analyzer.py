from collections import Counter
import matplotlib.pyplot as plt
from data_loader import DataLoader
from pdf_report_exporter import PDFReportExporter
import os

class LabelAnalyzer:
    def __init__(self):
        self.report_data = {}
        self.chart_paths = []

    def run(self):
        issues = DataLoader().get_issues()
        kind_counts = self.analyze_kind_labels(issues)
        area_counts = self.analyze_area_labels(issues)
        chart_path = self.plot_kind_label_pie_chart(kind_counts)
        if chart_path:
            self.chart_paths.append(chart_path)

        # Print summaries instead of exporting (export only in combined)
        print("\n🏷️ Label Analysis Summary")
        print("\nKind Labels:")
        for k, v in kind_counts.items():
            print(f"  {k}: {v}")
        print("\nArea Labels:")
        for k, v in area_counts.items():
            print(f"  {k}: {v}")

    def analyze_area_labels(self, issues):
        area_counts = Counter()
        for issue in issues:
            for label in issue.labels:
                if label.startswith("area/"):
                    area_counts[label] += 1
        self.report_data["Label: Area Counts"] = dict(area_counts)
        return area_counts

    def analyze_kind_labels(self, issues):
        kind_counts = Counter()
        for issue in issues:
            for label in issue.labels:
                if label.startswith("kind/"):
                    kind_counts[label] += 1
        self.report_data["Label: Kind Counts"] = dict(kind_counts)
        return kind_counts

    def plot_kind_label_pie_chart(self, kind_counts, save_path="label_kind_chart.png"):
        if not kind_counts:
            print("⚠️ No kind/* labels to plot.")
            return None

        labels, sizes = zip(*sorted(kind_counts.items(), key=lambda x: x[1], reverse=True))
        total = sum(sizes)
        labels_filtered, sizes_filtered, other_total = [], [], 0
        for label, count in zip(labels, sizes):
            if (count / total) < 0.03:
                other_total += count
            else:
                labels_filtered.append(label)
                sizes_filtered.append(count)
        if other_total:
            labels_filtered.append("Other")
            sizes_filtered.append(other_total)

        fig, ax = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax.pie(
            sizes_filtered, labels=labels_filtered, autopct="%1.1f%%",
            startangle=90, pctdistance=0.85
        )
        centre_circle = plt.Circle((0, 0), 0.70, fc="white")
        fig.gca().add_artist(centre_circle)
        ax.axis("equal")
        ax.set_title("Label Distribution: kind/* (Simplified)")

        fig.savefig(save_path, bbox_inches="tight")
        plt.show()
        plt.close(fig)
        print(f"🖼️ Label chart saved as {save_path}")
        return save_path

    def export_report_pdf(self, filename="label_analysis_report.pdf"):
        PDFReportExporter("Label Analysis Report").export(
            self.report_data,
            chart_paths=self.chart_paths,
            filename=filename
        )
