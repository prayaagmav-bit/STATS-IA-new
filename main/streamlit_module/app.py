"""Heatwave Analytics Dashboard
"""
import os
import sys
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from stats_modules.frequency import frequency_table
from stats_modules.dispersion import calculate_dispersion
from heatwave.monitor import analyze_heat_conditions
from Graphs.Graphs import generate_graphs

st.set_page_config(page_title="Heatwave Dashboard", page_icon="🌡️", layout="wide")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

@st.cache_data
def load():
    df = pd.read_csv(os.path.join(ROOT, "cleaned_daily_data.csv"))
    df["DATE"] = pd.to_datetime(df["DATE"])
    df["Y"] = df["DATE"].dt.year
    df["M"] = df["DATE"].dt.strftime("%b")
    df["D"] = df["DATE"].dt.day
    df["MONTH"] = df["DATE"].dt.strftime("%b %Y")
    return df

def make_scale(threshold):
    """Cool colours below the threshold, warm colours from the threshold up."""
    p = min(max((threshold - 26) / 19, 0.05), 0.97)
    return [[0, "#2f6f8f"], [p * 0.5, "#8cc4a8"], [p * 0.99, "#f2d27a"],
            [p, "#ee9a4a"], [(p + 1) / 2, "#d9482b"], [1, "#7a1424"]]

def central_tendency(s):
    return s.mean(), s.median(), s.round(0).mode()[0]

def days_from_event(event, df, years):
    try:
        points = event["selection"]["points"]
    except (KeyError, TypeError):
        return []
    keys = set()
    for p in points:
        try:
            keys.add((years[p["curve_number"]], p["y"], int(p["x"])))
        except (KeyError, IndexError, TypeError, ValueError):
            continue
    return [i for i, k in enumerate(zip(df["Y"], df["M"], df["D"])) if k in keys]

df = load()
min_date = df["DATE"].min().date()
max_date = df["DATE"].max().date()
years = sorted(df["Y"].unique())

st.title("🌡️ Heatwave Analytics Dashboard")

