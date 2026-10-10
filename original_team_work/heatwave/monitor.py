import os
import pandas as pd

def analyze_heat_conditions(df, temp_col='T2M_MAX', threshold=40.0):
    """
    Analyzes temperature data to determine heatwave status and generate an engineering decision.
    """
    if df.empty:
        return {"Error": "Dataset is empty."}
        
    # Ensure sequential data is ordered if Date exists, as consecutive days rely on chronology
    if 'DATE' in df.columns:
        df = df.sort_values(by='DATE').reset_index(drop=True)
    elif 'Date' in df.columns:
        df = df.sort_values(by='Date').reset_index(drop=True)
    
    # 1. Identify High-Temperature Days based on the threshold
    df['Is_High_Temp'] = df[temp_col] >= threshold
    
    # 2. Calculate Frequency and Percentage
    total_days = len(df)
    high_temp_days = int(df['Is_High_Temp'].sum())
    percent_high_temp = (high_temp_days / total_days) * 100
    
    # 3. Calculate consecutive high-temperature days (heatwave streaks)
    df['Streak_Group'] = (~df['Is_High_Temp']).cumsum()
    df['Consecutive_Days'] = df.groupby('Streak_Group')['Is_High_Temp'].cumsum()
    max_consecutive_days = int(df['Consecutive_Days'].max())
    
    max_temp = df[temp_col].max()
    
    # 4. Generate Heat Monitoring Status & Engineering Decision
    if max_consecutive_days >= 3:
        status = "CRITICAL: Severe Heatwave Detected"
        decision = (
            "1. Halt non-essential outdoor construction and engineering field work between 12 PM - 4 PM.\n"
            "2. Alert power grid operators to prep for load surges from HVAC systems to prevent blackouts.\n"
            "3. Monitor structural thermal expansion on critical infrastructure (e.g., railway tracks, steel bridges)."
        )
    elif percent_high_temp >= 15.0 or high_temp_days > 0:
        status = "ALERT: High Heat Frequency"
        decision = (
            "1. Enforce mandatory shaded rest breaks and hydration stations for field engineers and workers.\n"
            "2. Ensure backup cooling systems for sensitive data centers and equipment are functional."
        )
    else:
        status = "NORMAL: Temperature within operational limits"
        decision = (
            "1. Continue standard engineering and construction operations.\n"
            "2. Maintain routine daily weather logging."
        )
        
    # 5. Compile the final output for the Dashboard (Person 7)
    results = {
        "Total Days Analyzed": total_days,
        "Threshold Set (°C)": threshold,
        "Max Temp Recorded (°C)": round(max_temp, 2),
        "High-Temp Days": high_temp_days,
        "Percentage (%)": round(percent_high_temp, 2),
        "Max Consecutive Days": max_consecutive_days,
        "Monitoring Status": status,
        "Engineering Decision": decision
    }
    
    return results


if __name__ == "__main__":
    # Find the cleaned data CSV based on the folder structure
    file_path = 'cleaned_daily_data.csv'
    if not os.path.exists(file_path):
        file_path = '../cleaned_daily_data.csv'
    if not os.path.exists(file_path):
        file_path = '../data/cleaned_daily_data.csv'
    if not os.path.exists(file_path):
        file_path = 'data/cleaned_daily_data.csv'

    try:
        df = pd.read_csv(file_path)
        print(f"Loading dataset from: {file_path}")
        
        # Target temperature column: checks for T2M_MAX, otherwise uses the 2nd column
        target_col = 'T2M_MAX' if 'T2M_MAX' in df.columns else df.columns[1]
        
        print("\n=======================================================")
        print(" PERSON 6: HEATWAVE MONITORING & ENGINEERING DECISIONS")
        print("=======================================================")
        
        # Run the analysis
        results = analyze_heat_conditions(df, temp_col=target_col, threshold=40.0)
        
        # Print formatted results
        for key, value in results.items():
            if key in ["Monitoring Status", "Engineering Decision"]:
                print(f"\n--- {key.upper()} ---")
                print(value)
            else:
                print(f"{key}: {value}")
                
        print("\n=======================================================\n")
        
    except FileNotFoundError:
        print(f"Error: Could not find cleaned CSV file. Please make sure Person 1 has generated it in the data/ folder.")
