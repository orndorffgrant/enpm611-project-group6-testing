"""
Starting point of the application. This module is invoked from
the command line to run the analyses.
"""

import argparse
import json
from datetime import datetime

import config
from example_analysis import ExampleAnalysis
from content_text_analyzer import ContentTextAnalyzer
from label_analyzer import LabelAnalyzer


def parse_args():
    """Parses CLI args for non-interactive runs."""
    ap = argparse.ArgumentParser("run.py")

    ap.add_argument('--feature', '-f', type=int, required=True,
                    help='Which of the three features to run')
    ap.add_argument('--label', '-l', type=str, required=False,
                    help='Optional label filter')
    ap.add_argument('--start_date', type=str, required=False,
                    help='Start date for filtering issues (YYYY-MM-DD)')
    ap.add_argument('--end_date', type=str, required=False,
                    help='End date for filtering issues (YYYY-MM-DD)')
    ap.add_argument('--state', type=str, required=False,
                    help='Filter by issue state (open or closed)')
    return ap.parse_args()


def interactive_mode():
    """Interactive input to choose feature and filters."""
    print("\n=== 🧠 Interactive Analyzer Runner ===")
    print("1️⃣  Content/Text Analysis")
    print("2️⃣  Label Analysis")
    print("3️⃣  Combined Report")

    while True:
        try:
            feature = int(input("Enter choice (1-3): ").strip())
            if feature in [1, 2, 3]:
                break
        except ValueError:
            pass
        print("Invalid input. Please enter 1, 2, or 3.")

    start_date = input("Start date (YYYY-MM-DD) or leave blank: ").strip()
    end_date = input("End date (YYYY-MM-DD) or leave blank: ").strip()
    label = input("Filter by label (e.g. kind/bug) or leave blank: ").strip()
    state = input("Filter by state (open/closed) or leave blank: ").strip()

    start_date = datetime.fromisoformat(start_date) if start_date else None
    end_date = datetime.fromisoformat(end_date) if end_date else None
    label = label if label else None
    state = state if state else None

    return {
        "feature": feature,
        "start_date": start_date,
        "end_date": end_date,
        "label": label,
        "state": state
    }


def filter_issues(issues, start_date=None, end_date=None, label=None, state=None):
    """Filters loaded issues by date, label, or state."""
    filtered = []
    for issue in issues:
        created = None
        if issue.get("created_date"):
            try:
                created = datetime.fromisoformat(issue["created_date"])
            except ValueError:
                pass

        if start_date and created and created < start_date:
            continue
        if end_date and created and created > end_date:
            continue
        if label and label not in issue.get("labels", []):
            continue
        if state and issue.get("state") != state:
            continue
        filtered.append(issue)

    print(f"\n✅ Filtered down to {len(filtered)} issues.")
    return filtered


if __name__ == "__main__":
    # Ask if user wants interactive mode
    mode = input("Run in interactive mode? (y/n): ").strip().lower()

    if mode == "y":
        args_dict = interactive_mode()
        args = argparse.Namespace(**args_dict)
    else:
        args = parse_args()
        config.overwrite_from_args(args)

    # Load dataset
    with open("data/poetry_issues.json", "r") as f:
        issues = json.load(f)

    # Filter
    filtered_issues = filter_issues(
        issues,
        start_date=args.start_date,
        end_date=args.end_date,
        label=args.label,
        state=args.state
    )

    # --- Run selected feature ---
    if args.feature == 1:
        print("\n🧠 Running Content/Text Analysis...")
        analyzer = ContentTextAnalyzer()
        analyzer.compute_sentiment_summary(filtered_issues)
        analyzer.plot_sentiment_categories()
        analyzer.plot_wordcloud(filtered_issues)
        analyzer.get_top_keywords(filtered_issues)
        analyzer.get_common_error_messages(filtered_issues)
        analyzer.export_report_pdf("content_text_analysis_report.pdf")

    elif args.feature == 2:
        print("\n🏷️ Running Label Analysis...")
        analyzer = LabelAnalyzer()
        kind_labels = analyzer.analyze_kind_labels(filtered_issues)
        area_labels = analyzer.analyze_area_labels(filtered_issues)
        analyzer.plot_kind_label_pie_chart(kind_labels)
        print("\n✅ Label analysis complete.")

    elif args.feature == 3:
        print("\n📊 Running Combined Report...")
        cta = ContentTextAnalyzer()
        la  = LabelAnalyzer()

        # --- Content/Text Analysis ---
        cta.compute_sentiment_summary(filtered_issues)
        cta.plot_sentiment_categories()
        cta.plot_wordcloud(filtered_issues)
        cta.get_top_keywords(filtered_issues)
        cta.get_common_error_messages(filtered_issues)

        # --- Label Analysis & chart ---
        try:
            kind_counts = la.analyze_kind_labels(filtered_issues)
            area_counts = la.analyze_area_labels(filtered_issues)
            kind_chart  = la.plot_kind_label_pie_chart(kind_counts, save_path="label_kind_chart.png")
        except Exception as e:
            print(f"⚠️ Label analysis skipped due to error: {e}")
            kind_counts, area_counts, kind_chart = {}, {}, None

        # Merge label tables into the same report_data
        if kind_counts:
            cta.report_data["Label: Kind Counts"] = dict(kind_counts)
        if area_counts:
            cta.report_data["Label: Area Counts"] = dict(area_counts)
        # Attach label chart image so it will be embedded
        if kind_chart:
            cta.chart_paths.append(kind_chart)

        # --- Export unified PDF ---
        cta.export_report_pdf("combined_analysis_report.pdf")
        print("\n✅ Combined analysis report generated as combined_analysis_report.pdf")

    else:
        print("⚠️ Please specify a valid feature (1-3).")
