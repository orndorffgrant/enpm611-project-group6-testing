# 🧩 ENPM611 Project — GitHub Issues Analysis Platform

This repository provides an analytical application template for **ENPM611 (Software Engineering)** projects.  
The goal is to analyze GitHub issues from the [Poetry](https://github.com/python-poetry/poetry/issues) open-source repository and generate **data-driven insights** about project activity, response performance, sentiment trends, and labeling patterns — complete with **visualizations and exportable reports**.

---

## 🚀 Overview

The application provides both **interactive** and **automated** analysis modes.  
It includes four independent analyzers and one combined report generator:

| #   | Analyzer                           | Description                                                                   |
| --- | ---------------------------------- | ----------------------------------------------------------------------------- |
| 1️⃣  | **Contributor Activity Analyzer**  | Shows issue activity per contributor and visualizes issue-type distributions  |
| 2️⃣  | **Response & Resolution Analyzer** | Measures response and closure times across all issues                         |
| 3️⃣  | **Content/Text Analyzer**          | Analyzes text sentiment, keywords, and common error messages with word clouds |
| 4️⃣  | **Label Analyzer**                 | Examines issue labeling trends (e.g., `kind/*`, `area/*`) and produces charts |
| 5️⃣  | **Combined Report Generator**      | Merges all four analyses and exports a professional PDF report                |

Each analyzer can be run independently or combined into a single summarized report containing **all visual charts and summaries**.

---

## 🧱 Project Structure

```
enpm611-project-group6/
│
├── config.json                          # Configuration file (data paths, parameters)
├── run.py                               # Entry point for running analyses
│
├── data_loader.py                       # Loads JSON-formatted GitHub issues
├── model.py                             # Defines Issue, Event, and State data models
├── config.py                            # Handles environment-based configuration
│
├── contributor_activity_analyzer.py     # Analyzer #1
├── response_resolution_analyzer.py      # Analyzer #2
├── content_text_analyzer.py             # Analyzer #3
├── label_analyzer.py                    # Analyzer #4
│
├── pdf_report_exporter.py               # Handles PDF generation with Unicode-safe fonts
│
├── requirements.txt                     # Python dependencies
└── data/
    └── poetry_issues.json               # GitHub issues dataset
```

---

## ⚙️ Setup Instructions

### 1. Clone and Configure

Fork this repository, then clone it locally:

```bash
git clone https://github.com/DashRam64/enpm611-project-group6/tree/main
```

Download the `poetry_issues.json` file from the assignment and place it under the `data/` folder.

Update your `config.json` to point to the correct data file path.

💡 _You can also set `ENPM611_PROJECT_DATA_PATH` as an environment variable to avoid committing personal paths._

### 2. Create and Activate Virtual Environment

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

Install all project requirements:

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variable

**macOS/Linux:**

```bash
export ENPM611_PROJECT_DATA_PATH=/path/to/your/poetry_issues.json  # replace with your actual path
```

**Windows (PowerShell):**

```bash
$env:ENPM611_PROJECT_DATA_PATH="C:\path\to\your\poetry_issues.json" # replace with your actual path
```

**Windows (Command Prompt):**

```bash
set ENPM611_PROJECT_DATA_PATH="C:\path\to\your\poetry_issues.json" # replace with your actual path
```




---

## 🧭 Usage

### 🧠 Interactive Mode (Recommended)

Run the app interactively to choose analyses and filters:

```bash
python3 run.py
```

You'll be prompted with:

```
=== Interactive Analyzer Runner ===
1️⃣  Contributor Activity Analysis
2️⃣  Response & Resolution Analysis
3️⃣  Content/Text Analysis
4️⃣  Label Analysis
5️⃣  Combined Report (All Analyses)
```

Follow the prompts to optionally filter by:

- Start date / End date (e.g., `2022-01-01`)
- Label (e.g., `kind/bug`)
- Issue state (`open` or `closed`)

### ⚡ Command-Line Mode

You can also directly specify which analysis to run:

```bash
python3 run.py --feature 2 --state closed
```

| Flag                          | Description                                            |
| ----------------------------- | ------------------------------------------------------ |
| `--feature`                   | Required. Choose 1–5 to select which analysis to run   |
| `--label`                     | Optional. Filter issues by label                       |
| `--state`                     | Optional. Filter by issue state (e.g., open, closed)   |
| `--start_date` / `--end_date` | Optional. Restrict issues to a date range (YYYY-MM-DD) |

---

## 📊 Analysis Outputs

### 🧍 Contributor Activity

- Active issues per contributor
- Distribution of issue types (e.g., bug, enhancement)
- Horizontal bar charts for contribution activity

### 🕒 Response & Resolution

- Mean and median first-response times
- Resolution durations for closed issues
- Histograms and scatter plots showing response vs. resolution patterns

### 🧠 Content/Text

- Sentiment distribution (Positive, Neutral, Negative)
- Keyword frequency ranking
- Common error messages extracted from issue text
- Word cloud visualization

### 🏷️ Label Analysis

- Label frequency breakdown (`kind/*` and `area/*`)
- Simplified pie charts with low-frequency labels grouped under "Other"

### 📄 PDF Report Exporting

Each analyzer can produce a standalone report (optional), but the Combined Report (Option 5) automatically merges all results and visualizations into one comprehensive PDF:

```bash
python3 run.py --feature 5
```

This generates:

```
combined_analysis_report.pdf
```

Which includes:

- Charts from all analyzers
- Summary statistics and top insights
- Label distributions and contributor breakdowns

---

## 🧰 Requirements

`requirements.txt` includes:

```txt
matplotlib
numpy
textblob
wordcloud
fpdf
```

💡 Run `python -m textblob.download_corpora` once to install sentiment analysis resources.

---

## 🧩 VSCode Integration

This project includes a `.vscode` setup for debugging convenience:

- `launch.json`: predefined run configurations for each analyzer
- `settings.json`: user interface tweaks for easier debugging

To use:

1. Open the folder in VSCode
2. Press **Run** ▶️ on the left toolbar
3. Choose your desired analysis (1–5)

---

## 🧪 Example Usage

**Run Sentiment Analysis:**

```bash
python3 run.py --feature 3
```

**Generate Full Combined PDF:**

```bash
python3 run.py --feature 5
```

**Run Contributor Stats Only:**

```bash
python3 run.py --feature 1 --state open
```

---

## 📚 Project Highlights

✅ Modular analyzer design  
✅ Interactive filtering  
✅ Rich text sentiment analysis  
✅ Word cloud & visual charts  
✅ Automated report generation  
✅ Unicode-safe PDF exporting  
✅ Consistent DataLoader integration

---

## 🧠 Authors

**Team:** ENPM611 Project Group 6  
**Contributors:** Muhideen Mustapha, Gowri Mungath, Darshan Ram  
**Institution:** University of Maryland, College Park
