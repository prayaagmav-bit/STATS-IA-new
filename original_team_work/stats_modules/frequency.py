import os
import pandas as pd

EDGES = [26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46]   # 2 degree wide boxes


def frequency_table(df, col="T2M_MAX", edges=EDGES):
    """Take the data, return the frequency table (a DataFrame)."""
    temps = df[col]
    total = len(temps)
    rows = []
    running_total = 0

    for i in range(len(edges) - 1):
        low = edges[i]
        high = edges[i + 1]

        count = int(((temps >= low) & (temps < high)).sum())
        running_total = running_total + count

        rows.append({
            "Class Interval (°C)": f"{low}-{high}",
            "Frequency": count,
            "Relative Frequency": round(count / total, 4),
            "Percentage (%)": round(count / total * 100, 2),
            "Cumulative Frequency": running_total,
            "Cumulative %": round(running_total / total * 100, 2),
        })

    return pd.DataFrame(rows)



if __name__ == "__main__":
    folder = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(folder, "..", "cleaned_daily_data.csv"))

    table = frequency_table(df)
    print(table.to_string(index=False))
    table.to_csv(os.path.join(folder, "..", "frequency_table.csv"), index=False)