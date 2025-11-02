from collections import Counter, defaultdict
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

        # --- Individual label analyses ---
        kind_counts = self.analyze_kind_labels(issues)
        area_counts = self.analyze_area_labels(issues)
        prefix_counts = self.analyze_label_prefixes(issues)

        # --- Charts ---
        kind_chart = self.plot_kind_label_pie_chart(kind_counts)
        prefix_chart = self.plot_label_prefix_distribution(prefix_counts)
        if kind_chart:
            self.chart_paths.append(kind_chart)
        if prefix_chart:
            self.chart_paths.append(prefix_chart)

        # --- Print summaries (console) ---
        print("\n🏷️ Label Analysis Summary")

        print("\nKind Labels:")
        for k, v in kind_counts.items():
            print(f"  {k}: {v}")

        print("\nArea Labels:")
        for k, v in area_counts.items():
            print(f"  {k}: {v}")

        print("\n📊 Label Prefix Breakdown:")
        for prefix, count in prefix_counts.items():
            print(f"  {prefix}: {count}")

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

    def analyze_label_prefixes(self, issues):
        prefix_counts = Counter()
        for issue in issues:
            for label in issue.labels:
                if "/" in label:
                    prefix = label.split("/")[0]
                    prefix_counts[prefix] += 1
        self.report_data["Label: Prefix Breakdown"] = dict(prefix_counts)
        return prefix_counts

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
            sizes_filtered,
            labels=labels_filtered,
            autopct="%1.1f%%",
            startangle=90,
            pctdistance=0.85
        )
        centre_circle = plt.Circle((0, 0), 0.70, fc="white")
        fig.gca().add_artist(centre_circle)
        ax.axis("equal")
        ax.set_title("Label Distribution: kind/* (Simplified)")

        fig.savefig(save_path, bbox_inches="tight")
        plt.show()
        plt.close(fig)
        print(f"🖼️ Kind label chart saved as {save_path}")
        return save_path

    def plot_label_prefix_distribution(self, prefix_counts, save_path="label_prefix_distribution.png"):
        """
        Bar chart showing how many labels fall under each prefix type.
        """
        if not prefix_counts:
            print("⚠️ No label prefixes to plot.")
            return None

        labels = list(prefix_counts.keys())
        values = list(prefix_counts.values())

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(labels, values, color="teal", alpha=0.85)

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + (max(values) * 0.01), 
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold"
            )

        ax.set_title("Label Category Distribution by Prefix", fontsize=12, weight="bold")
        ax.set_xlabel("Label Prefix (category)")
        ax.set_ylabel("Count of Labels")
        ax.grid(axis="y", linestyle="--", alpha=0.6)

        fig.tight_layout()
        fig.savefig(save_path, bbox_inches="tight")
        plt.show()
        plt.close(fig)
        print(f"🖼️ Label prefix distribution chart saved as {save_path}")
        return save_path

    def export_report_pdf(self, filename="label_analysis_report.pdf"):
        print("\n📋 PDF Report Data Contents:")
        for key, value in self.report_data.items():
            print(f"  {key}: {value}")
            
        PDFReportExporter("Label Analysis Report").export(
            self.report_data,
            chart_paths=self.chart_paths,
            filename=filename
        )