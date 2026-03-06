import pandas as pd
import matplotlib.pyplot as plt


plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12,
    "pdf.fonttype": 42,  
    "ps.fonttype": 42
}) # sets a clearer, more readable font for the exported PDF chart

UDAJE_PATH = r"C:\Users\bbbac\Documents\portfol projekty\Python_insolvence\udaje.csv"        # TODO: replace with your local path
UDALOSTI_PATH = r"C:\Users\bbbac\Documents\portfol projekty\Python_insolvence\udalosti.csv"  # TODO: replace with your local path

def main() -> None:  

  # 1) loading, parsing, and basic preparation of the CSV files
  udaje = pd.read_csv(UDAJE_PATH, sep=";")
  udalosti = pd.read_csv(UDALOSTI_PATH, sep=";") # reads input CSVs from configured paths

  udaje.columns = udaje.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")
  udalosti.columns = udalosti.columns.astype(str).str.strip().str.lower().str.replace(" ", "_") # standardizes and unifies column names in both tables

  udaje = udaje.astype({"rc": "string", "spisova_znacka": "string", "soud_name": "string", "debtors": "string",})
  udalosti = udalosti.astype({"spisova_znacka": "string", "udalost": "int64",}) # sets column dtypes

  # 2) sex/gender identification
  sex_digit = pd.to_numeric(udaje["rc"].str[2], errors="coerce") # takes the 3rd character from "rc" and parses it as a number (non-numeric -> NaN)
  udaje["sex"] = (sex_digit >= 5).map({True: "F", False: "M"}) # infers sex based on the encoded digit (>= 5 -> female, otherwise male)
  udaje.loc[sex_digit.isna(), "sex"] = pd.NA  # for rows where the 3rd character is not numeric, marks sex as NA

  # 3) identifying successful debt relief cases
  success = set(udalosti.loc[udalosti["udalost"] == 178, "spisova_znacka"])  # builds a set of case IDs that contain the "success/discharge" event

  persons = udaje.copy() # creates a working copy of the "udaje" table
  persons["success"] = persons["spisova_znacka"].isin(success).astype(int) # flags persons whose case contains event 178 as successful (1), else 0

  # 4) success rate over time
  udalosti["datum"] = pd.to_datetime(udalosti["datum"], errors="coerce") # converts the "datum" column to datetime (invalid values -> NaT)

  req_cases = (udalosti.loc[udalosti["udalost"] == 6, ["spisova_znacka", "datum"]].dropna().sort_values("datum").drop_duplicates("spisova_znacka", keep="first")) # for each case, keeps the earliest date of event 6 (treated as the "request/start year" anchor)

  req_cases["success"] = req_cases["spisova_znacka"].isin(success).astype(int) # marks which cases later contain the success event (178)
  req_cases["year"] = req_cases["datum"].dt.year # extracts the year from the event-6 date

  req = udaje[["spisova_znacka"]].merge(req_cases[["spisova_znacka", "year", "success"]],on="spisova_znacka", how="inner") # expands case-level (year, success) back to the person level (because multiple persons can share one case)
  
  # 5) computing and printing results
  print("PERSONS: N =", len(persons), # total number of persons in the dataset
    "| successful =", int(persons["success"].sum()), # number of persons in successful cases
    "| success rate =", round(persons["success"].mean(), 4)) # overall success rate

  print("\nSUCCESS RATE BY SEX/GENDER:") # section header for success-by-sex
  print(persons.groupby("sex")["success"].agg(n_persons="size", n_success="sum", success_rate="mean")) # counts persons, successful persons, and success rate by sex
  print("Unspecified sex/gender:", int(persons["sex"].isna().sum())) # number of persons with missing/unspecified sex

  print("\nSUCCESS RATE BY COURT:")
  print(persons.groupby("soud_name")["success"].agg(n_persons="size", n_success="sum", success_rate="mean").sort_values("success_rate", ascending=False)) # aggregates by court and sorts courts by success rate
  
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
  plt.savefig("success_over_time.pdf")
  plt.close()
    
if __name__ == "__main__":
    main()