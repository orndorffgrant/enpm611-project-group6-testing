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

        # Sort and group small slices into "Other"
        labels, sizes = zip(*sorted(kind_counts.items(), key=lambda x: x[1], reverse=True))
        total = sum(sizes)
        labels_filtered, sizes_filtered = [], []
        other_total = 0

        for label, count in zip(labels, sizes):
            if (count / total) < 0.03:  # labels under 3% get grouped
                other_total += count
            else:
                labels_filtered.append(label)
                sizes_filtered.append(count)

        if other_total > 0:
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

        # Improve look
        centre_circle = plt.Circle((0, 0), 0.70, fc="white")
        fig.gca().add_artist(centre_circle)
        ax.axis("equal")
        ax.set_title("Label Distribution: kind/* (Simplified)")

        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
        print(f"🖼️ Cleaned label kind chart saved as {save_path}")
        return save_path