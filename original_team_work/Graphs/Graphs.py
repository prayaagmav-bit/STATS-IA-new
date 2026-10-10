import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def generate_graphs(cleaned_data_path="cleaned_daily_data.csv", freq_data_path="frequency_table.csv", cleaned_df=None, freq_df=None, threshold=40.0):
    if cleaned_df is None:
        cleaned_df = pd.read_csv(cleaned_data_path)
    if freq_df is None:
        freq_df = pd.read_csv(freq_data_path)

    if not pd.api.types.is_datetime64_any_dtype(cleaned_df["DATE"]):
        cleaned_df["DATE"] = pd.to_datetime(cleaned_df["DATE"])

    bins = list(range(26, 48, 2))
    class_labels = freq_df["Class Interval (°C)"].tolist()
    frequencies = freq_df["Frequency"].tolist()

    midpoints = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]

    fig = make_subplots(
        rows=3, cols=2, 
        subplot_titles=(
            "1. Daily Maximum Temperature Trend", 
            "2. Temperature Distribution Histogram",
            "3. Frequency Bar Graph across Class Intervals", 
            "4. Frequency Polygon (Class Midpoints)",
            "5. Temperature Dispersion & Outliers (Box Plot)"
        ),
        vertical_spacing=0.1,
        horizontal_spacing=0.05
    )

    # 1. Line Chart
    fig.add_trace(go.Scatter(
        x=cleaned_df["DATE"], y=cleaned_df["T2M_MAX"], 
        mode="lines", line=dict(color="crimson", width=1.5),
        name="Max Temp",
        hovertemplate="Date: %{x}<br>Temp: %{y} °C<extra></extra>"
    ), row=1, col=1)
    
    fig.add_hline(y=threshold, line_dash="dash", line_color="black", 
                  annotation_text=f"Threshold ({threshold}°C)", 
                  row=1, col=1)

    # 2. Histogram (Use Bar chart since we have bins or use go.Histogram)
    fig.add_trace(go.Histogram(
        x=cleaned_df["T2M_MAX"], 
        xbins=dict(start=26, end=48, size=2),
        marker_color="orange",
        marker_line_color="black",
        marker_line_width=1,
        name="Frequency",
        hovertemplate="Temp: %{x} °C<br>Days: %{y}<extra></extra>"
    ), row=1, col=2)

    # 3. Bar Graph
    fig.add_trace(go.Bar(
        x=class_labels, y=frequencies,
        marker_color="skyblue",
        marker_line_color="black",
        marker_line_width=1,
        name="Class Freq",
        hovertemplate="Interval: %{x}<br>Days: %{y}<extra></extra>"
    ), row=2, col=1)

    # 4. Polygon
    midpoints_poly = [25] + midpoints + [47]
    counts_poly = [0] + frequencies + [0]
    fig.add_trace(go.Scatter(
        x=midpoints_poly, y=counts_poly,
        mode="lines+markers",
        line=dict(color="purple", width=2),
        marker=dict(symbol="square"),
        fill="tozeroy",
        fillcolor="rgba(128, 0, 128, 0.15)",
        name="Polygon",
        hovertemplate="Midpoint: %{x} °C<br>Freq: %{y}<extra></extra>"
    ), row=2, col=2)

    # 5. Box plot
    fig.add_trace(go.Box(
        x=cleaned_df["T2M_MAX"],
        marker_color="salmon",
        name="Temp Dispersion",
        hovertemplate="Temp: %{x} °C<extra></extra>"
    ), row=3, col=1)

    fig.update_layout(
        height=1000, 
        title_text="Heatwave Monitoring System",
        showlegend=False,
    )

    # Update axes titles
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    
    fig.update_xaxes(title_text="Temperature Interval (°C)", row=1, col=2)
    fig.update_yaxes(title_text="Frequency (Days)", row=1, col=2)
    
    fig.update_xaxes(title_text="Class Interval (°C)", row=2, col=1)
    fig.update_yaxes(title_text="Number of Days", row=2, col=1)
    
    fig.update_xaxes(title_text="Midpoint Temperature (°C)", row=2, col=2)
    fig.update_yaxes(title_text="Frequency", row=2, col=2)
    
    fig.update_xaxes(title_text="Daily Max Temperature (°C)", row=3, col=1)

    return fig