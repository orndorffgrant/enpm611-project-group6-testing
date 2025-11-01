"""
Starting point of the application.
"""
import argparse
from datetime import datetime

import config
from example_analysis import ExampleAnalysis
from content_text_analyzer import ContentTextAnalyzer
from label_analyzer import LabelAnalyzer
from contributor_activity_analyzer import ContributorActivityAnalyzer
from response_resolution_analyzer import ResponseResolutionAnalyzer


def parse_args():
    """Parses CLI args for non-interactive runs."""
    ap = argparse.ArgumentParser("run.py")

    ap.add_argument('--feature', '-f', type=int, required=True,
                    help='Which feature to run (1–5)')
    ap.add_argument('--start_date', type=str, required=False,
                    help='Start date (YYYY-MM-DD)')
    ap.add_argument('--end_date', type=str, required=False,
                    help='End date (YYYY-MM-DD)')
    ap.add_argument('--label', '-l', type=str, required=False,
                    help='Optional label filter')
    ap.add_argument('--state', type=str, required=False,
                    help='Filter by issue state (open or closed)')
    return ap.parse_args()


def interactive_mode():
    """Interactive selection of feature and optional filters."""
    print("\n=== Interactive Analyzer Runner ===")
    print("1️⃣  Contributor Activity Analysis")
    print("2️⃣  Response & Resolution Analysis")
    print("3️⃣  Content/Text Analysis")
    print("4️⃣  Label Analysis")
    print("5️⃣  Combined Report (All Analyses)")

    while True:
        try:
            feature = int(input("Enter choice (1–5): ").strip())
            if feature in [1, 2, 3, 4, 5]:
                break
        except ValueError:
            pass
        print("Invalid input. Please enter 1–5.")

    start_date = input("Start date (YYYY-MM-DD) or leave blank: ").strip()
    end_date = input("End date (YYYY-MM-DD) or leave blank: ").strip()
    label = input("Filter by label (e.g. kind/bug) or leave blank: ").strip()
    state = input("Filter by state (open/closed) or leave blank: ").strip()

    start_date = datetime.fromisoformat(start_date) if start_date else None
    end_date = datetime.fromisoformat(end_date) if end_date else None

    return {
        "feature": feature,
        "start_date": start_date,
        "end_date": end_date,
        "label": label or None,
        "state": state or None
    }


if __name__ == "__main__":
    # Interactive or non-interactive mode
    mode = input("Run in interactive mode? (y/n): ").strip().lower()

    if mode == "y":
        args_dict = interactive_mode()
        args = argparse.Namespace(**args_dict)
    else:
        args = parse_args()
        config.overwrite_from_args(args)

    feature = args.feature

    # --- Run the selected analyzer(s) ---
    if feature == 1:
        print("\n👥 Running Contributor Activity Analysis...")
        analyzer = ContributorActivityAnalyzer()
        analyzer.run()
        print("\n✅ Contributor Activity Analysis Complete.")

    elif feature == 2:
        print("\n🕒 Running Response & Resolution Analysis...")
        analyzer = ResponseResolutionAnalyzer()
        analyzer.run()
        print("\n✅ Response & Resolution Analysis Complete.")

    elif feature == 3:
        print("\n🧠 Running Content/Text Analysis...")
        analyzer = ContentTextAnalyzer()
        analyzer.run()
        print("\n✅ Content/Text Analysis Complete.")

    elif feature == 4:
        print("\n🏷️ Running Label Analysis...")
        analyzer = LabelAnalyzer()
        analyzer.run()
        print("\n✅ Label Analysis Complete.")

    elif feature == 5:
        print("\n📊 Running Combined Report (All Analyses)...")

        # Sequentially run all analyzers
        ca = ContributorActivityAnalyzer()
        rra = ResponseResolutionAnalyzer()
        cta = ContentTextAnalyzer()
        la = LabelAnalyzer()

        # Each analyzer loads data via DataLoader
        ca.run()
        rra.run()
        cta.run()
        la.run()

        # Merge results for the unified PDF
        combined_report = cta.report_data.copy()
        combined_report.update({
            "Contributor Activity": getattr(ca, "report_data", {}),
            "Response & Resolution": getattr(rra, "report_data", {}),
            "Label: Kind Counts": la.report_data.get("Label: Kind Counts", {}),
            "Label: Area Counts": la.report_data.get("Label: Area Counts", {})
        })

        # Combine chart images
        all_charts = []
        for a in [ca, rra, cta, la]:
            if hasattr(a, "chart_paths"):
                all_charts.extend(a.chart_paths)

        # Export unified PDF
        from pdf_report_exporter import PDFReportExporter
        PDFReportExporter("Combined Project Analysis Report").export(
            combined_report, chart_paths=all_charts, filename="combined_analysis_report.pdf"
        )
        print("\n✅ Combined Analysis Report Generated as combined_analysis_report.pdf")

    else:
        print("⚠️ Invalid feature selected (choose 1–5).")
