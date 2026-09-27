"""
ETL Pipeline for UCI Bank Marketing Dataset -> Power BI Funnel Analysis
Transforms raw bank-additional-full.csv into a clean Star Schema with Funnel event models.
"""

import os
import sys
import calendar
import datetime
import pandas as pd
import numpy as np

def run_etl():
    base_dir = r"C:\Users\sahad\.gemini\antigravity\scratch\bank_marketing_funnel_powerbi"
    raw_path = os.path.join(base_dir, "bank-additional", "bank-additional-full.csv")
    out_dir = os.path.join(base_dir, "clean_data")
    os.makedirs(out_dir, exist_ok=True)

    print("Loading raw data from:", raw_path)
    df = pd.read_csv(raw_path, sep=";")
    print(f"Raw rows: {len(df):,}, columns: {df.shape[1]}")

    # 1. Timeline & Dates
    years = []
    for idx in range(len(df)):
        if idx < 27690:
            years.append(2008)
        elif idx < 39130:
            years.append(2009)
        else:
            years.append(2010)
    df["year"] = years

    month_map = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 
                 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
    dow_map = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4}

    date_lookup = {}
    for y in [2008, 2009, 2010]:
        for m in range(1, 13):
            cal = calendar.monthcalendar(y, m)
            for dow in range(5):
                valid_days = [week[dow] for week in cal if week[dow] != 0]
                date_lookup[(y, m, dow)] = [datetime.date(y, m, d) for d in valid_days]

    counts = {}
    call_dates = []
    for idx, row in df.iterrows():
        y = row["year"]
        m = month_map[row["month"]]
        dow = dow_map[row["day_of_week"]]
        valid_list = date_lookup[(y, m, dow)]
        key = (y, m, dow)
        c = counts.get(key, 0)
        chosen_date = valid_list[c % len(valid_list)]
        counts[key] = c + 1
        call_dates.append(chosen_date)

    df["CallDate"] = call_dates
    df["DateKey"] = [int(d.strftime("%Y%m%d")) for d in call_dates]
    df["LeadID"] = [f"LEAD-{i+1:06d}" for i in range(len(df))]

    # 2. Text Normalization
    df["Job"] = df["job"].str.replace(".", "", regex=False).str.title()
    df["Marital"] = df["marital"].str.title()
    df["Education"] = df["education"].str.replace(".", " ", regex=False).str.title()
    df["Education"] = df["Education"].replace({
        "Basic 4Y": "Basic (4y)",
        "Basic 6Y": "Basic (6y)",
        "Basic 9Y": "Basic (9y)",
        "High School": "High School",
        "Professional Course": "Professional Course",
        "University Degree": "University Degree"
    })
    df["CreditDefault"] = df["default"].str.title()
    df["HousingLoan"] = df["housing"].str.title()
    df["PersonalLoan"] = df["loan"].str.title()
    df["Channel"] = df["contact"].map({"cellular": "Cellular", "telephone": "Telephone (Landline)"})
    df["PriorOutcome"] = df["poutcome"].str.title()

    # 3. Dim_Demographics
    demo_cols = ["age", "Job", "Marital", "Education", "CreditDefault", "HousingLoan", "PersonalLoan"]
    dim_demo = df[demo_cols].drop_duplicates().reset_index(drop=True)
    dim_demo["DemographicKey"] = range(1, len(dim_demo) + 1)
    
    def age_bracket(age):
        if age < 30: return "<30 Young Adult"
        if age <= 45: return "30-45 Prime Working"
        if age <= 60: return "46-60 Mature Adult"
        return "60+ Senior"
    dim_demo["AgeGroup"] = dim_demo["age"].apply(age_bracket)

    def job_category(job):
        if job in ["Admin", "Management", "Technician"]: return "White Collar"
        if job in ["Blue-Collar", "Services", "Housemaid"]: return "Blue Collar / Services"
        if job in ["Entrepreneur", "Self-Employed"]: return "Business Owner / Self-Employed"
        if job in ["Student", "Retired"]: return "Student / Retiree"
        return "Other / Unknown"
    dim_demo["JobCategory"] = dim_demo["Job"].apply(job_category)

    df = df.merge(dim_demo, on=demo_cols, how="left")

    # 4. Dim_Channel
    dim_channel = pd.DataFrame([
        {"ChannelKey": 1, "Channel": "Cellular", "ChannelType": "Mobile Direct", "ChannelDescription": "Direct mobile phone outreach to prospective client"},
        {"ChannelKey": 2, "Channel": "Telephone (Landline)", "ChannelType": "Fixed Wireline", "ChannelDescription": "Fixed-line landline telephone outreach"}
    ])
    df = df.merge(dim_channel[["ChannelKey", "Channel"]], on="Channel", how="left")

    # 5. Dim_Date
    min_date = df["CallDate"].min()
    max_date = df["CallDate"].max()
    full_dates = pd.date_range(min_date, max_date, freq="D")
    dim_date = pd.DataFrame({
        "Date": full_dates.date,
        "DateKey": [int(d.strftime("%Y%m%d")) for d in full_dates],
        "Year": full_dates.year,
        "Quarter": ["Q" + str(q) for q in full_dates.quarter],
        "YearQuarter": [f"{d.year}-Q{d.quarter}" for d in full_dates],
        "MonthName": full_dates.strftime("%B"),
        "MonthShort": full_dates.strftime("%b"),
        "MonthNumber": full_dates.month,
        "YearMonth": full_dates.strftime("%Y-%m"),
        "DayOfMonth": full_dates.day,
        "DayOfWeek": full_dates.strftime("%A"),
        "DayOfWeekShort": full_dates.strftime("%a"),
        "DayOfWeekNumber": full_dates.dayofweek + 1, # 1=Mon, 7=Sun
        "IsWeekend": [1 if d.dayofweek >= 5 else 0 for d in full_dates]
    })

    # 6. Buckets & Funnel Attributes
    def duration_bucket(sec):
        if sec < 60: return "< 1 Min (Immediate Drop)"
        if sec < 180: return "1 - 3 Min (Short Pitch)"
        if sec < 300: return "3 - 5 Min (Deliberation)"
        if sec < 600: return "5 - 10 Min (Deep Discussion)"
        return "> 10 Min (Extended Negotiation)"
    df["DurationBracket"] = df["duration"].apply(duration_bucket)

    def touches_bucket(c):
        if c == 1: return "1 Touch"
        if c == 2: return "2 Touches"
        if c == 3: return "3 Touches"
        if c <= 5: return "4-5 Touches"
        if c <= 10: return "6-10 Touches"
        return "11+ Touches"
    df["TouchesBracket"] = df["campaign"].apply(touches_bucket)

    df["IsConverted"] = (df["y"] == "yes").astype(int)
    df["Stage1_Targeted"] = 1
    df["Stage2_Connected"] = (df["duration"] >= 60).astype(int)
    df["Stage3_Engaged"] = ((df["duration"] >= 180) | (df["y"] == "yes")).astype(int)
    df["Stage4_Opportunity"] = ((df["duration"] >= 300) | (df["y"] == "yes")).astype(int)
    df["Stage5_Customer"] = (df["y"] == "yes").astype(int)

    def drop_stage(row):
        if row["Stage5_Customer"] == 1: return "5. Converted Customer"
        if row["Stage4_Opportunity"] == 1: return "4. Dropped at Final Close"
        if row["Stage3_Engaged"] == 1: return "3. Dropped at Deliberation"
        if row["Stage2_Connected"] == 1: return "2. Dropped at Pitch"
        return "1. Dropped at Connect"
    df["FunnelDropStage"] = df.apply(drop_stage, axis=1)

    # 7. Fact_Marketing_Campaign
    fact_cols = [
        "LeadID", "DateKey", "CallDate", "DemographicKey", "ChannelKey",
        "duration", "campaign", "pdays", "previous", "PriorOutcome",
        "emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed",
        "DurationBracket", "TouchesBracket", "IsConverted",
        "Stage1_Targeted", "Stage2_Connected", "Stage3_Engaged", "Stage4_Opportunity", "Stage5_Customer",
        "FunnelDropStage"
    ]
    fact_df = df[fact_cols].copy()
    fact_df.rename(columns={
        "duration": "CallDuration_Seconds",
        "campaign": "TouchesCount",
        "pdays": "DaysSincePriorContact",
        "previous": "PriorContactsCount",
        "emp.var.rate": "EmploymentVariationRate",
        "cons.price.idx": "ConsumerPriceIndex",
        "cons.conf.idx": "ConsumerConfidenceIndex",
        "euribor3m": "Euribor3M",
        "nr.employed": "NumberEmployed"
    }, inplace=True)
    fact_df["CallDuration_Minutes"] = np.round(fact_df["CallDuration_Seconds"] / 60.0, 2)

    # 8. Dim_Funnel_Stages
    dim_stages = pd.DataFrame([
        {"StageID": 1, "StageOrder": 1, "StageName": "1. Outreach / Targeted", "StageShort": "Targeted", "FunnelTier": "Top of Funnel (TOFU)", "StageDescription": "All prospective leads targeted in the campaign"},
        {"StageID": 2, "StageOrder": 2, "StageName": "2. Connected Leads", "StageShort": "Connected", "FunnelTier": "Top of Funnel (TOFU)", "StageDescription": "Prospects connected and passed initial greeting (duration >= 60s)"},
        {"StageID": 3, "StageOrder": 3, "StageName": "3. Engaged Pitch", "StageShort": "Engaged", "FunnelTier": "Middle of Funnel (MOFU)", "StageDescription": "Prospects who listened to the full value proposition (duration >= 180s or converted)"},
        {"StageID": 4, "StageOrder": 4, "StageName": "4. Qualified Opportunity", "StageShort": "Opportunity", "FunnelTier": "Bottom of Funnel (BOFU)", "StageDescription": "High-intent prospects in deep deliberation (duration >= 300s or converted)"},
        {"StageID": 5, "StageOrder": 5, "StageName": "5. Converted Customer", "StageShort": "Customer", "FunnelTier": "Won Customer", "StageDescription": "Prospects who accepted the offer and subscribed to the term deposit"}
    ])

    # 9. Fact_Funnel_Events (Unpivoted table for native Funnel visual and slicing)
    stage_events = []
    for s_id, col, s_name in [
        (1, "Stage1_Targeted", "1. Outreach / Targeted"),
        (2, "Stage2_Connected", "2. Connected Leads"),
        (3, "Stage3_Engaged", "3. Engaged Pitch"),
        (4, "Stage4_Opportunity", "4. Qualified Opportunity"),
        (5, "Stage5_Customer", "5. Converted Customer")
    ]:
        sub = df[df[col] == 1][["LeadID", "DateKey", "DemographicKey", "ChannelKey"]].copy()
        sub["StageID"] = s_id
        sub["StageName"] = s_name
        sub["StageReachedFlag"] = 1
        stage_events.append(sub)
    fact_funnel_events = pd.concat(stage_events, ignore_index=True)

    # Save all files to CSV
    fact_df.to_csv(os.path.join(out_dir, "Fact_Marketing_Campaign.csv"), index=False)
    dim_demo.to_csv(os.path.join(out_dir, "Dim_Demographics.csv"), index=False)
    dim_channel.to_csv(os.path.join(out_dir, "Dim_Channel.csv"), index=False)
    dim_date.to_csv(os.path.join(out_dir, "Dim_Date.csv"), index=False)
    dim_stages.to_csv(os.path.join(out_dir, "Dim_Funnel_Stages.csv"), index=False)
    fact_funnel_events.to_csv(os.path.join(out_dir, "Fact_Funnel_Events.csv"), index=False)

    print("Successfully generated all Star Schema CSV files in:", out_dir)
    print("Files created:")
    for f in os.listdir(out_dir):
        sz = os.path.getsize(os.path.join(out_dir, f)) / 1024
        print(f" - {f} ({sz:,.1f} KB)")

if __name__ == "__main__":
    run_etl()
