import pandas as pd

def normalize(text):
    return text.lower().replace("*", "").replace("(", "").replace(")", "").strip()

def find_column(df, keywords):
    for col in df.columns:
        col_norm = normalize(col)
        for key in keywords:
            if key in col_norm:
                return col
    return None


def process_data(df):
    # Clean column names
    df.columns = df.columns.str.strip()

    # Debug (IMPORTANT – remove later)
    print("Columns found:", df.columns.tolist())

    # Flexible column detection
    date_col = find_column(df, ["date of visit"])
    visit_col = find_column(df, ["visit type"])
    cp_col = find_column(df, ["channel partner company"])
    booking_col = find_column(df, ["booking done"])

    # Fail-safe fallback (very important)
    if not date_col:
        raise Exception(f"❌ Date column not found. Available columns: {df.columns.tolist()}")
    if not visit_col:
        raise Exception(f"❌ Visit type column not found. Available columns: {df.columns.tolist()}")
    if not cp_col:
        raise Exception(f"❌ Channel Partner column not found. Available columns: {df.columns.tolist()}")
    if not booking_col:
        raise Exception(f"❌ Booking column not found. Available columns: {df.columns.tolist()}")

    # Convert date
    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    # Create Month
    df["Month"] = df["Date"].dt.to_period("M")

    # Standardize values (VERY IMPORTANT)
    df[visit_col] = df[visit_col].astype(str).str.strip().str.lower()
    df[booking_col] = df[booking_col].astype(str).str.strip().str.upper()

    # Overall Summary
    summary = df.groupby(cp_col).agg(
        Fresh_Walkins=(visit_col, lambda x: (x.str.contains("first")).sum()),
        Revisits=(visit_col, lambda x: (x.str.contains("revisit")).sum()),
        Bookings=(booking_col, lambda x: (x == "Y").sum())
    ).reset_index()

    summary["Conversion %"] = summary["Bookings"] / summary["Fresh_Walkins"].replace(0, 1)
    summary["Revisit Rate"] = summary["Revisits"] / summary["Fresh_Walkins"].replace(0, 1)

    # Monthly Summary
    monthly = df.groupby("Month").agg(
        Fresh=(visit_col, lambda x: (x.str.contains("first")).sum()),
        Revisits=(visit_col, lambda x: (x.str.contains("revisit")).sum()),
        Bookings=(booking_col, lambda x: (x == "Y").sum()),
        Active_CPs=(cp_col, "nunique")
    ).reset_index()

    monthly["Conversion %"] = monthly["Bookings"] / monthly["Fresh"].replace(0, 1)

    # Last 30 Days Active CP
    last_30 = df[df["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=30)]
    active_cp = last_30[last_30[visit_col].str.contains("first")][cp_col].nunique()

    return summary, monthly, active_cp
