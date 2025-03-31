import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add paths to import custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import custom modules
from utils.data_processor import DataProcessor
from utils.visualization import create_wait_time_heatmap, create_early_arrival_chart

def show_reports():
    """Display the reports and analytics page."""
    st.title("Reports & Analytics")
    
    # Get current datetime from session state
    current_datetime = datetime.combine(
        st.session_state.current_date,
        st.session_state.current_time
    )
    
    # Access data processor from session state
    data_processor = st.session_state.data_processor
    
    # Load data
    appointments_df = data_processor.load_appointment_data()
    doctors_df = data_processor.load_doctor_data()
    
    if appointments_df.empty or doctors_df.empty:
        st.error("No appointment or doctor data available. Please check data sources.")
        return
    
    # Date range selector
    st.subheader("Select Date Range for Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get min and max dates from the appointment data
        min_date = min(appointments_df['appointment_date']) if not appointments_df.empty else current_datetime.date() - timedelta(days=30)
        max_date = max(appointments_df['appointment_date']) if not appointments_df.empty else current_datetime.date()
        
        # Calculate a default start date that's within the valid range
        default_start = max(min_date, min(max_date, current_datetime.date() - timedelta(days=14)))
        
        start_date = st.date_input(
            "Start Date",
            value=default_start,
            min_value=min_date,
            max_value=max_date
        )
    
    with col2:
        # Calculate a default end date that's within the valid range
        default_end = max(min_date, min(max_date, current_datetime.date()))
        
        end_date = st.date_input(
            "End Date",
            value=default_end,
            min_value=min_date,
            max_value=max_date
        )
    
    # Fix date range if end_date is before start_date
    if end_date < start_date:
        st.warning("End date cannot be before start date. Adjusting to match start date.")
        end_date = start_date
    
    # Filter appointments by date range
    filtered_appointments = appointments_df[
        (appointments_df['appointment_date'] >= start_date) & 
        (appointments_df['appointment_date'] <= end_date)
    ]
    
    if filtered_appointments.empty:
        st.warning(f"No appointment data available for the selected date range ({start_date} to {end_date}).")
        return
    
    # Display key metrics for the selected period
    st.subheader("Key Metrics Summary")
    
    # Calculate metrics
    total_appointments = len(filtered_appointments)
    avg_wait_time = round(filtered_appointments['wait_time_minutes'].mean(), 1)
    max_wait_time = filtered_appointments['wait_time_minutes'].max()
    early_arrivals = filtered_appointments[filtered_appointments['arrived_early'] == True]
    early_arrival_rate = len(early_arrivals) / total_appointments * 100
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Appointments", total_appointments)
    
    with col2:
        st.metric("Avg Wait Time", f"{avg_wait_time} min")
    
    with col3:
        st.metric("Max Wait Time", f"{max_wait_time} min")
    
    with col4:
        st.metric("Early Arrival Rate", f"{early_arrival_rate:.1f}%")
    
    # Wait Time Analysis
    st.subheader("Wait Time Analysis")
    
    # Create tabs for different wait time visualizations
    tab1, tab2, tab3 = st.tabs(["Wait Time by Hour", "Wait Time by Day", "Wait Time by Specialty"])
    
    with tab1:
        # Group by hour of day
        hour_wait_times = filtered_appointments.groupby('hour_of_day')['wait_time_minutes'].mean().reset_index()
        hour_wait_times['hour_label'] = hour_wait_times['hour_of_day'].apply(lambda x: f"{x}:00")
        
        # Create bar chart
        fig = px.bar(
            hour_wait_times,
            x='hour_label',
            y='wait_time_minutes',
            labels={
                'hour_label': 'Hour of Day',
                'wait_time_minutes': 'Average Wait Time (minutes)'
            },
            title="Average Wait Time by Hour of Day"
        )
        
        # Add color zones for different wait time levels
        fig.add_hrect(
            y0=0, y1=15,
            fillcolor="green", opacity=0.1,
            layer="below", line_width=0,
        )
        
        fig.add_hrect(
            y0=15, y1=30,
            fillcolor="orange", opacity=0.1,
            layer="below", line_width=0,
        )
        
        fig.add_hrect(
            y0=30, y1=100,
            fillcolor="red", opacity=0.1,
            layer="below", line_width=0,
        )
        
        # Highlight peak hours
        peak_hours = ['17:00', '18:00', '19:00']
        fig.for_each_trace(
            lambda trace: trace.update(marker_color=['#ff5252' if x in peak_hours else '#1e88e5' for x in hour_wait_times['hour_label']])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show insights
        peak_wait_time = hour_wait_times[hour_wait_times['hour_label'].isin(peak_hours)]['wait_time_minutes'].mean()
        non_peak_wait_time = hour_wait_times[~hour_wait_times['hour_label'].isin(peak_hours)]['wait_time_minutes'].mean()
        
        st.info(f"**Insight:** Peak hour (5PM-7PM) wait times average **{peak_wait_time:.1f} minutes**, which is **{(peak_wait_time/non_peak_wait_time - 1)*100:.1f}%** higher than non-peak hours.")
    
    with tab2:
        # Create wait time heatmap by day and hour
        wait_time_heatmap = create_wait_time_heatmap(filtered_appointments)
        st.plotly_chart(wait_time_heatmap, use_container_width=True)
        
        # Show day of week analysis
        day_wait_times = filtered_appointments.groupby('day_of_week')['wait_time_minutes'].mean().reset_index()
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_wait_times['day_name'] = day_wait_times['day_of_week'].apply(lambda x: day_names[x])
        
        busiest_day = day_wait_times.loc[day_wait_times['wait_time_minutes'].idxmax(), 'day_name']
        least_busy_day = day_wait_times.loc[day_wait_times['wait_time_minutes'].idxmin(), 'day_name']
        
        st.info(f"**Insight:** {busiest_day} is typically the busiest day with the longest wait times, while {least_busy_day} has the shortest wait times.")
    
    with tab3:
        # Merge appointments with doctor data to get specialties
        merged_data = filtered_appointments.merge(
            doctors_df[['doctor_id', 'specialty']], 
            on='doctor_id',
            how='inner'
        )
        
        # Group by specialty
        specialty_wait_times = merged_data.groupby('specialty')['wait_time_minutes'].mean().reset_index()
        
        # Sort by wait time (descending)
        specialty_wait_times = specialty_wait_times.sort_values('wait_time_minutes', ascending=False)
        
        # Create bar chart
        fig = px.bar(
            specialty_wait_times,
            x='specialty',
            y='wait_time_minutes',
            color='wait_time_minutes',
            color_continuous_scale=['green', 'yellow', 'red'],
            labels={
                'specialty': 'Specialty',
                'wait_time_minutes': 'Average Wait Time (minutes)'
            },
            title="Average Wait Time by Specialty"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show specialty insights
        highest_wait_specialty = specialty_wait_times.iloc[0]['specialty']
        lowest_wait_specialty = specialty_wait_times.iloc[-1]['specialty']
        
        st.info(f"**Insight:** {highest_wait_specialty} has the highest average wait time, while {lowest_wait_specialty} has the lowest.")
    
    # Patient Arrival Patterns
    st.subheader("Patient Arrival Patterns")
    
    # Early arrival chart
    early_arrival_chart = create_early_arrival_chart(filtered_appointments)
    st.plotly_chart(early_arrival_chart, use_container_width=True)
    
    # Calculate peak hour early arrival percentage
    peak_hours_appointments = filtered_appointments[filtered_appointments['hour_of_day'].isin([17, 18, 19])]
    peak_early_arrivals = peak_hours_appointments[peak_hours_appointments['arrived_early'] == True]
    peak_early_arrival_rate = len(peak_early_arrivals) / len(peak_hours_appointments) * 100 if len(peak_hours_appointments) > 0 else 0
    
    st.info(f"**Insight:** During peak hours (5PM-7PM), **{peak_early_arrival_rate:.1f}%** of patients arrive early, compared to the overall average of **{early_arrival_rate:.1f}%**.")
    
    # Doctor Performance Analysis
    st.subheader("Doctor Performance Analysis")
    
    # Merge appointments with doctor data
    doctor_performance = filtered_appointments.merge(
        doctors_df,
        on='doctor_id',
        how='inner'
    )
    
    # Group by doctor
    doctor_metrics = doctor_performance.groupby(['doctor_id', 'doctor_name', 'specialty']).agg(
        avg_wait_time=('wait_time_minutes', 'mean'),
        appointments_count=('appointment_id', 'count'),
        early_arrival_rate=('arrived_early', 'mean')
    ).reset_index()
    
    # Calculate early arrival rate as percentage
    doctor_metrics['early_arrival_rate'] = doctor_metrics['early_arrival_rate'] * 100
    
    # Round metrics
    doctor_metrics['avg_wait_time'] = doctor_metrics['avg_wait_time'].round(1)
    doctor_metrics['early_arrival_rate'] = doctor_metrics['early_arrival_rate'].round(1)
    
    # Create a scatter plot of wait time vs number of appointments
    fig = px.scatter(
        doctor_metrics,
        x='appointments_count',
        y='avg_wait_time',
        color='specialty',
        size='early_arrival_rate',
        hover_name='doctor_name',
        labels={
            'appointments_count': 'Number of Appointments',
            'avg_wait_time': 'Average Wait Time (minutes)',
            'early_arrival_rate': 'Early Arrival Rate (%)'
        },
        title="Doctor Performance Analysis"
    )
    
    fig.update_traces(
        marker=dict(line=dict(width=1, color='DarkSlateGrey')),
        selector=dict(mode='markers')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show insights for doctors
    highest_volume_doctor = doctor_metrics.loc[doctor_metrics['appointments_count'].idxmax()]
    lowest_wait_doctor = doctor_metrics.loc[doctor_metrics['avg_wait_time'].idxmin()]
    
    st.info(f"""
    **Doctor Insights:**
    - Dr. {highest_volume_doctor['doctor_name']} ({highest_volume_doctor['specialty']}) had the highest patient volume with {highest_volume_doctor['appointments_count']} appointments.
    - Dr. {lowest_wait_doctor['doctor_name']} ({lowest_wait_doctor['specialty']}) had the lowest average wait time at {lowest_wait_doctor['avg_wait_time']} minutes.
    """)
    
    # AI-Generated Recommendations
    st.subheader("AI-Generated Optimization Recommendations")
    
    # Get recommendations from the schedule optimizer
    schedule_optimizer = st.session_state.schedule_optimizer
    recommendations = schedule_optimizer.get_recommendations(
        current_datetime,
        appointments_df,
        doctors_df
    )
    
    # Display recommendations
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")
    
    # Export options
    st.subheader("Export Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Wait Time Analysis"):
            st.info("Wait time analysis report would be exported here in a real system.")
    
    with col2:
        if st.button("Export Doctor Performance Report"):
            st.info("Doctor performance report would be exported here in a real system.")

if __name__ == "__main__":
    # This allows the module to be run directly
    show_reports()
