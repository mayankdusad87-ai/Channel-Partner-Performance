import pandas as pd

def process_data(df):

    df.columns = df.columns.fillna("").astype(str).str.strip()

    def find(name):
        for col in df.columns:
            if name in col.lower():
                return col
        return None

    date_col = find("date of visit")
    visit_col = find("visit type")
    cp_col = find("channel partner")
    booking_col = find("booking done")
    affinity_col = find("affinity")

    if not all([date_col, visit_col, cp_col, booking_col, affinity_col]):
        raise Exception("❌ Required columns missing")

    # ---------------- CLEAN ----------------
    df[cp_col] = df[cp_col].astype(str).str.upper().str.strip()
    df[visit_col] = df[visit_col].astype(str).str.lower().str.strip()
    df[booking_col] = df[booking_col].astype(str).str.upper().str.strip()
    df[affinity_col] = df[affinity_col].astype(str).str.lower().str.strip()

    df["Date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
    df = df[df["Date"].notna()]

    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    # ---------------- LIFECYCLE ----------------
    total_months = df["Month"].nunique()

    if total_months <= 3:
        lifecycle = "EARLY"
    elif total_months <= 6:
        lifecycle = "GROWTH"
    else:
        lifecycle = "MATURE"

    # ---------------- FUNNEL ----------------
    cp = df.groupby(cp_col).apply(
        lambda g: pd.Series({
            "Fresh": g[g[visit_col].str.contains("first")].shape[0],
            "Revisit": g[g[visit_col].str.contains("revisit")].shape[0],
            "Hot": g[g[affinity_col].str.contains("hot")].shape[0],
            "Warm": g[g[affinity_col].str.contains("warm")].shape[0],
            "Cold": g[g[affinity_col].str.contains("cold")].shape[0],
            "Lost": g[g[affinity_col].str.contains("lost")].shape[0],
            "Bookings": (g[booking_col] == "Y").sum()
        })
    ).reset_index()

    # ---------------- METRICS ----------------
    cp["Conversion %"] = (cp["Bookings"] / cp["Fresh"].replace(0,1))*100
    cp["Hot %"] = (cp["Hot"] / cp["Fresh"].replace(0,1))*100
    cp["Hot→Booking %"] = (cp["Bookings"] / cp["Hot"].replace(0,1))*100

    # ---------------- ROOT CAUSE ----------------
    def diagnose(row):
        if row["Fresh"] > 20 and row["Conversion %"] < 5:
            return "CLOSING ISSUE"
        elif row["Fresh"] > 20 and row["Hot %"] < 20:
            return "POOR LEAD QUALITY"
        elif row["Fresh"] < 10 and row["Conversion %"] > 10:
            return "LOW VOLUME HIGH QUALITY"
        elif row["Fresh"] < 10:
            return "INACTIVE CP"
        else:
            return "STABLE"

    cp["Problem"] = cp.apply(diagnose, axis=1)

    # ---------------- STRATEGY ----------------
    def strategy(row):
        if row["Conversion %"] > 10 and row["Fresh"] > 20:
            return "SCALE"
        elif row["Problem"] == "CLOSING ISSUE":
            return "FIX"
        elif row["Problem"] == "LOW VOLUME HIGH QUALITY":
            return "INCUBATE"
        else:
            return "DROP"

    cp["Strategy"] = cp.apply(strategy, axis=1)

    # ---------------- ACTIONS ----------------
    def action(row):
        if row["Strategy"] == "SCALE":
            return "Increase allocation + priority inventory"
        elif row["Strategy"] == "FIX":
            return "Sales training + joint closing support"
        elif row["Strategy"] == "INCUBATE":
            return "Increase lead flow + marketing push"
        else:
            return "Reduce focus / replace"

    cp["Action"] = cp.apply(action, axis=1)

    cp["Lifecycle"] = lifecycle

    # ---------------- MONTHLY ----------------
    monthly = df.groupby("Month").agg(
        Fresh=("Date","count"),
        Bookings=(booking_col, lambda x: (x=="Y").sum())
    ).reset_index()
    monthly["Conversion %"] = (monthly["Bookings"]/monthly["Fresh"])*100

    return cp.round(2), monthly.round(2)
