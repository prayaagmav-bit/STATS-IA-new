import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def generate_graphs(
    cleaned_data_path="cleaned_daily_data.csv",
    freq_data_path="frequency_table.csv",
    cleaned_df=None,
    freq_df=None,
    threshold=40.0,
):
  base_dir = os.path.dirname(os.path.abspath(__file__))
  if cleaned_df is None:
    if cleaned_data_path and os.path.exists(cleaned_data_path):
      cleaned_df = pd.read_csv(cleaned_data_path)
    else:
      candidates = [
          cleaned_data_path if cleaned_data_path else "",
          os.path.join(base_dir, "..", "cleaned_daily_data.csv"),
          os.path.join(base_dir, "cleaned_daily_data.csv"),
          "cleaned_daily_data.csv",
          os.path.join("main", "cleaned_daily_data.csv"),
          os.path.join("main", "Graphs", "cleaned_daily_data.csv"),
      ]
      path = next(
          (p for p in candidates if p and os.path.exists(p)),
          "cleaned_daily_data.csv",
      )
      cleaned_df = pd.read_csv(path)

  if freq_df is None:
    if freq_data_path and os.path.exists(freq_data_path):
      freq_df = pd.read_csv(freq_data_path)
    else:
      candidates = [
          os.path.join(base_dir, "..", "frequency_table.csv"),
          os.path.join(base_dir, "frequency_table.csv"),
          os.path.join("main", "frequency_table.csv"),
          os.path.join("main", "Graphs", "frequency_table.csv"),
          "frequency_table.csv",
      ]
      path = next(
          (p for p in candidates if p and os.path.exists(p)),
          "frequency_table.csv",
      )
      freq_df = pd.read_csv(path)

  if not pd.api.types.is_datetime64_any_dtype(cleaned_df["DATE"]):
    cleaned_df["DATE"] = pd.to_datetime(cleaned_df["DATE"])

  bins = list(range(26, 48, 2))
  frequencies = freq_df["Frequency"].tolist()
  midpoints = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]

  # Clean 2x2 grid layout (4 subplots total)
  fig = make_subplots(
      rows=2,
      cols=2,
      subplot_titles=(
          "1. Daily Maximum Temperature Trend",
          "2. Temperature Distribution Histogram",
          "3. Frequency Polygon (Class Midpoints)",
          "4. Temperature Dispersion & Outliers (Box Plot)",
      ),
      vertical_spacing=0.12,
      horizontal_spacing=0.08,
  )

  # 1. Line Chart (Row 1, Col 1)
  fig.add_trace(
      go.Scatter(
          x=cleaned_df["DATE"],
          y=cleaned_df["T2M_MAX"],
          mode="lines",
          line=dict(color="crimson", width=1.5),
          name="Max Temp",
          hovertemplate="Date: %{x}<br>Temp: %{y} °C<extra></extra>",
      ),
      row=1,
      col=1,
  )

  fig.add_hline(
      y=threshold,
      line_dash="dash",
      line_color="black",
      annotation_text=f"Threshold ({threshold}°C)",
      row=1,
      col=1,
  )

  # 2. Histogram (Row 1, Col 2)
  fig.add_trace(
      go.Histogram(
          x=cleaned_df["T2M_MAX"],
          xbins=dict(start=26, end=48, size=2),
          marker_color="orange",
          marker_line_color="black",
          marker_line_width=1,
          name="Frequency",
          hovertemplate="Temp: %{x} °C<br>Days: %{y}<extra></extra>",
      ),
      row=1,
      col=2,
  )

  # 3. Polygon (Row 2, Col 1)
  midpoints_poly = [25] + midpoints + [47]
  counts_poly = [0] + frequencies + [0]
  fig.add_trace(
      go.Scatter(
          x=midpoints_poly,
          y=counts_poly,
          mode="lines+markers",
          line=dict(color="purple", width=2),
          marker=dict(symbol="square"),
          fill="tozeroy",
          fillcolor="rgba(128, 0, 128, 0.15)",
          name="Polygon",
          hovertemplate="Midpoint: %{x} °C<br>Freq: %{y}<extra></extra>",
      ),
      row=2,
      col=1,
  )

  # 4. Box plot (Row 2, Col 2)
  fig.add_trace(
      go.Box(
          x=cleaned_df["T2M_MAX"],
          marker_color="salmon",
          name="Temp Dispersion",
          hovertemplate="Temp: %{x} °C<extra></extra>",
      ),
      row=2,
      col=2,
  )

  fig.update_layout(
      height=750,
      title_text="Heatwave Monitoring System",
      showlegend=False,
  )

  # Update axis titles
  fig.update_xaxes(title_text="Date", row=1, col=1)
  fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)

  fig.update_xaxes(title_text="Temperature Interval (°C)", row=1, col=2)
  fig.update_yaxes(title_text="Frequency (Days)", row=1, col=2)

  fig.update_xaxes(title_text="Midpoint Temperature (°C)", row=2, col=1)
  fig.update_yaxes(title_text="Frequency", row=2, col=1)

  fig.update_xaxes(title_text="Daily Max Temperature (°C)", row=2, col=2)

  return fig