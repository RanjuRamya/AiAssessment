import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Add paths to import custom modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import custom modules
from models.wait_time_predictor import WaitTimePredictor
from models.schedule_optimizer import ScheduleOptimizer
from utils.data_processor import DataProcessor
from utils.visualization import create_wait_time_chart, create_patient_flow_chart

# Page configuration
st.set_page_config(
    page_title="Jayanagar Specialty Clinic AI Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import login functionality
from pages.login import show_login_signup

# Initialize session state variables if they don't exist
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()

if 'wait_time_predictor' not in st.session_state:
    st.session_state.wait_time_predictor = WaitTimePredictor()

if 'schedule_optimizer' not in st.session_state:
    st.session_state.schedule_optimizer = ScheduleOptimizer()

if 'current_date' not in st.session_state:
    # Use today's date
    st.session_state.current_date = datetime.now().date()

if 'current_time' not in st.session_state:
    # Use current time or set to 17:30 (5:30 PM) for demonstration of peak hours
    current_hour = datetime.now().hour
    if 9 <= current_hour <= 20:  # If within business hours (9 AM - 8 PM)
        st.session_state.current_time = datetime.now().time()
    else:
        # Default to peak hours for demonstration if outside business hours
        st.session_state.current_time = datetime.strptime("17:30", "%H:%M").time()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Load data
def load_data():
    # Check if data is already loaded in session state
    if 'appointments_df' not in st.session_state:
        try:
            # Load and process appointment data
            st.session_state.appointments_df = st.session_state.data_processor.load_appointment_data()
            st.session_state.doctors_df = st.session_state.data_processor.load_doctor_data()
            
            # Train the prediction model
            st.session_state.wait_time_predictor.train(
                st.session_state.appointments_df,
                st.session_state.doctors_df
            )
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.session_state.appointments_df = pd.DataFrame()
            st.session_state.doctors_df = pd.DataFrame()

load_data()

# Check authentication
is_authenticated = show_login_signup()

# Only show the main app content if authenticated
if is_authenticated:
    # Sidebar navigation
    st.sidebar.title("Clinic Management System")
    # Use text icon instead of image to avoid external dependency
    st.sidebar.markdown("## 🏥")

    # Time simulation controls
    st.sidebar.header("Time Simulation")
    if st.sidebar.button("⏱️ Advance Time (30 min)"):
        # Advance the simulated time by 30 minutes
        current_datetime = datetime.combine(
            st.session_state.current_date,
            st.session_state.current_time
        )
        new_datetime = current_datetime + timedelta(minutes=30)
        st.session_state.current_date = new_datetime.date()
        st.session_state.current_time = new_datetime.time()
        st.rerun()

    # Display current simulated time
    current_datetime = datetime.combine(
        st.session_state.current_date,
        st.session_state.current_time
    )
    st.sidebar.write(f"Current Time: {current_datetime.strftime('%Y-%m-%d %H:%M')}")

    # Set up navigation options
    nav_options = [
        "📊 Dashboard",
        "🗓️ Book Appointment",
        "📆 All Appointments",
        "🔍 Appointment Navigator",
        "👥 Patient Queue Management",
        "👨‍⚕️ Doctor Management", 
        "🏆 Staff Efficiency Dashboard",
        "📝 Reports & Analytics",
        "⚙️ Settings"
    ]

    # Check if we need to navigate based on button clicks
    if 'nav_selection' in st.session_state:
        selected_nav = st.session_state.nav_selection
        # Find the index of the selected nav option
        try:
            default_idx = nav_options.index(selected_nav)
        except ValueError:
            default_idx = 0
        # Clear the selection after using it
        st.session_state.nav_selection = None
    else:
        default_idx = 0

    # Display the navigation sidebar
    page = st.sidebar.radio(
        "Navigation",
        nav_options,
        index=default_idx
    )

    # Page routing
    if page == "📊 Dashboard":
        # WELCOME PAGE / OPENING PAGE
        st.title("Welcome to Jayanagar Specialty Clinic")
        
        # Display user's name if available
        if st.session_state.current_user:
            st.success(f"Welcome, {st.session_state.current_user['name']}!")
        
        # Header image or logo
        st.image("generated-icon.png", width=150)
        
        # Welcome message
        st.markdown("""
        ### AI-Powered Clinic Management System
        
        Welcome to our intelligent clinic management platform designed to optimize patient flow, 
        reduce wait times, and enhance the experience for both patients and staff.
        """)
        
        # Quick stats overview
        st.subheader("Today at a Glance")
        
        # Get summary metrics from the data processor
        metrics = st.session_state.data_processor.get_summary_metrics(current_datetime)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Current Wait Time", 
                value=f"{metrics['avg_wait_time']} min",
                delta=f"{metrics['wait_time_delta']} min"
            )
        
        with col2:
            st.metric(
                label="Patients Today", 
                value=metrics['total_appointments'],
                delta=metrics['completed_appointments']
            )
        
        with col3:
            st.metric(
                label="In Queue Now", 
                value=metrics['patients_in_queue']
            )
        
        with col4:
            st.metric(
                label="Doctors Available", 
                value=f"{metrics['available_doctors']}/{metrics['total_doctors']}"
            )
        
        # Quick actions section with large, clickable cards
        st.subheader("Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Appointment booking card
            st.markdown("""
            <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center; background-color: #f8f9fa;">
                <h3 style="color: #0066cc;">📅 Book an Appointment</h3>
                <p>Schedule a new appointment with any of our specialists</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Book Now", key="book_btn"):
                st.session_state.nav_selection = "🗓️ Book Appointment"
                st.rerun()
        
        with col2:
            # Check appointments card
            st.markdown("""
            <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center; background-color: #f8f9fa;">
                <h3 style="color: #0066cc;">🔍 View Appointments</h3>
                <p>Check your upcoming appointments and wait times</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("View Appointments", key="view_appt_btn"):
                st.session_state.nav_selection = "🔍 Appointment Navigator"
                st.rerun()
        
        # Current status section
        st.subheader("Current Clinic Status")
        
        # Wait time chart
        st.markdown("#### Estimated Wait Times")
        wait_time_chart = create_wait_time_chart(
            st.session_state.data_processor.get_wait_time_predictions(current_datetime)
        )
        st.plotly_chart(wait_time_chart, use_container_width=True)
        
        # Specialty status
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Queue Status by Specialty")
            specialty_data = st.session_state.data_processor.get_specialty_queue_data(current_datetime)
            specialty_chart = st.session_state.data_processor.create_specialty_chart(specialty_data)
            st.plotly_chart(specialty_chart, use_container_width=True)
        
        with col2:
            st.markdown("#### Today's AI Insights")
            recommendations = st.session_state.schedule_optimizer.get_recommendations(
                current_datetime,
                st.session_state.appointments_df,
                st.session_state.doctors_df
            )
            
            for i, rec in enumerate(recommendations[:2], 1):
                st.info(f"**Insight {i}:** {rec}")
            
            # Patient notifications
            st.markdown("#### Recent Notifications")
            notifications = st.session_state.data_processor.get_recent_notifications(current_datetime)
            
            for notification in notifications[:3]:
                st.write(f"**{notification['time']}** - {notification['message']} (Patient ID: {notification['patient_id']})")
        
        # Features highlight
        st.subheader("Key Features")
        
        feature_col1, feature_col2, feature_col3 = st.columns(3)
        
        with feature_col1:
            st.markdown("""
            #### 🔮 AI Wait Time Prediction
            Our system uses machine learning to predict and minimize wait times for patients.
            """)
        
        with feature_col2:
            st.markdown("""
            #### 📱 Patient Notifications
            Automated notifications help keep patients informed about their appointments.
            """)
        
        with feature_col3:
            st.markdown("""
            #### 📊 Staff Efficiency Dashboard
            Performance metrics and gamification help optimize staff productivity.
            """)

    elif page == "🗓️ Book Appointment":
        # Import and run the appointment booking page
        from pages.appointment_booking import show_appointment_booking
        show_appointment_booking()
        
    elif page == "📆 All Appointments":
        # Import and run the all appointments page
        from pages.all_appointments import show_all_appointments
        show_all_appointments()

    elif page == "🔍 Appointment Navigator":
        # Import and run the appointment navigator page
        from pages.appointment_navigator import show_appointment_navigator
        show_appointment_navigator()

    elif page == "👥 Patient Queue Management":
        # Import and run the patient queue management page
        from pages.patient_queue import show_patient_queue
        show_patient_queue()

    elif page == "👨‍⚕️ Doctor Management":
        # Import and run the doctor management page
        from pages.doctor_management import show_doctor_management
        show_doctor_management()

    elif page == "🏆 Staff Efficiency Dashboard":
        # Import and run the staff dashboard page
        from pages.staff_dashboard import show_staff_dashboard
        show_staff_dashboard()

    elif page == "📝 Reports & Analytics":
        # Import and run the reports page
        from pages.reports import show_reports
        show_reports()

    elif page == "⚙️ Settings":
        # Import and run the settings page
        from pages.settings import show_settings
        show_settings()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Jayanagar Specialty Clinic AI Management System\n\n"
        "Version 1.0.0 | © 2025"
    )
