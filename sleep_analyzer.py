import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta

# Configure the page
st.set_page_config(
    page_title="Sleep Schedule Analyzer",
    page_icon="🌙",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1E90FF;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #4169E1;
        border-bottom: 2px solid #1E90FF;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .highlight {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E90FF;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .recommendation {
        background-color: #e6f7ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<h1 class="main-header">🌙 Sleep Schedule Analyzer</h1>', unsafe_allow_html=True)
st.markdown("""
    <div class="highlight">
    <p>Track and analyze your sleep patterns to improve your sleep health. 
    Research shows that consistent, quality sleep reduces the risk of chronic diseases and improves overall wellbeing.</p>
    </div>
""", unsafe_allow_html=True)

# Introduction and information
with st.expander("ℹ️ About Sleep Health"):
    st.markdown("""
    ### Why Sleep Regularity Matters
    
    Numerous studies have shown that irregular sleep patterns are linked to significant health risks:
    - Regular sleep decreases the chance of death by up to 48%
    - Lower likelihood of heart disease and cancer
    - Reduced risk of Type 2 diabetes, Parkinson's disease, kidney failure, and liver cirrhosis
    
    This tool helps you track and improve your sleep regularity and duration.
    """)

# Initialize session state for storing sleep data
if 'sleep_data' not in st.session_state:
    st.session_state.sleep_data = pd.DataFrame(columns=['Date', 'Bedtime', 'WakeTime', 'SleepDuration'])

# Function to calculate sleep duration
def calculate_sleep_duration(bedtime, waketime):
    # Convert to datetime objects for calculation
    if isinstance(bedtime, time):
        bedtime_dt = datetime.combine(datetime.now().date(), bedtime)
    else:
        bedtime_dt = datetime.combine(datetime.now().date(), time(bedtime.hour, bedtime.minute))
        
    if isinstance(waketime, time):
        waketime_dt = datetime.combine(datetime.now().date(), waketime)
    else:
        waketime_dt = datetime.combine(datetime.now().date(), time(waketime.hour, waketime.minute))
    
    if bedtime_dt > waketime_dt:  # Handle overnight sleep (e.g., 11 PM to 7 AM)
        waketime_dt += timedelta(days=1)
    
    sleep_duration = (waketime_dt - bedtime_dt).total_seconds() / 3600  # Convert to hours
    return sleep_duration

# Function to add new sleep entry
def add_sleep_entry(date, bedtime, waketime):
    sleep_duration = calculate_sleep_duration(bedtime, waketime)
    
    new_entry = pd.DataFrame({
        'Date': [date],
        'Bedtime': [bedtime],
        'WakeTime': [waketime],
        'SleepDuration': [sleep_duration]
    })
    
    st.session_state.sleep_data = pd.concat([st.session_state.sleep_data, new_entry], ignore_index=True)
    st.success("Sleep entry added successfully!")

# Function to analyze sleep patterns
def analyze_sleep_patterns(df):
    if len(df) < 2:
        return {
            'avg_sleep': df['SleepDuration'].mean() if len(df) > 0 else 0,
            'sleep_consistency': 0,
            'recommendations': ["Add more data to get meaningful insights."]
        }
    
    avg_sleep = df['SleepDuration'].mean()
    sleep_std = df['SleepDuration'].std()
    
    # Calculate bedtime consistency (standard deviation of bedtime hours)
    bedtimes = df['Bedtime'].apply(lambda x: x.hour + x.minute/60 if hasattr(x, 'hour') else 0)
    bedtime_std = bedtimes.std()
    
    recommendations = []
    
    # Sleep duration recommendations
    if avg_sleep < 7:
        recommendations.append("Your average sleep duration is below the recommended 7-8 hours. Try to go to bed earlier or wake up later.")
    elif avg_sleep > 9:
        recommendations.append("Your average sleep duration is above the recommended 7-8 hours. While sleep needs vary, excessive sleep can sometimes indicate underlying health issues.")
    else:
        recommendations.append("Your average sleep duration is within the recommended range. Great job!")
    
    # Sleep consistency recommendations
    if bedtime_std > 1.5:
        recommendations.append("Your bedtime varies significantly. Try to go to bed at the same time each night to improve sleep quality.")
    elif bedtime_std > 0.75:
        recommendations.append("Your bedtime is somewhat irregular. Consider establishing a more consistent sleep schedule.")
    else:
        recommendations.append("Your bedtime is consistent, which is excellent for maintaining healthy sleep patterns.")
    
    # Sleep duration consistency
    if sleep_std > 1.5:
        recommendations.append("Your sleep duration varies considerably. Aim for a consistent amount of sleep each night.")
    
    return {
        'avg_sleep': avg_sleep,
        'sleep_consistency': bedtime_std,
        'recommendations': recommendations
    }

# Main app layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<h2 class="sub-header">Add Sleep Entry</h2>', unsafe_allow_html=True)
    
    # Use a form to collect sleep data
    with st.form("sleep_form"):
        date = st.date_input("Date", datetime.now().date())
        bedtime = st.time_input("Bedtime", time(23, 0))
        waketime = st.time_input("Wake Time", time(7, 0))
        
        submitted = st.form_submit_button("Add Entry")
        
        if submitted:
            add_sleep_entry(date, bedtime, waketime)
            st.rerun()  # Refresh to show updated data

    # Display current sleep data
    if not st.session_state.sleep_data.empty:
        st.markdown('<h2 class="sub-header">Your Sleep Data</h2>', unsafe_allow_html=True)
        display_df = st.session_state.sleep_data.copy()
        
        # Convert Date column to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(display_df['Date']):
            display_df['Date'] = pd.to_datetime(display_df['Date'])
            
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        display_df['Bedtime'] = display_df['Bedtime'].apply(lambda x: x.strftime('%H:%M') if hasattr(x, 'strftime') else str(x))
        display_df['WakeTime'] = display_df['WakeTime'].apply(lambda x: x.strftime('%H:%M') if hasattr(x, 'strftime') else str(x))
        display_df['SleepDuration'] = display_df['SleepDuration'].round(2)
        display_df = display_df.rename(columns={
            'Date': 'Date',
            'Bedtime': 'Bedtime',
            'WakeTime': 'Wake Time',
            'SleepDuration': 'Hours Slept'
        })
        st.dataframe(display_df, use_container_width=True)
        
        if st.button("Clear All Data"):
            st.session_state.sleep_data = pd.DataFrame(columns=['Date', 'Bedtime', 'WakeTime', 'SleepDuration'])
            st.rerun()

with col2:
    if not st.session_state.sleep_data.empty:
        # Make sure Date column is datetime for analysis
        analysis_df = st.session_state.sleep_data.copy()
        if not pd.api.types.is_datetime64_any_dtype(analysis_df['Date']):
            analysis_df['Date'] = pd.to_datetime(analysis_df['Date'])
            
        # Analyze sleep patterns
        analysis = analyze_sleep_patterns(analysis_df)
        
        # Display metrics
        st.markdown('<h2 class="sub-header">Sleep Analysis</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Average Sleep Duration", f"{analysis['avg_sleep']:.2f} hours", 
                     delta="Good" if 7 <= analysis['avg_sleep'] <= 9 else "Needs improvement")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Bedtime Consistency", f"{analysis['sleep_consistency']:.2f} hours std", 
                     delta="Consistent" if analysis['sleep_consistency'] < 0.75 else "Variable")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Sleep duration chart using Streamlit's native chart
        if len(analysis_df) > 0:
            chart_data = analysis_df.copy()
            chart_data['DateStr'] = chart_data['Date'].dt.strftime('%m-%d')
            st.subheader('Sleep Duration by Date')
            st.bar_chart(chart_data.set_index('DateStr')['SleepDuration'])
            
            # Add reference lines for recommended sleep
            st.caption("Recommended range: 7-9 hours per night")
            
            # Bedtime consistency chart
            bedtimes_df = analysis_df.copy()
            bedtimes_df['BedtimeHour'] = bedtimes_df['Bedtime'].apply(
                lambda x: x.hour + x.minute/60 if hasattr(x, 'hour') else 0
            )
            bedtimes_df['DateStr'] = bedtimes_df['Date'].dt.strftime('%m-%d')
            
            st.subheader('Bedtime Consistency')
            st.line_chart(bedtimes_df.set_index('DateStr')['BedtimeHour'])
        
        # Recommendations
        st.markdown('<h2 class="sub-header">Recommendations</h2>', unsafe_allow_html=True)
        for rec in analysis['recommendations']:
            st.markdown(f'<div class="recommendation">📌 {rec}</div>', unsafe_allow_html=True)
    
    else:
        st.info("Add your sleep data to see analysis and recommendations.")
        st.markdown("![Sleep Image](https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80)")
        st.caption("Quality sleep is essential for good health")

# Footer with references
st.markdown("---")
st.markdown("""
    **References:**
    - [Sleep regularity and mortality risk](https://www.sciencedaily.com/releases/2024/02/240222214147.htm)
    - [Regular sleep schedule and lower mortality risk](https://www.health.com/regular-sleep-schedule-lower-mortality-risk-8413749)
    - [Health conditions linked to irregular sleep](https://www.thesun.co.uk/health/36076579/gangrene-liver-damage-diabetes-conditions-late-bedtime)
""")