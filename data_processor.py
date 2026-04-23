import pandas as pd

def process_data(df):
    df.columns = df.columns.str.strip()

    df['Date of Visit'] = pd.to_datetime(df['Date of Visit* (DD-MM-YYYY)'], dayfirst=True, errors='coerce')

    # Filters
    fresh = df[df['Visit type'] == 'First Visit']
    revisit = df[df['Visit type'] == 'Revisit']
    bookings = df[df['Booking Done (Y/N)'] == 'Y']

    # Summary
    summary = df.groupby('Channel Partner Company*').agg(
        Fresh_Walkins=('Visit type', lambda x: (x == 'First Visit').sum()),
        Revisits=('Visit type', lambda x: (x == 'Revisit').sum()),
        Bookings=('Booking Done (Y/N)', lambda x: (x == 'Y').sum())
    ).reset_index()

    summary['Conversion %'] = summary['Bookings'] / summary['Fresh_Walkins']
    summary['Revisit Rate'] = summary['Revisits'] / summary['Fresh_Walkins']

    # Monthly
    df['Month'] = df['Date of Visit'].dt.to_period('M')

    monthly = df.groupby('Month').agg(
        Fresh=('Visit type', lambda x: (x == 'First Visit').sum()),
        Revisits=('Visit type', lambda x: (x == 'Revisit').sum()),
        Bookings=('Booking Done (Y/N)', lambda x: (x == 'Y').sum()),
        Active_CPs=('Channel Partner Company*', 'nunique')
    ).reset_index()

    monthly['Conversion %'] = monthly['Bookings'] / monthly['Fresh']

    # Last 30 days active CP
    last_30 = df[df['Date of Visit'] >= pd.Timestamp.today() - pd.Timedelta(days=30)]
    active_cp = last_30[last_30['Visit type'] == 'First Visit']['Channel Partner Company*'].nunique()

    return summary, monthly, active_cp
