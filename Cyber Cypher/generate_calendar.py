import pandas as pd
from datetime import datetime, timedelta

def generate_master_sheet():
    # --- 1. DEFINE THE EVENTS ---
    festivals = {
        "2026-01-26": "Republic Day", "2026-03-25": "Holi",
        "2026-08-15": "Independence Day", "2026-10-02": "Gandhi Jayanti",
        "2026-10-20": "Dussehra", "2026-11-01": "Diwali",
        "2026-12-25": "Christmas"
    }
    
    sales = [
        ("2026-01-20", 6, "Republic Day Sale"),
        ("2026-08-08", 7, "Freedom Sale"),
        ("2026-10-05", 25, "Great Indian Festival") 
    ]

    data = []
    start_date = datetime(2026, 1, 1)

    # --- 2. LOOP THROUGH 365 DAYS ---
    for i in range(365):
        curr = start_date + timedelta(days=i)
        curr_str = curr.strftime("%Y-%m-%d")
        day_val = curr.day
        weekday = curr.weekday()
        
        # Defaults (Normal Day)
        context = "Normal_Day"
        fail_limit = 0.05   # 5%
        latency_limit = 800 # 800ms
        peak_start = 18     # 6 PM
        peak_end = 22       # 10 PM

        # PRIORITY 1: Salary Week (1st-7th)
        if 1 <= day_val <= 7:
            context = "Salary_Week"
            fail_limit = 0.12
            latency_limit = 1200
            peak_start, peak_end = 10, 14

        # PRIORITY 2: Month End (25th+)
        elif day_val >= 25:
            context = "Month_End"
            fail_limit = 0.08
            latency_limit = 1000
            peak_start, peak_end = 19, 23

        # PRIORITY 3: Weekends (Fri-Sun) - Overrides Normal, but not Salary
        if weekday >= 4 and "Salary" not in context:
            context = "Weekend_Rush"
            fail_limit = 0.10
            latency_limit = 950
            peak_start, peak_end = 17, 23

        # PRIORITY 4: Sales (Overrides all previous)
        for s_start, duration, name in sales:
            s_date = datetime.strptime(s_start, "%Y-%m-%d")
            if s_date <= curr <= s_date + timedelta(days=duration):
                context = f"SALE_{name.replace(' ', '_')}"
                fail_limit = 0.18
                latency_limit = 1800
                peak_start, peak_end = 12, 23
                break

        # PRIORITY 5: Pre-Festival (5 Days Before) - Critical
        for f_date_str in festivals:
            f_date = datetime.strptime(f_date_str, "%Y-%m-%d")
            delta = (f_date - curr).days
            if 0 < delta <= 5 and "SALE" not in context:
                context = "Pre_Festival_Rush"
                fail_limit = 0.15
                latency_limit = 1500
                peak_start, peak_end = 18, 23

        # PRIORITY 6: Festival Day (Highest Priority)
        if curr_str in festivals:
            context = f"FESTIVAL_{festivals[curr_str]}"
            fail_limit = 0.25
            latency_limit = 2500
            peak_start, peak_end = 9, 23

        data.append({
            "Date": curr_str,
            "Context": context,
            "Max_Failure_Rate": fail_limit,
            "Max_Latency": latency_limit,
            "Peak_Start": peak_start,
            "Peak_End": peak_end
        })

    # Save File
    df = pd.DataFrame(data)
    df.to_csv("indian_payment_calendar.csv", index=False)
    print("✅ Spreadsheet generated: indian_payment_calendar.csv")

if __name__ == "__main__":
    generate_master_sheet()