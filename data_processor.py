import pandas as pd

def process_data(df):

    # ---------------- CLEAN COLUMN NAMES ----------------
    df.columns = df.columns.fillna("").astype(str).str.strip()

    def find(name):
        for col in df.columns:
            if name in col.lower():
                return col
        return None

    # ---------------- COLUMN DETECTION ----------------
    date_col = find("date of visit")
    visit_col = find("visit type")
    cp_col = find("channel partner")
    booking_col = find("booking done")
    affinity_col = find("affinity")

    if not all([date_col, visit_col, cp_col, booking_col, affinity_col]):
        raise Exception("❌ Required columns missing in CIF sheet")

    # ---------------- STRING CLEANING ----------------
    df[visit_col] = df[visit_col].fillna("").astype(str).str.lower().str.strip()
    df[booking_col] = df[booking_col].fillna("").astype(str).str.upper().str.strip()
    df[affinity_col] = df[affinity_col].fillna("").astype(str).str.lower().str.strip()

    # ---------------- DATE PARSING (SAFE) ----------------
    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    # 👉 Split data:
    df_valid_dates = df[df["Date"].notna()].copy()   # for monthly
    df_all = df.copy()                               # for CP analysis (NO DROPS)

    # ---------------- MONTH (ONLY VALID DATES) ----------------
    df_valid_dates["Month"] = df_valid_dates["Date"].dt.to_period("M").astype(str)

    # ---------------- FUNNEL (USE FULL DATA) ----------------
    cp_funnel = df_all.groupby(cp_col).agg(
        Fresh_Walkins=(visit_col, lambda x: (x == "first visit").sum()),
        Revisits=(visit_col, lambda x: (x == "revisit").sum()),
        Hot=(affinity_col, lambda x: (x == "hot").sum()),
        Warm=(affinity_col, lambda x: (x == "warm").sum()),
        Cold=(affinity_col, lambda x: (x == "cold").sum()),
        Bookings=(booking_col, lambda x: (x == "Y").sum())
    ).reset_index()

    cp_funnel["Conversion %"] = (
        cp_funnel["Bookings"] / cp_funnel["Fresh_Walkins"].replace(0, 1)
    ) * 100

    cp_funnel = cp_funnel.round(2)

    # ---------------- SUMMARY ----------------
    summary = cp_funnel.copy()

    # ---------------- MONTHLY (ONLY VALID DATES) ----------------
    monthly = df_valid_dates.groupby("Month").agg(
        Fresh=("Date", "count"),
        Bookings=(booking_col, lambda x: (x == "Y").sum())
    ).reset_index()

    monthly["Conversion %"] = (
        monthly["Bookings"] / monthly["Fresh"].replace(0, 1)
    ) * 100

    monthly = monthly.round(2)

    # ---------------- ACTIVE CP (ONLY VALID DATES) ----------------
    last_30 = df_valid_dates[
        df_valid_dates["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=30)
    ]

    active_cp = last_30[cp_col].nunique()

    # ---------------- DATA QUALITY WARNING ----------------
    invalid_dates = df["Date"].isna().sum()
    if invalid_dates > 0:
        print(f"⚠️ {invalid_dates} rows had invalid dates (excluded from monthly, included in CP analysis)")

    return summary, monthly, cp_funnel, active_cp
