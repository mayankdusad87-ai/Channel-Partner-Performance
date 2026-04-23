import pandas as pd

def process_data(df):

    df.columns = df.columns.fillna("").astype(str).str.strip()

    # 🔍 column detection
    def find(col_name):
        for col in df.columns:
            if col_name in col.lower():
                return col
        return None

    date_col = find("date of visit")
    visit_col = find("visit type")
    cp_col = find("channel partner")
    booking_col = find("booking done")

    if not all([date_col, visit_col, cp_col, booking_col]):
        raise Exception("❌ Required columns not found")

    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])

    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    df[visit_col] = df[visit_col].fillna("").astype(str).str.lower()
    df[booking_col] = df[booking_col].fillna("").astype(str).str.upper()

    summary = df.groupby(cp_col).agg(
        Fresh_Walkins=(visit_col, lambda x: x.str.contains("first", na=False).sum()),
        Revisits=(visit_col, lambda x: x.str.contains("revisit", na=False).sum()),
        Bookings=(booking_col, lambda x: (x == "Y").sum())
    ).reset_index()

    summary["Fresh_Walkins"] = summary["Fresh_Walkins"].replace(0, 1)

    summary["Conversion %"] = (summary["Bookings"] / summary["Fresh_Walkins"]) * 100
    summary["Revisit Rate"] = (summary["Revisits"] / summary["Fresh_Walkins"]) * 100

    summary = summary.round(2)

    monthly = df.groupby("Month").agg(
        Fresh=(visit_col, lambda x: x.str.contains("first", na=False).sum()),
        Revisits=(visit_col, lambda x: x.str.contains("revisit", na=False).sum()),
        Bookings=(booking_col, lambda x: (x == "Y").sum()),
        Active_CPs=(cp_col, "nunique")
    ).reset_index()

    monthly["Fresh"] = monthly["Fresh"].replace(0, 1)
    monthly["Conversion %"] = (monthly["Bookings"] / monthly["Fresh"]) * 100

    monthly = monthly.round(2)

    last_30 = df[df["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=30)]
    active_cp = last_30[last_30[visit_col].str.contains("first", na=False)][cp_col].nunique()

    return summary, monthly, active_cp