# Top Level Controls
col1, col2 = st.columns(2)
with col1:
    selected_dates = st.date_input(
        "📅 Select Timeline:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
with col2:
    threshold = st.slider("🔥 Heatwave Threshold (°C)", 35.0, 45.0, 40.0, 0.5)

# Setup Data View based on timeline
if len(selected_dates) == 2:
    start_date, end_date = selected_dates
    view = df[(df["DATE"].dt.date >= start_date) & (df["DATE"].dt.date <= end_date)].copy()
elif len(selected_dates) == 1:
    start_date = end_date = selected_dates[0]
    view = df[(df["DATE"].dt.date == start_date)].copy()
else:
    view = df.copy()

st.markdown("---")

tab_home, tab_calendar = st.tabs(["🏠 Main Dashboard", "🗓️ Warming Calendar"])

# ==========================================
# TAB 1: MAIN DASHBOARD
# ==========================================
with tab_home:
    if view.empty:
        st.warning("No data for this date range.")
    else:
        st.subheader("Statistical Overview & Engineering Decision")
        
        # Calculate stats
        temps = view["T2M_MAX"]
        mean, median, mode = central_tendency(temps)
        
        if len(view) > 1:
            d = calculate_dispersion(view, "T2M_MAX")
            std_dev = f"{d['Standard Deviation']:.2f} °C"
            cv = f"{d['Coefficient of Variation (%)']:.1f}%"
        else:
            std_dev = "N/A"
            cv = "N/A"

        res = analyze_heat_conditions(view.copy(), temp_col="T2M_MAX", threshold=threshold)

        # Status Box
        status = res.get("Monitoring Status", "NORMAL")
        box = st.error if "CRITICAL" in status else st.warning if "ALERT" in status else st.success
        box(f"**Status:** {status}")

        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("**Centre**")
            st.metric("Mean", f"{mean:.2f} °C")
            st.write(f"Median: {median:.2f} °C")
        with c2:
            st.markdown("**Spread**")
            st.metric("Std Dev", std_dev)
            st.write(f"CV: {cv}")
        with c3:
            st.markdown("**Frequency**")
            st.metric(f"Days ≥ {threshold} °C", f"{res.get('High-Temp Days', 0)}")
            st.write(f"Share: {res.get('Percentage (%)', 0)}%")
        with c4:
            st.markdown("**Extremes**")
            st.metric("Max Streak", f"{res.get('Max Consecutive Days', 0)} days")
            st.write(f"Hottest: {res.get('Max Temp Recorded (°C)', 0)} °C")

        st.markdown("**Engineering Decision:**")
        st.info(res.get("Engineering Decision", ""))

        st.markdown("---")
        st.subheader("📈 Graphical Analysis")
        st.caption("These graphs reflect the data within your selected timeline.")
        
        anim_col, blank = st.columns([1, 3])
        animate_btn = anim_col.button("▶️ Play Animation (Month by Month)", help="Animate the graphs over time")

        graph_placeholder = st.empty()

        if animate_btn:
            import time
            df["YearMonth_sort"] = df["DATE"].dt.year * 100 + df["DATE"].dt.month
            unique_ym = sorted(df["YearMonth_sort"].unique())
            
            for ym in unique_ym:
                anim_view = df[df["YearMonth_sort"] <= ym].copy()
                current_date_str = anim_view["DATE"].max().strftime("%B %Y")
                
                with graph_placeholder.container():
                    st.markdown(f"#### 📅 Data up to: **{current_date_str}**")
                    anim_freq_df = frequency_table(anim_view)
                    fig_graphs = generate_graphs(cleaned_df=anim_view, freq_df=anim_freq_df, threshold=threshold)
                    st.plotly_chart(fig_graphs, use_container_width=True)
                
                # Small pause between frames
                time.sleep(0.1)
                
        else:
            # Static view based on the timeline picker
            with graph_placeholder.container():
                freq_df = frequency_table(view)
                fig_graphs = generate_graphs(cleaned_df=view, freq_df=freq_df, threshold=threshold)
                st.plotly_chart(fig_graphs, use_container_width=True)


# ==========================================
# TAB 2: WARMING CALENDAR
# ==========================================
with tab_calendar:
    st.subheader("🗓️ Monthly Warming Calendar")
    st.caption("Select a specific month and year below to view its daily temperature grid. Drag a box over any days to get a free-form group summary.")
    
    cal_col1, cal_col2 = st.columns(2)
    selected_year = cal_col1.selectbox("Select Year", years)
    selected_month = cal_col2.selectbox("Select Month", MONTHS)
    
    # Filter for the selected month/year
    cal_mask = (df["Y"] == selected_year) & (df["M"] == selected_month)
    sub = df[cal_mask]
    
    if not sub.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sub["D"], y=sub["M"], mode="markers", showlegend=False,
            marker=dict(symbol="square", size=25, color=sub["T2M_MAX"], coloraxis="coloraxis"),
            customdata=np.stack([sub["DATE"].dt.strftime("%d %b %Y"), sub["T2M_MAX"].round(1)], axis=-1),
            hovertemplate="%{customdata[0]}<br>%{customdata[1]} °C<extra></extra>",
            unselected=dict(marker=dict(opacity=0.25)),
        ))
            
        fig.update_layout(height=250, dragmode="select", margin=dict(l=5, r=5, t=28, b=5),
                          coloraxis=dict(colorscale=make_scale(threshold), cmin=26, cmax=45,
                                         colorbar=dict(title="°C", thickness=10, len=0.9)),
                          title=f"Warming Grid for {selected_month} {selected_year}")
        fig.update_xaxes(range=[0.3, 31.7], tickvals=list(range(1, 32)), showgrid=False, title="Day of Month")
        fig.update_yaxes(type="category", categoryorder="array", categoryarray=MONTHS,
                         autorange="reversed", showgrid=False)
                         
        event = st.plotly_chart(fig, key="calendar", on_select="rerun",
                                selection_mode=("box", "lasso", "points"))
    
        # Summarize dragged days on the calendar
        drag = days_from_event(event, df, years)
        if drag and len(drag) >= 2:
            st.markdown("---")
            st.subheader("Selection Summary")
            drag_view = df.iloc[drag]
            drag_mean, drag_median, drag_mode = central_tendency(drag_view["T2M_MAX"])
            drag_d = calculate_dispersion(drag_view, "T2M_MAX")
            drag_r = analyze_heat_conditions(drag_view.copy(), temp_col="T2M_MAX", threshold=threshold)
            
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Selected Days", f"{len(drag_view)}")
            s2.metric("Mean Temp", f"{drag_mean:.2f} °C")
            s3.metric("Std Dev", f"{drag_d['Standard Deviation']:.2f} °C")
            s4.metric(f"Days ≥ {threshold} °C", f"{drag_r.get('High-Temp Days', 0)}")
    else:
        st.info("No data available for the selected month and year.")
