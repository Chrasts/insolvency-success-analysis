import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12,
    "pdf.fonttype": 42,  
    "ps.fonttype": 42
}) # sets a clearer, more readable font for the exported PDF chart

ROOT_DIR = Path(__file__).resolve().parent.parent  
DATA_DIR = ROOT_DIR / "data"
REPORT_FIG_DIR = ROOT_DIR / "report" / "figures"

cases_CSV = DATA_DIR / "cases.csv"
events_CSV = DATA_DIR / "events.csv"
SUCCESS_TIME_PDF = REPORT_FIG_DIR / "success_over_time.pdf"

def main() -> None:  

  # 1) loading, parsing, and basic preparation of the CSV files
  cases = pd.read_csv(cases_CSV, encoding="latin1")
  events = pd.read_csv(events_CSV, encoding="latin1") # reads input CSVs from configured paths

  cases.columns = cases.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")
  events.columns = events.columns.astype(str).str.strip().str.lower().str.replace(" ", "_") # standardizes and unifies column names in both tables

  cases = cases.astype({"masked_birth_id": "string", "case_id": "string", "court_name": "string", "debtor_order": "string",})
  events = events.astype({"case_id": "string", "event_code": "int64",}) # sets column dtypes

  # 2) sex/gender identification
  sex_digit = pd.to_numeric(cases["masked_birth_id"].str[2], errors="coerce") # takes the 3rd character from "masked_birth_id" and parses it as a number (non-numeric -> NaN)
  cases["sex"] = (sex_digit >= 5).map({True: "F", False: "M"}) # infers sex based on the encoded digit (>= 5 -> female, otherwise male)
  cases.loc[sex_digit.isna(), "sex"] = pd.NA  # for rows where the 3rd character is not numeric, marks sex as NA

  # 3) identifying successful debt relief cases
  success = set(events.loc[events["event_code"] == 178, "case_id"])  # builds a set of case IDs that contain the "success/discharge" event

  persons = cases.copy() # creates a working copy of the "cases" table
  persons["success"] = persons["case_id"].isin(success).astype(int) # flags persons whose case contains event 178 as successful (1), else 0

  # 4) success rate over time
  events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce") # converts the "event_date" column to datetime (invalid values -> NaT)

  req_cases = (events.loc[events["event_code"] == 6, ["case_id", "event_date"]].dropna().sort_values("event_date").drop_duplicates("case_id", keep="first")) # for each case, keeps the earliest date of event 6 (treated as the "request/start year" anchor)

  req_cases["success"] = req_cases["case_id"].isin(success).astype(int) # marks which cases later contain the success event (178)
  req_cases["year"] = req_cases["event_date"].dt.year # extracts the year from the event-6 date

  req = cases[["case_id"]].merge(req_cases[["case_id", "year", "success"]],on="case_id", how="inner") # expands case-level (year, success) back to the person level (because multiple persons can share one case)
  
  # 5) computing and printing results
  print("PERSONS: N =", len(persons), # total number of persons in the dataset
    "| successful =", int(persons["success"].sum()), # number of persons in successful cases
    "| success rate =", round(persons["success"].mean(), 4)) # overall success rate

  print("\nSUCCESS RATE BY SEX/GENDER:") # section header for success-by-sex
  print(persons.groupby("sex")["success"].agg(n_persons="size", n_success="sum", success_rate="mean")) # counts persons, successful persons, and success rate by sex
  print("Unspecified sex/gender:", int(persons["sex"].isna().sum())) # number of persons with missing/unspecified sex

  print("\nSUCCESS RATE BY COURT:")
  print(persons.groupby("court_name")["success"].agg(n_persons="size", n_success="sum", success_rate="mean").sort_values("success_rate", ascending=False)) # aggregates by court and sorts courts by success rate
  
  print("\nSUCCESS OVER TIME (by request year):")
  success_by_year = req.groupby("year")["success"].agg(n_persons="size", n_success="sum", success_rate="mean")
  print(success_by_year) # aggregates by request/start year (counts include multi-debtor cases via person-level expansion)

  # 6) creating a chart of success over time (exports a PDF chart), which is then included in the final PDF report via LaTeX
  g = success_by_year.sort_index()

  plt.figure()
  plt.plot(g.index, g["success_rate"] * 100, marker="o")
  plt.xticks(g.index.astype(int))
  plt.ylim(0, 100)
  plt.xlabel("Request Year")
  plt.ylabel("Percent of persons successfully discharged")
  plt.title("Debt Relief Success Over Time")
  plt.grid(True)
  plt.tight_layout()
  REPORT_FIG_DIR.mkdir(parents=True, exist_ok=True)
  plt.savefig(SUCCESS_TIME_PDF, bbox_inches="tight")
  plt.close()
    
if __name__ == "__main__":
    main()