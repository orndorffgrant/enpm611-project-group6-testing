# analysis/label_analyzer.py
from collections import Counter, defaultdict
import matplotlib.pyplot as plt

class LabelAnalyzer:
    def __init__(self):
        self.report_data = {}

    def analyze_area_labels(self, issues):
        area_counts = Counter()
        for issue in issues:
            for label in issue.get("labels", []):
                if label.startswith("area/"):
                    area_counts[label] += 1
        self.report_data["Label: Area Counts"] = dict(area_counts)
        return area_counts

    def analyze_kind_labels(self, issues):
        kind_counts = Counter()
        for issue in issues:
            for label in issue.get("labels", []):
                if label.startswith("kind/"):
                    kind_counts[label] += 1
        self.report_data["Label: Kind Counts"] = dict(kind_counts)
        return kind_counts

    def plot_kind_label_pie_chart(self, kind_counts, save_path="label_kind_chart.png"):
        if not kind_counts:
            print("⚠️ No kind/* labels to plot.")
            return None
        labels = list(kind_counts.keys())
        sizes  = list(kind_counts.values())
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.set_title("Label Distribution: kind/*")
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
        print(f"🖼️ Label kind chart saved as {save_path}")
        return save_path