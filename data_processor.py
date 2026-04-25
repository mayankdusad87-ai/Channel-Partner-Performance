import pandas as pd

def process_data(df):

    # ---------------- CLEAN COLUMN NAMES ----------------
    df.columns = df.columns.astype(str).str.strip()

    # ---------------- FIX COLUMN NAMES ----------------
    cp_col = "Channel Partner Company*"
    date_col = [c for c in df.columns if "date" in c.lower()][0]
    visit_col = [c for c in df.columns if "visit" in c.lower()][0]
    booking_col = [c for c in df.columns if "booking" in c.lower()][0]
    affinity_col = [c for c in df.columns if "affinity" in c.lower()][0]

    # ---------------- CLEAN DATA ----------------
    df[cp_col] = df[cp_col].astype(str).str.upper().str.strip()
    df[visit_col] = df[visit_col].astype(str).str.lower().str.strip()
    df[booking_col] = df[booking_col].astype(str).str.upper().str.strip()
    df[affinity_col] = df[affinity_col].astype(str).str.lower().str.strip()

    df["Date"] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
    df = df[df["Date"].notna()]

    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    # ---------------- LIFECYCLE ----------------
    months = df["Month"].nunique()

    if months <= 3:
        lifecycle = "EARLY"
    elif months <= 6:
        lifecycle = "GROWTH"
    else:
        lifecycle = "MATURE"

    # ---------------- FUNNEL ----------------
    cp = df.groupby(cp_col).apply(
        lambda g: pd.Series({
            "Fresh": g[g[visit_col].str.contains("first")].shape[0],
            "Hot": g[g[affinity_col].str.contains("hot")].shape[0],
            "Warm": g[g[affinity_col].str.contains("warm")].shape[0],
            "Cold": g[g[affinity_col].str.contains("cold")].shape[0],
            "Bookings": (g[booking_col] == "Y").sum()
        })
    ).reset_index()

    cp = cp.rename(columns={cp.columns[0]: "Channel Partner"})

    # ---------------- METRICS ----------------
    cp["Conversion %"] = (cp["Bookings"] / cp["Fresh"].replace(0,1))*100
    cp["Hot %"] = (cp["Hot"] / cp["Fresh"].replace(0,1))*100
    cp["Hot→Booking %"] = (cp["Bookings"] / cp["Hot"].replace(0,1))*100

    # ---------------- DIAGNOSIS ----------------
    def problem(row):
        if row["Fresh"] > 20 and row["Conversion %"] < 5:
            return "CLOSING ISSUE"
        elif row["Hot %"] < 20:
            return "POOR LEAD QUALITY"
        elif row["Fresh"] < 10:
            return "LOW VOLUME"
        else:
            return "STABLE"

    cp["Problem"] = cp.apply(problem, axis=1)

    # ---------------- STRATEGY ----------------
    def strategy(row):
        if row["Conversion %"] > 10 and row["Fresh"] > 20:
            return "SCALE"
        elif row["Problem"] == "CLOSING ISSUE":
            return "FIX"
        elif row["Problem"] == "LOW VOLUME":
            return "INCUBATE"
        else:
            return "DROP"

    cp["Strategy"] = cp.apply(strategy, axis=1)

    # ---------------- ACTION ----------------
    def action(row):
        if row["Strategy"] == "SCALE":
            return "Increase inventory allocation + priority deals"
        elif row["Strategy"] == "FIX":
            return "Do joint site visits + closing support"
        elif row["Strategy"] == "INCUBATE":
            return "Increase lead flow + marketing push"
        else:
            return "Reduce focus / remove from network"

    cp["Action"] = cp.apply(action, axis=1)

    cp["Lifecycle"] = lifecycle

    # ---------------- MONTHLY ----------------
    monthly = df.groupby("Month").agg(
        Fresh=("Date","count"),
        Bookings=(booking_col, lambda x: (x=="Y").sum())
    ).reset_index()

    monthly["Conversion %"] = (monthly["Bookings"]/monthly["Fresh"])*100

    return cp.round(2), monthly.round(2)
