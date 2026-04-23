import pandas as pd
import re

# ---------------- NORMALIZATION ----------------
def normalize(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9 ]', ' ', text)  # remove special chars
    text = re.sub(r'\s+', ' ', text)         # remove extra spaces
    return text.strip()

# ---------------- COLUMN FINDER ----------------
def find_column(df, keywords):
    for col in df.columns:
        col_norm = normalize(col)
        for key in keywords:
            if key in col_norm:
                return col
    return None


# ---------------- MAIN FUNCTION ----------------
def process_data(df):

    # Clean column names
    df.columns = df.columns.str.strip()

    # DEBUG (keep for now)
    print("Columns found:", df.columns.tolist())

    # ---------------- DETECT COLUMNS ----------------
    date_col = find_column(df, ["date visit", "visit date", "date"])
    visit_col = find_column(df, ["visit type"])
    cp_col = find_column(df, ["channel partner"])
    booking_col = find_column(df, ["booking done", "booking"])

    # ---------------- VALIDATION ----------------
    if not date_col:
        raise Exception(f"❌ Date column not found. Columns: {df.columns.tolist()}")

    if not visit_col:
        raise Exception(f"❌ Visit type column not found. Columns: {df.columns.tolist()}")

    if not cp_col:
        raise Exception(f"❌ Channel Partner column not found. Columns: {df.columns.tolist()}")

    if not booking_col:
        raise Exception(f"❌ Booking column not found. Columns: {df.columns.tolist()}")

    # ---------------- DATE PROCESSING ----------------
    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    # Drop invalid dates
    df = df.dropna(subset=["Date"])

    # ---------------- MONTH ----------------
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    # ---------------- STANDARDIZE VALUES ----------------
    df[visit_col] = df[visit_col].astype(str).str.lower().str.strip()
    df[booking_col] = df[booking_col].astype(str).str.upper().str.strip()

    # ---------------- OVERALL SUMMARY ----------------
    summary = df.groupby(cp_col).agg(
        Fresh_Walkins=(visit_col, lambda x: x.str.contains("first").sum()),
        Revisits=(visit_col, lambda x: x.str.contains("revisit").sum()),
        Bookings=(booking_col, lambda x: (x == "Y").sum())
    ).reset_index()

    # Avoid division errors
    summary["Fresh_Walkins"] = summary["Fresh_Walkins"].replace(0, 1)

    summary["Conversion %"] = (summary["Bookings"] / summary["Fresh_Walkins"]) * 100
    summary["Revisit Rate"] = (summary["Revisits"] / summary["Fresh_Walkins"]) * 100

    summary = summary.round(2)

    # ---------------- MONTHLY SUMMARY ----------------
    monthly = df.groupby("Month").agg(
        Fresh=(visit_col, lambda x: x.str.contains("first").sum()),
        Revisits=(visit_col, lambda x: x.str.contains("revisit").sum()),
        Bookings=(booking_col, lambda x: (x == "Y").sum()),
        Active_CPs=(cp_col, "nunique")
    ).reset_index()

    monthly["Fresh"] = monthly["Fresh"].replace(0, 1)

    monthly["Conversion %"] = (monthly["Bookings"] / monthly["Fresh"]) * 100
    monthly = monthly.round(2)

    # ---------------- LAST 30 DAYS ----------------
    last_30 = df[df["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=30)]

    active_cp = last_30[
        last_30[visit_col].str.contains("first")
    ][cp_col].nunique()

    return summary, monthly, active_cp
