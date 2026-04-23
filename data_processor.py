import pandas as pd

def find_column(df, keyword):
    for col in df.columns:
        if keyword.lower() in col.lower():
            return col
    return None


def process_data(df):
    # Clean column names
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace("*", "", regex=False)

    # Detect columns dynamically
    date_col = find_column(df, "Date of Visit")
    visit_col = find_column(df, "Visit type")
    cp_col = find_column(df, "Channel Partner Company")
    booking_col = find_column(df, "Booking Done")

    if not all([date_col, visit_col, cp_col, booking_col]):
        raise Exception("❌ Required columns not found. Please check Excel format.")

    # Convert date
    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    # Create Month
    df["Month"] = df["Date"].dt.to_period("M")

    # Overall Summary
    summary = df.groupby(cp_col).agg(
        Fresh_Walkins=(visit_col, lambda x: (x == "First Visit").sum()),
        Revisits=(visit_col, lambda x: (x == "Revisit").sum()),
        Bookings=(booking_col, lambda x: (x == "Y").sum())
    ).reset_index()

    summary["Conversion %"] = summary["Bookings"] / summary["Fresh_Walkins"].replace(0, 1)
    summary["Revisit Rate"] = summary["Revisits"] / summary["Fresh_Walkins"].replace(0, 1)

    # Monthly Summary
    monthly = df.groupby("Month").agg(
        Fresh=(visit_col, lambda x: (x == "First Visit").sum()),
        Revisits=(visit_col, lambda x: (x == "Revisit").sum()),
        Bookings=(booking_col, lambda x: (x == "Y").sum()),
        Active_CPs=(cp_col, "nunique")
    ).reset_index()

    monthly["Conversion %"] = monthly["Bookings"] / monthly["Fresh"].replace(0, 1)

    # Last 30 Days Active CP
    last_30 = df[df["Date"] >= pd.Timestamp.today() - pd.Timedelta(days=30)]
    active_cp = last_30[last_30[visit_col] == "First Visit"][cp_col].nunique()

    return summary, monthly, active_cp
