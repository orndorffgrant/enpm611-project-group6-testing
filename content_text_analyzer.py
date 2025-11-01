import re
from collections import Counter
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from data_loader import DataLoader
from pdf_report_exporter import PDFReportExporter
import os

class ContentTextAnalyzer:
    def __init__(self):
        self.report_data = {}
        self.chart_paths = []

    def run(self):
        issues = DataLoader().get_issues()
        self.compute_sentiment_summary(issues)
        self.plot_sentiment_categories()
        self.plot_wordcloud(issues)
        self.get_top_keywords(issues)
        self.get_common_error_messages(issues)

    def get_top_keywords(self, issues, n=20):
        all_text = " ".join(i.text or "" for i in issues)
        words = re.findall(r"\b[a-zA-Z]{3,}\b", all_text.lower())
        freq = Counter(words).most_common(n)
        self.report_data["Top Keywords"] = freq
        print("\n🔠 Top Keywords:")
        for w, c in freq:
            print(f"  {w}: {c}")
        return freq

    def get_common_error_messages(self, issues):
        errors = Counter()
        for issue in issues:
            for line in (issue.text or "").splitlines():
                if "error" in line.lower() or "exception" in line.lower():
                    errors[line.strip()] += 1
        common_errors = errors.most_common(10)
        self.report_data["Common Errors"] = common_errors
        print("\n❗ Common Error Messages:")
        for msg, count in common_errors:
            print(f"  {msg[:100]} (x{count})")
        return common_errors

    def compute_sentiment_summary(self, issues):
        cats = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for issue in issues:
            text = issue.text or ""
            try:
                s = TextBlob(text).sentiment.polarity
            except Exception:
                s = 0
            if s > 0.1:
                cats["Positive"] += 1
            elif s < -0.1:
                cats["Negative"] += 1
            else:
                cats["Neutral"] += 1
        self.report_data["Sentiment Summary"] = cats
        print("\n🪄 Sentiment Summary:")
        for k, v in cats.items():
            print(f"  {k}: {v}")
        return cats

    def plot_sentiment_categories(self):
        summary = self.report_data.get("Sentiment Summary", {})
        if not summary:
            print("⚠️ No sentiment summary to plot.")
            return
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(summary.keys(), summary.values(), color=["green", "gray", "red"])
        ax.set_title("Sentiment Classification")
        ax.set_xlabel("Category")
        ax.set_ylabel("Number of Issues")
        path = "sentiment_chart.png"
        fig.savefig(path, bbox_inches="tight")
        plt.show()
        plt.close(fig)
        self.chart_paths.append(path)
        print(f"🖼️ Sentiment chart saved as {path}")

    def plot_wordcloud(self, issues):
        all_text = " ".join(i.text or "" for i in issues)
        if not all_text.strip():
            print("⚠️ No text found to generate word cloud.")
            return
        stopwords = STOPWORDS.union({
            "python", "python3", "package", "pip", "install", "error",
            "project", "file", "function", "version"
        })
        wc = WordCloud(width=800, height=400, background_color="white", stopwords=stopwords)
        wc.generate(all_text)
        plt.figure(figsize=(8, 4))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        path = "wordcloud.png"
        plt.savefig(path, bbox_inches="tight")
        plt.show()
        plt.close()
        self.chart_paths.append(path)
        print(f"🌥️ Word cloud saved as {path}")

    def export_report_pdf(self, filename="content_text_analysis_report.pdf"):
        PDFReportExporter("Content/Text Analysis Report").export(
            self.report_data,
            chart_paths=self.chart_paths,
            filename=filename
        )
