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

    # ---------------- CLEAN CHANNEL PARTNER ----------------
    df[cp_col] = (
        df[cp_col]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.replace("\xa0", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # ---------------- CLEAN VISIT TYPE ----------------
    df[visit_col] = (
        df[visit_col]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.replace("\xa0", " ", regex=True)
        .str.replace("\n", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # ---------------- CLEAN OTHER FIELDS ----------------
    df[booking_col] = df[booking_col].fillna("").astype(str).str.upper().str.strip()
    df[affinity_col] = df[affinity_col].fillna("").astype(str).str.lower().str.strip()

    # ---------------- DATE ----------------
    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    df_all = df.copy()
    df_valid = df[df["Date"].notna()].copy()

    df_valid["Month"] = df_valid["Date"].dt.to_period("M").astype(str)

    # ---------------- FUNNEL LOGIC (CORRECTED) ----------------
    cp_funnel = df_all.groupby(cp_col).apply(
        lambda g: pd.Series({

            "Fresh_Walkins": g[g[visit_col].str.contains("first", na=False)].shape[0],

            "Revisits": g[g[visit_col].str.contains("revisit", na=False)].shape[0],

            "Hot": g[
                (g[visit_col].str.contains("first", na=False)) &
                (g[affinity_col].str.contains("hot", na=False))
            ].shape[0],

            "Warm": g[
                (g[visit_col].str.contains("first", na=False)) &
                (g[affinity_col].str.contains("warm", na=False))
            ].shape[0],

            "Cold": g[
                (g[visit_col].str.contains("first", na=False)) &
                (g[affinity_col].str.contains("cold", na=False))
            ].shape[0],

            "Bookings": (g[booking_col] == "Y").sum()

        })
    ).reset_index()

    # ---------------- METRICS ----------------
    cp_funnel["Conversion %"] = (
        cp_funnel["Bookings"] / cp_funnel["Fresh_Walkins"].replace(0, 1)
    ) * 100

    cp_funnel = cp_funnel.round(2)

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

    return summary, monthly, cp_funnel, active_cp
