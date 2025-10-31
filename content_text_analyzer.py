# analysis/content_text_analyzer.py
import re
from collections import Counter
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from fpdf import FPDF
import os


class ContentTextAnalyzer:
    def __init__(self):
        self.report_data = {}
        self.chart_paths = []  # tracks all saved chart images

    # -----------------------------
    #  Keyword and Error Extraction
    # -----------------------------
    def get_top_keywords(self, issues, n=20):
        all_text = " ".join((issue.get("text") or "") for issue in issues)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        freq = Counter(words).most_common(n)
        self.report_data["Top Keywords"] = freq
        return freq

    def get_common_error_messages(self, issues):
        errors = Counter()
        for issue in issues:
            text = issue.get("text") or ""
            for line in text.splitlines():
                if "error" in line.lower() or "exception" in line.lower():
                    errors[line.strip()] += 1
        self.report_data["Common Errors"] = errors.most_common(10)
        return dict(errors)

    # -----------------------------
    #  Sentiment Summary
    # -----------------------------
    def compute_sentiment_summary(self, issues):
        """
        Compute and classify sentiment polarity into Positive, Neutral, or Negative.
        """
        categories = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for issue in issues:
            text = issue.get("text") or ""
            try:
                sentiment = TextBlob(text).sentiment.polarity
            except Exception:
                sentiment = 0.0

            if sentiment > 0.1:
                categories["Positive"] += 1
            elif sentiment < -0.1:
                categories["Negative"] += 1
            else:
                categories["Neutral"] += 1

        self.report_data["Sentiment Summary"] = categories
        print("\n🪄 Sentiment Summary:", categories)
        return categories

    # -----------------------------
    #  Visualization Helpers
    # -----------------------------
    def _save_plot_as_image(self, fig, filename):
        """Save a matplotlib figure temporarily for embedding in PDF."""
        fig.savefig(filename, bbox_inches="tight")
        plt.close(fig)
        return filename

    def plot_sentiment_categories(self):
        """Bar chart showing positive / neutral / negative sentiment."""
        summary = self.report_data.get("Sentiment Summary", {})
        if not summary:
            print("⚠️ No sentiment summary to plot.")
            return None

        labels = list(summary.keys())
        sizes = list(summary.values())
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(labels, sizes, color=["green", "gray", "red"])
        ax.set_title("Sentiment Classification")
        ax.set_xlabel("Category")
        ax.set_ylabel("Number of Issues")

        image_path = "sentiment_chart.png"
        self._save_plot_as_image(fig, image_path)
        self.chart_paths.append(image_path)
        print(f"🖼️ Sentiment chart saved as {image_path}")
        return image_path

    def plot_wordcloud(self, issues):
        """Generate and save a word cloud of issue descriptions."""
        all_text = " ".join((issue.get("text") or "") for issue in issues)
        if not all_text.strip():
            print("⚠️ No text found to generate word cloud.")
            return

        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_text)
        plt.figure(figsize=(8, 4))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title("Word Cloud of Issue Descriptions")

        image_path = "wordcloud.png"
        plt.savefig(image_path, bbox_inches="tight")
        plt.show()
        plt.close()
        self.chart_paths.append(image_path)
        print(f"🌥️ Word cloud saved as {image_path}")

    # -----------------------------
    #  PDF Report Generation
    # -----------------------------
    def export_report_pdf(self, filename="content_text_analysis_report.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_margins(left=15, top=15, right=15)

        pdf.cell(200, 10, txt="Content/Text & Label Analysis Report", ln=True, align='C')
        pdf.ln(10)

        # 1️⃣ Sentiment Summary
        summary = self.report_data.get("Sentiment Summary")
        if summary:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, txt="Sentiment Summary", ln=True)
            pdf.set_font("Arial", size=10)
            for k, v in summary.items():
                pdf.cell(0, 8, txt=f"{k}: {v}", ln=True)
            pdf.ln(10)

        # --- Image Embeds (sentiment chart, word cloud, label pie) ---
        def add_image_if_present(path_substring, title):
            for p in self.chart_paths:
                if p and path_substring in p and os.path.exists(p):
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, txt=title, ln=True)
                    pdf.image(p, x=10, y=None, w=180)
                    pdf.ln(10)

        add_image_if_present("sentiment_chart", "Sentiment Classification Chart")
        add_image_if_present("wordcloud", "Word Cloud")
        add_image_if_present("label_kind_chart", "Label Distribution: kind/*")

        # 4️⃣ Top Keywords
        keywords = self.report_data.get("Top Keywords", [])
        if keywords:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, txt="Top Keywords", ln=True)
            pdf.set_font("Arial", size=10)
            for word, count in keywords:
                pdf.cell(0, 8, txt=f"{word}: {count}", ln=True)
            pdf.ln(10)

        # 5️⃣ Common Errors
        errors = self.report_data.get("Common Errors", [])
        if errors:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, txt="Common Errors", ln=True)
            pdf.set_font("Arial", size=10)

            def safe_write_error(msg, count):
                """Safely write long or unprintable error lines to PDF."""
                try:
                    text = f"{msg} (Count: {count})"
                    text = "".join(ch if 32 <= ord(ch) <= 126 else "?" for ch in text)
                    text = re.sub(r"\s+", " ", text).strip()
                    if len(text) > 400:
                        text = text[:400] + "… [truncated]"
                    if len(text) > 80:
                        text = " ".join(text[i:i+80] for i in range(0, len(text), 80))
                    pdf.multi_cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
                except Exception:
                    try:
                        pdf.multi_cell(0, 8, "[Unprintable Error Line]")
                    except Exception:
                        pass

            for msg, count in errors:
                safe_write_error(msg, count)
            pdf.ln(10)

        # 6️⃣ Label Counts (tables)
        for label_section in ["Label: Kind Counts", "Label: Area Counts"]:
            data = self.report_data.get(label_section)
            if data:
                pdf.add_page()
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, txt=label_section, ln=True)
                pdf.set_font("Arial", size=10)
                for k, v in data.items():
                    pdf.cell(0, 8, txt=f"{k}: {v}", ln=True)
                pdf.ln(8)

        # --- Output and cleanup ---
        pdf.output(filename)
        print(f"✅ PDF report saved to {filename}")

        for path in self.chart_paths:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
