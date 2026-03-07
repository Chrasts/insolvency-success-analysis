# Debt Relief (Insolvency) Event-Log Analysis

This repository contains a small end-to-end data analysis project based on two relational tables describing insolvency (debt relief) proceedings. The goal is to infer whether a proceeding was **successfully completed** from an event log, link the outcome to debtor characteristics, and summarize results in a short PDF report.

> Note: The CSV input files included in this repository are **fictional sample files** created for demonstration purposes. They are structurally similar to the original inputs used for the assignment, but they do **not** contain real case data. Therefore, any results reproduced from the public repository are only illustrative and do not correspond to real-world insolvency outcomes.

---

## Project overview

### Data model
The analysis uses two tables:

- **`data/cases.csv`** — one row per person participating in a specific insolvency case:
  - case identifier (e.g., docket / case id),
  - court name,
  - debtor order within the case (some cases have multiple debtors),
  - a partially anonymized personal identifier derived from the Czech birth-number format, from which sex can be inferred using the dataset’s encoding rule.

- **`data/events.csv`** — one row per event:
  - event date,
  - event type/code,
  - case identifier (link to `data/cases.csv`).

These public-facing files correspond to the original assignment tables commonly referred to as **`udaje`** and **`udalosti`**.

### Success definition (label)
A case is considered **successful** if its event history contains the legal outcome corresponding to the debtor being **discharged from paying the remaining unpaid claims** (event code **178**). All other cases are treated as unsuccessful.

The binary label `success` is assigned at the **person level** by linking each person to their case.

### Questions answered
- How many persons are in the dataset? How many successfully completed the process, and what is the overall success rate?
- Does success differ by sex? Does it differ by court?
- Does success change over time (by a chosen time anchor available in the data)? A simple chart is included.

---

## Repository contents

- **`src/analysis.py`**  
  Commented Python script that:
  1. loads and cleans the two input tables,
  2. derives `sex` from the partially anonymized identifier (using the dataset’s encoding rule),
  3. infers `success` from the event log and assigns it to persons via the case identifier,
  4. computes aggregate metrics:
     - total number of persons, number of successes, overall success rate,
     - success rate by sex,
     - success rate by court,
     - success rate over time,
  5. generates a **PDF plot** (time trend), saved under a fixed filename used later by LaTeX.

- **`report/report.tex`**  
  LaTeX source that builds the final report PDF. It:
  - contains the narrative structure and tables,
  - references the externally generated plot PDF (created by `src/analysis.py`) via `\includegraphics{...}`.

  **Important:** The LaTeX file expects the plot PDF to exist at a specific relative path / filename.  
  If you rename or move the plot, update the path in `report/report.tex`.

- **`report/report.pdf`**  
  The final PDF report (tables + plot).

- **`data/cases.csv`** and **`data/events.csv`**  
  Public sample input files included for demonstration and repository completeness. These files are intentionally fictional and should be understood as portfolio-safe examples rather than real research data.

- **`report/figures/success_over_time.pdf`**  
  A PDF file containing the time-trend plot produced by `src/analysis.py` (included for convenience if present in the repository).

- **`LICENSE`**  
  License file for the repository.
  
---

## How to run

Install Python dependencies:

```bash
pip install -r requirements.txt
