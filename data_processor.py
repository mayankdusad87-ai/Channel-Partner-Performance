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

    # ---------------- CLEAN DATA ----------------
    df[cp_col] = (
        df[cp_col]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.replace("\xa0", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

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

    df[booking_col] = df[booking_col].fillna("").astype(str).str.upper().str.strip()
    df[affinity_col] = df[affinity_col].fillna("").astype(str).str.lower().str.strip()

    # ---------------- DATE ----------------
    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    df_all = df.copy()
    df_valid = df[df["Date"].notna()].copy()

    df_valid["Month"] = df_valid["Date"].dt.to_period("M").astype(str)

    # ---------------- FUNNEL ----------------
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

            "Lost": g[
                (g[visit_col].str.contains("first", na=False)) &
                (g[affinity_col].str.contains("lost", na=False))
            ].shape[0],

            "Bookings": (g[booking_col] == "Y").sum()

        })
    ).reset_index()

    # ---------------- CORE METRICS ----------------
    cp_funnel["Conversion %"] = (
        cp_funnel["Bookings"] / cp_funnel["Fresh_Walkins"].replace(0, 1)
    ) * 100

    cp_funnel["Fresh_to_Hot %"] = (
        cp_funnel["Hot"] / cp_funnel["Fresh_Walkins"].replace(0, 1)
    ) * 100

    cp_funnel["Hot_to_Booking %"] = (
        cp_funnel["Bookings"] / cp_funnel["Hot"].replace(0, 1)
    ) * 100

    cp_funnel["Productivity"] = (
        cp_funnel["Bookings"] / cp_funnel["Fresh_Walkins"].replace(0, 1)
    )

    cp_funnel["Quality Score"] = (
        cp_funnel["Hot"] * 2 +
        cp_funnel["Warm"] * 1 -
        cp_funnel["Cold"] * 1 -
        cp_funnel["Lost"] * 2
    )

    cp_funnel["Leakage"] = (
        cp_funnel["Fresh_Walkins"] -
        (cp_funnel["Hot"] + cp_funnel["Warm"] + cp_funnel["Cold"] + cp_funnel["Lost"])
    )

    # ---------------- DYNAMIC SEGMENTATION ----------------
    fresh_median = cp_funnel["Fresh_Walkins"].median()
    conv_median = cp_funnel["Conversion %"].median()

    def classify(row):
        if row["Fresh_Walkins"] >= fresh_median and row["Conversion %"] >= conv_median:
            return "High Volume - High Conversion"
        elif row["Fresh_Walkins"] >= fresh_median and row["Conversion %"] < conv_median:
            return "High Volume - Low Conversion"
        elif row["Fresh_Walkins"] < fresh_median and row["Conversion %"] >= conv_median:
            return "Low Volume - High Conversion"
        else:
            return "Low Volume - Low Conversion"

    cp_funnel["Segment"] = cp_funnel.apply(classify, axis=1)

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

    active_cp_df = last_30[
        last_30[visit_col].str.contains("first", na=False)
    ][[cp_col, "Date"]]

    active_cp_df = active_cp_df.sort_values(by="Date", ascending=False)
    active_cp_df = active_cp_df.drop_duplicates(subset=[cp_col])

    active_cp_count = active_cp_df[cp_col].nunique()

    return summary, monthly, cp_funnel, active_cp_count, active_cp_df
