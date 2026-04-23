import pandas as pd

def process_data(df):

    # Clean column names
    df.columns = df.columns.str.strip()

    # ---------------- COLUMN DETECTION ----------------
    date_col = None
    visit_col = None
    cp_col = None
    booking_col = None

    for col in df.columns:
        col_lower = col.lower()

        if "date of visit" in col_lower:
            date_col = col

        if "visit type" in col_lower:
            visit_col = col

        if "channel partner company" in col_lower:
            cp_col = col

        if "booking done" in col_lower:
            booking_col = col

    # ---------------- VALIDATION ----------------
    if not date_col:
        raise Exception("❌ Date column not found")

    if not visit_col:
        raise Exception("❌ Visit type column not found")

    if not cp_col:
        raise Exception("❌ Channel Partner column not found")

    if not booking_col:
        raise Exception("❌ Booking column not found")

    # ---------------- CLEAN DATA ----------------
    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])

    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    df[visit_col] = df[visit_col].fillna("").astype(str).str.lower().str.strip()
    df[booking_col] = df[booking_col].fillna("").astype(str).str.upper().str.strip()

    # ---------------- OVERALL ----------------
    summary = df.groupby(cp_col).agg(
        Fresh_Walkins=(visit_col, lambda x: x.astype(str).str.contains("first", na=False).sum()),
        Revisits=(visit_col, lambda x: x.astype(str).str.contains("revisit", na=False).sum()),
        Bookings=(booking_col, lambda x: (x.astype(str) == "Y").sum())
    ).reset_index()

    summary["Fresh_Walkins"] = summary["Fresh_Walkins"].replace(0, 1)

    summary["Conversion %"] = (summary["Bookings"] / summary["Fresh_Walkins"]) * 100
    summary["Revisit Rate"] = (summary["Revisits"] / summary["Fresh_Walkins"]) * 100

    summary = summary.round(2)

    # ---------------- MONTHLY ----------------
    monthly = df.groupby("Month").agg(
        Fresh=(visit_col, lambda x: x.astype(str).str.contains("first", na=False).sum()),
        Revisits=(visit_col, lambda x: x.astype(str).str.contains("revisit", na=False).sum()),
        Bookings=(booking_col, lambda x: (x.astype(str) == "Y").sum()),
        Active_CPs=(cp_col, "nunique")
    ).reset_index()

    monthly["Fresh"] = monthly["Fresh"].replace(0, 1)
    monthly["Conversion %"] = (monthly["Bookings"] / monthly["Fresh"]) * 100

    monthly = monthly.round(2)

    # ---------------- LAST 30 DAYS ----------------
    last_30 = df[df["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=30)]

    active_cp = last_30[
        last_30[visit_col].astype(str).str.contains("first", na=False)
    ][cp_col].nunique()

    return summary, monthly, active_cp
