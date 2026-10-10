import pandas as pd
import numpy as np

def calculate_dispersion(df: pd.DataFrame, column_name: str = 'T2M_MAX') -> dict:
    """
    Calculates measures of dispersion for a given temperature column.
    
    Args:
        df (pd.DataFrame): The temperature dataset.
        column_name (str): The column name to calculate dispersion for (default: 'T2M_MAX').
        
    Returns:
        dict: A dictionary containing Range, Variance, Standard Deviation, and Coefficient of Variation.
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in the dataset.")
        
    # Extract the data, dropping any missing values just in case
    data = df[column_name].dropna()
    
    # Calculate Range
    data_min = data.min()
    data_max = data.max()
    data_range = data_max - data_min
    
    # Calculate Variance (Sample Variance, ddof=1)
    variance = data.var(ddof=1)
    
    # Calculate Standard Deviation (Sample Standard Deviation, ddof=1)
    std_dev = data.std(ddof=1)
    
    # Calculate Mean to compute the Coefficient of Variation
    mean_val = data.mean()
    
    # Calculate Coefficient of Variation (as a percentage)
    cv = (std_dev / mean_val) * 100 if mean_val != 0 else 0
    
    return {
        "Range": data_range,
        "Variance": variance,
        "Standard Deviation": std_dev,
        "Coefficient of Variation (%)": cv,
        "Min": data_min,
        "Max": data_max,
        "Mean": mean_val
    }

def print_dispersion_summary(dispersion_results: dict):
    """
    Helper function to print the dispersion results nicely (Useful for Person 5's manual check).
    """
    print("--- Measures of Dispersion ---")
    print(f"Minimum Temperature: {dispersion_results['Min']:.2f} °C")
    print(f"Maximum Temperature: {dispersion_results['Max']:.2f} °C")
    print(f"Mean Temperature:    {dispersion_results['Mean']:.2f} °C")
    print("-" * 30)
    print(f"Range:               {dispersion_results['Range']:.2f} °C")
    print(f"Variance:            {dispersion_results['Variance']:.2f} (°C)²")
    print(f"Standard Deviation:  {dispersion_results['Standard Deviation']:.2f} °C")
    print(f"Coeff. of Variation: {dispersion_results['Coefficient of Variation (%)']:.2f} %")
    print("-" * 30)

# If this file is run directly (for Person 5 to test their code independently)
if __name__ == "__main__":
    try:
        # Assuming the CSV is accessible from this path when run from the root directory
        df_sample = pd.read_csv("Graphs/cleaned_daily_data.csv")
        
        # Test the function on the Maximum Temperature column
        results = calculate_dispersion(df_sample, 'T2M_MAX')
        print_dispersion_summary(results)
    except FileNotFoundError:
        print("Dataset not found. Please ensure 'cleaned_daily_data.csv' is in the 'Graphs' directory.")
