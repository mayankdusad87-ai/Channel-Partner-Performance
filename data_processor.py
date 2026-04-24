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

    # ---------------- CLEAN STRINGS ----------------
    # 🔥 IMPORTANT FIX FOR VISIT TYPE
    df[visit_col] = (
        df[visit_col]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.replace("\xa0", " ", regex=True)   # hidden space fix
        .str.replace("\n", " ", regex=True)     # line break fix
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

    # ---------------- DATE HANDLING ----------------
    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    # Keep all rows for CP logic
    df_all = df.copy()

    # Use only valid dates for time-based analysis
    df_valid = df[df["Date"].notna()].copy()

    df_valid["Month"] = df_valid["Date"].dt.to_period("M").astype(str)

    # ---------------- FUNNEL (FIXED LOGIC) ----------------
    cp_funnel = df_all.groupby(cp_col).agg(
        Fresh_Walkins=(visit_col, lambda x: x.str.contains("first", na=False).sum()),
        Revisits=(visit_col, lambda x: x.str.contains("revisit", na=False).sum()),
        Hot=(affinity_col, lambda x: x.str.contains("hot", na=False).sum()),
        Warm=(affinity_col, lambda x: x.str.contains("warm", na=False).sum()),
        Cold=(affinity_col, lambda x: x.str.contains("cold", na=False).sum()),
        Bookings=(booking_col, lambda x: (x == "Y").sum())
    ).reset_index()

    # ---------------- METRICS ----------------
    cp_funnel["Conversion %"] = (
        cp_funnel["Bookings"] / cp_funnel["Fresh_Walkins"].replace(0, 1)
    ) * 100

    cp_funnel = cp_funnel.round(2)

    # ---------------- SUMMARY ----------------
    summary = cp_funnel.copy()

    # ---------------- MONTHLY ----------------
    monthly = df_valid.groupby("Month").agg(
        Fresh=("Date", "count"),
        Bookings=(booking_col, lambda x: (x == "Y").sum())
    ).reset_index()

    monthly["Conversion %"] = (
        monthly["Bookings"] / monthly["Fresh"].replace(0, 1)
    ) * 100

    monthly = monthly.round(2)

    # ---------------- ACTIVE CP ----------------
    last_30 = df_valid[
        df_valid["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=30)
    ]

    active_cp = last_30[cp_col].nunique()

    # ---------------- DEBUG (optional) ----------------
    # print("Unique Visit Types:", df[visit_col].unique())

    return summary, monthly, cp_funnel, active_cp    return summary, monthly, cp_funnel, active_cp
