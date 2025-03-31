import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add paths to import custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import custom modules
from models.wait_time_predictor import WaitTimePredictor
from models.schedule_optimizer import ScheduleOptimizer
from utils.data_processor import DataProcessor
from utils.visualization import create_wait_time_chart, create_patient_flow_chart

def show_dashboard():
    """Display the main dashboard page."""
    st.title("Clinic Dashboard")
    
    # Get current datetime from session state
    current_datetime = datetime.combine(
        st.session_state.current_date,
        st.session_state.current_time
    )
    
    # Access data processor from session state
    data_processor = st.session_state.data_processor
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get summary metrics from the data processor
    metrics = data_processor.get_summary_metrics(current_datetime)
    
    with col1:
        st.metric(
            label="Current Wait Time", 
            value=f"{metrics['avg_wait_time']} min",
            delta=f"{metrics['wait_time_delta']} min"
        )
    
    with col2:
        st.metric(
            label="Patients in Queue", 
            value=metrics['patients_in_queue'],
            delta=metrics['queue_delta']
        )
    
    with col3:
        st.metric(
            label="Available Doctors", 
            value=f"{metrics['available_doctors']}/{metrics['total_doctors']}"
        )
    
    with col4:
        st.metric(
            label="Appointments Today", 
            value=metrics['total_appointments'],
            delta=metrics['completed_appointments']
        )
    
    # Charts section
    st.subheader("Current Wait Time Predictions")
    wait_time_chart = create_wait_time_chart(
        data_processor.get_wait_time_predictions(current_datetime)
    )
    st.plotly_chart(wait_time_chart, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Patient Flow (Today)")
        patient_flow_chart = create_patient_flow_chart(
            data_processor.get_patient_flow_data(st.session_state.current_date)
        )
        st.plotly_chart(patient_flow_chart, use_container_width=True)
    
    with col2:
        st.subheader("Current Queue Status by Specialty")
        specialty_data = data_processor.get_specialty_queue_data(current_datetime)
        specialty_chart = data_processor.create_specialty_chart(specialty_data)
        st.plotly_chart(specialty_chart, use_container_width=True)
    
    # AI Insights Section
    st.subheader("🤖 AI Insights & Recommendations")
    recommendations = st.session_state.schedule_optimizer.get_recommendations(
        current_datetime,
        st.session_state.data_processor.load_appointment_data(),
        st.session_state.data_processor.load_doctor_data()
    )
    
    for i, rec in enumerate(recommendations[:3], 1):
        st.info(f"**Recommendation {i}:** {rec}")
    
    # Notification Panel (Simulated)
    st.subheader("📱 Recent Patient Notifications")
    notifications = data_processor.get_recent_notifications(current_datetime)
    
    for notification in notifications:
        st.write(f"**{notification['time']}** - {notification['message']} (Patient ID: {notification['patient_id']})")

if __name__ == "__main__":
    # This allows the module to be run directly
    show_dashboard()
