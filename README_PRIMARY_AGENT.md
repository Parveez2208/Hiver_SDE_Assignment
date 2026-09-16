# 1. Primary Agent README (README_PRIMARY_AGENT.md)

## 1.1 Overview
This module implements the primary LLM-powered support agent designed to classify inbound user tweets, generate ground-truth replies, and apply structured escalation logic. It also includes the primary evaluation harness to compare generated outputs against a curated 200-item golden dataset.

## 1.2 System Architecture & Data Flow
**Flow:** Inbound Tweet JSON -> Primary Support Agent (LLM) -> Regex Output Parser -> Intent & Response Data / Escalation Flag -> Primary Evaluation Harness -> Evaluation Metric Results (JSON).

## 1.3 Core Components
**1.3.1 Intent Taxonomy & Response Logic**
* **Account Issue / Technical Support:** Provides immediate resolution steps.
* **Billing / Refund:** Identifies transaction scope and routes to policy workflows[cite: 1].
* **Escalation Trigger:** Triggers structured escalation when queries fall outside predefined resolution bounds[cite: 1].

**1.3.2 Output Formatting & Parsing**
* **Output Standard:** Strict adherence to formatted strings or JSON structures[cite: 1].
* **Regex Verification Pattern:** `r"^(Auto-handled|Escalate: .*)$"`[cite: 1].
* **Parsing Handling:** Extracts evaluation parameters, intent categories, and reply keywords using native `json` and `re` modules[cite: 1].

## 1.4 Setup & Execution
**1.4.1 Prerequisites**
* Python 3.9+[cite: 1]
* Required packages: `requests`, `fastapi`, `uvicorn`[cite: 1]

**1.4.2 Installation & Reproducibility (Under 15 Mins)**
```bash
git clone [https://github.com/bismil-07/hiver-sde-assignment](https://github.com/bismil-07/hiver-sde-assignment)
cd hiver-sde-assignment
pip install -r requirements.txt
