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

    # ---------------- DATE CLEANING ----------------
    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    # ⚠️ Drop only invalid dates
    df = df.dropna(subset=["Date"])

    # ---------------- STRING CLEANING ----------------
    df[visit_col] = (
        df[visit_col]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
    )

    df[booking_col] = (
        df[booking_col]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df[affinity_col] = (
        df[affinity_col]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
    )

    # ---------------- MONTH ----------------
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    # ---------------- FUNNEL (FIXED LOGIC) ----------------
    cp_funnel = df.groupby(cp_col).agg(
        Fresh_Walkins=(visit_col, lambda x: (x == "first visit").sum()),
        Revisits=(visit_col, lambda x: (x == "revisit").sum()),
        Hot=(affinity_col, lambda x: (x == "hot").sum()),
        Warm=(affinity_col, lambda x: (x == "warm").sum()),
        Cold=(affinity_col, lambda x: (x == "cold").sum()),
        Bookings=(booking_col, lambda x: (x == "Y").sum())
    ).reset_index()

    # ---------------- CONVERSION ----------------
    cp_funnel["Conversion %"] = (
        cp_funnel["Bookings"] / cp_funnel["Fresh_Walkins"].replace(0, 1)
    ) * 100

    cp_funnel = cp_funnel.round(2)

    # ---------------- SUMMARY ----------------
    summary = cp_funnel.copy()

    # ---------------- MONTHLY ----------------
    monthly = df.groupby("Month").agg(
        Fresh=("Date", "count"),
        Bookings=(booking_col, lambda x: (x == "Y").sum())
    ).reset_index()

    monthly["Conversion %"] = (
        monthly["Bookings"] / monthly["Fresh"].replace(0, 1)
    ) * 100

    monthly = monthly.round(2)

    # ---------------- ACTIVE CP ----------------
    last_30 = df[df["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=30)]
    active_cp = last_30[cp_col].nunique()

    return summary, monthly, cp_funnel, active_cp
