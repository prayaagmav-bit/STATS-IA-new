import os
import pandas as pd
from scipy import stats

def calculate_central_tendency():
    # Define file path for cleaned daily temperature data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, '..', 'cleaned_daily_data.csv'),
        os.path.join(base_dir, 'cleaned_daily_data.csv'),
        'cleaned_daily_data.csv',
        os.path.join('main', 'cleaned_daily_data.csv'),
        '../cleaned_daily_data.csv',
        'statistics/cleaned_daily_data.csv',
    ]
    file_path = next((p for p in candidates if os.path.exists(p)), 'cleaned_daily_data.csv')
        
    print(f"Loading dataset from: {file_path}")
    df = pd.read_csv(file_path)
    
    # Target temperature column (e.g., T2M_MAX or T2M)
    target_col = 'T2M_MAX' if 'T2M_MAX' in df.columns else df.columns[1]
    data = df[target_col].dropna()
    
    # Calculate Central Tendency
    mean_val = data.mean()
    median_val = data.median()
    mode_result = stats.mode(data, keepdims=True)
    mode_val = mode_result.mode[0]
    
    print("\n==========================================")
    print(" PERSON 2: DESCRIPTIVE STATISTICS MODULE")
    print("==========================================")
    print(f"Target Feature: {target_col}")
    print(f"Mean Temperature:   {mean_val:.2f} °C")
    print(f"Median Temperature: {median_val:.2f} °C")
    print(f"Mode Temperature:   {mode_val:.2f} °C")
    print("==========================================")
    
    # Save frequency distribution table
    freq_table = data.value_counts().reset_index()
    freq_table.columns = ['Temperature', 'Frequency']
    freq_output = os.path.join(base_dir, 'frequency_table.csv')
    freq_table.to_csv(freq_output, index=False)
    print("Frequency distribution table saved successfully.")

if __name__ == '__main__':
    calculate_central_tendency()