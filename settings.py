import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add paths to import custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_settings():
    """Display the settings page for the clinic management system."""
    st.title("System Settings")
    
    # Create tabs for different settings categories
    tab1, tab2, tab3, tab4 = st.tabs([
        "General Settings", 
        "Notification Settings", 
        "AI Model Settings",
        "System Information"
    ])
    
    with tab1:
        st.subheader("General Clinic Settings")
        
        # Clinic information
        with st.form("clinic_info_form"):
            st.markdown("### Clinic Information")
            
            # Clinic name
            clinic_name = st.text_input("Clinic Name", value="Jayanagar Specialty Clinic")
            
            # Operating hours
            col1, col2 = st.columns(2)
            with col1:
                opening_time = st.time_input("Opening Time", value=datetime.strptime("09:00", "%H:%M").time())
            with col2:
                closing_time = st.time_input("Closing Time", value=datetime.strptime("20:00", "%H:%M").time())
            
            # Peak hours
            col1, col2 = st.columns(2)
            with col1:
                peak_start = st.time_input("Peak Hours Start", value=datetime.strptime("17:00", "%H:%M").time())
            with col2:
                peak_end = st.time_input("Peak Hours End", value=datetime.strptime("20:00", "%H:%M").time())
            
            # Default appointment duration
            default_duration = st.slider("Default Appointment Duration (minutes)", 
                                       min_value=5, max_value=60, value=15, step=5)
            
            # Buffer time between appointments
            buffer_time = st.slider("Buffer Time Between Appointments (minutes)", 
                                  min_value=0, max_value=15, value=5, step=5)
            
            # Submit button
            if st.form_submit_button("Save General Settings"):
                st.success("General settings saved successfully!")
        
        # Queue management settings
        with st.form("queue_settings_form"):
            st.markdown("### Queue Management Settings")
            
            # Early arrival handling
            early_arrival_handling = st.selectbox(
                "Early Arrival Handling Policy",
                options=[
                    "Strict Scheduled Time",
                    "Dynamic Queue Adjustment",
                    "Priority Based on Arrival Time"
                ],
                index=1
            )
            
            # Maximum wait time threshold
            max_wait_threshold = st.slider("Maximum Wait Time Alert Threshold (minutes)", 
                                         min_value=15, max_value=60, value=30, step=5)
            
            # Enable wait time predictions
            enable_predictions = st.checkbox("Enable AI Wait Time Predictions", value=True)
            
            # Queue display settings
            queue_display = st.multiselect(
                "Information to Display on Public Queue Screen",
                options=[
                    "Patient Name",
                    "Patient ID",
                    "Doctor Name",
                    "Specialty",
                    "Scheduled Time",
                    "Estimated Wait Time",
                    "Queue Position"
                ],
                default=["Patient ID", "Doctor Name", "Specialty", "Estimated Wait Time", "Queue Position"]
            )
            
            # Submit button
            if st.form_submit_button("Save Queue Settings"):
                st.success("Queue management settings saved successfully!")
    
    with tab2:
        st.subheader("Notification Settings")
        
        # SMS notification settings
        with st.form("notification_settings_form"):
            st.markdown("### Patient Notification Settings")
            
            # Enable SMS notifications
            enable_sms = st.checkbox("Enable SMS Notifications", value=True)
            
            # Notification timing
            if enable_sms:
                # Appointment reminders
                st.markdown("#### Appointment Reminders")
                send_day_before = st.checkbox("Send reminder day before appointment", value=True)
                send_hour_before = st.checkbox("Send reminder 1 hour before appointment", value=True)
                
                # Wait time notifications
                st.markdown("#### Wait Time Notifications")
                wait_time_threshold = st.slider("Send notification if wait time exceeds (minutes)", 
                                               min_value=15, max_value=60, value=30, step=5)
                
                notify_delays = st.checkbox("Notify patients of significant delays", value=True)
                
                # Notification templates
                st.markdown("#### Notification Templates")
                
                reminder_template = st.text_area(
                    "Appointment Reminder Template",
                    value="Hello, this is a reminder about your appointment at Jayanagar Specialty Clinic on [DATE] at [TIME]. Please arrive 10 minutes before your scheduled time. Reply CONFIRM to confirm your appointment."
                )
                
                wait_time_template = st.text_area(
                    "Wait Time Update Template",
                    value="Hello, your current estimated wait time at Jayanagar Specialty Clinic is [WAIT_TIME] minutes. We apologize for any inconvenience. Please contact the reception if you have any questions."
                )
            
            # Submit button
            if st.form_submit_button("Save Notification Settings"):
                st.success("Notification settings saved successfully!")
        
        # Staff notification settings
        with st.form("staff_notification_form"):
            st.markdown("### Staff Notification Settings")
            
            # Enable staff notifications
            enable_staff_notifications = st.checkbox("Enable Staff Notifications", value=True)
            
            if enable_staff_notifications:
                # Notification types
                notify_high_volume = st.checkbox("Notify when patient volume exceeds threshold", value=True)
                notify_doctor_delay = st.checkbox("Notify when doctor is running behind schedule", value=True)
                
                # Threshold settings
                volume_threshold = st.slider("High volume threshold (patients waiting)", 
                                           min_value=5, max_value=30, value=15, step=5)
                
                delay_threshold = st.slider("Doctor delay threshold (minutes)", 
                                          min_value=15, max_value=60, value=30, step=5)
            
            # Submit button
            if st.form_submit_button("Save Staff Notification Settings"):
                st.success("Staff notification settings saved successfully!")
    
    with tab3:
        st.subheader("AI Model Settings")
        
        # AI model information
        if 'wait_time_predictor' in st.session_state:
            wait_time_predictor = st.session_state.wait_time_predictor
            
            # Check if model is trained
            model_status = "Trained" if wait_time_predictor.model_trained else "Not Trained"
            
            st.info(f"**Wait Time Prediction Model Status:** {model_status}")
            
            # Display feature importance if available
            if wait_time_predictor.model_trained and wait_time_predictor.feature_importance is not None:
                st.subheader("Model Feature Importance")
                
                # Get top 10 features
                top_features = wait_time_predictor.feature_importance.head(10)
                
                # Create bar chart
                st.bar_chart(top_features)
                
                st.markdown("These features have the most significant impact on wait time predictions.")
        
        # Model settings
        with st.form("model_settings_form"):
            st.markdown("### Wait Time Prediction Model Settings")
            
            # Model update frequency
            update_frequency = st.selectbox(
                "Model Update Frequency",
                options=["Daily", "Weekly", "Monthly", "Manual Only"],
                index=1
            )
            
            # Prediction confidence threshold
            confidence_threshold = st.slider("Prediction Confidence Threshold", 
                                          min_value=0.0, max_value=1.0, value=0.7, step=0.1)
            
            # Features to use
            st.markdown("#### Model Features")
            
            use_hour_of_day = st.checkbox("Hour of Day", value=True)
            use_day_of_week = st.checkbox("Day of Week", value=True)
            use_specialty = st.checkbox("Doctor Specialty", value=True)
            use_doctor_experience = st.checkbox("Doctor Experience", value=True)
            use_consultation_time = st.checkbox("Average Consultation Time", value=True)
            use_patient_count = st.checkbox("Patient Count", value=True)
            use_early_arrival = st.checkbox("Early Arrival Pattern", value=True)
            
            # Submit button
            if st.form_submit_button("Save Model Settings"):
                st.success("Model settings saved successfully!")
        
        # Model actions
        st.markdown("### Model Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Retrain Model with Current Data"):
                if 'wait_time_predictor' in st.session_state and 'data_processor' in st.session_state:
                    with st.spinner("Retraining model..."):
                        # Get data
                        appointments_df = st.session_state.data_processor.load_appointment_data()
                        doctors_df = st.session_state.data_processor.load_doctor_data()
                        
                        # Retrain model
                        success = st.session_state.wait_time_predictor.train(appointments_df, doctors_df)
                        
                        if success:
                            st.success("Model retrained successfully!")
                        else:
                            st.error("Failed to retrain model. Check data availability.")
        
        with col2:
            if st.button("Reset Model to Default"):
                st.warning("This will reset the model to its default state.")
                reset_confirmed = st.checkbox("Confirm reset")
                
                if reset_confirmed:
                    if 'wait_time_predictor' in st.session_state:
                        # Create a new model instance
                        st.session_state.wait_time_predictor = type(st.session_state.wait_time_predictor)()
                        st.success("Model reset to default!")
    
    with tab4:
        st.subheader("System Information")
        
        # Get current datetime from session state
        current_datetime = datetime.combine(
            st.session_state.current_date,
            st.session_state.current_time
        )
        
        # Display system information
        st.markdown("### Clinic Management System")
        st.markdown("**Version:** 1.0.0")
        st.markdown(f"**System Time:** {current_datetime.strftime('%Y-%m-%d %H:%M')}")
        
        # Check if data is loaded
        data_loaded = 'appointments_df' in st.session_state and 'doctors_df' in st.session_state
        model_trained = 'wait_time_predictor' in st.session_state and st.session_state.wait_time_predictor.model_trained
        
        # Display component status
        st.markdown("### Component Status")
        
        components = [
            {"name": "Data Processor", "status": "Active" if data_loaded else "Inactive"},
            {"name": "Wait Time Prediction Model", "status": "Trained" if model_trained else "Not Trained"},
            {"name": "Schedule Optimizer", "status": "Active" if 'schedule_optimizer' in st.session_state else "Inactive"},
            {"name": "Notification System", "status": "Simulated"},
            {"name": "User Interface", "status": "Active"}
        ]
        
        # Create DataFrame for display
        components_df = pd.DataFrame(components)
        
        # Set colors based on status
        components_df['color'] = components_df['status'].apply(
            lambda x: 'green' if x in ['Active', 'Trained'] else 'red' if x in ['Inactive', 'Not Trained'] else 'orange'
        )
        
        # Display status table
        for _, component in components_df.iterrows():
            st.markdown(
                f"<div style='display: flex; justify-content: space-between;'>"
                f"<span>{component['name']}</span>"
                f"<span style='color: {component['color']};'>{component['status']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        
        # System maintenance
        st.markdown("### System Maintenance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Cache"):
                st.info("Cache would be cleared in a real system.")
                st.success("Cache cleared successfully!")
        
        with col2:
            if st.button("Backup System Data"):
                st.info("System data would be backed up in a real system.")
                st.success("Backup created successfully!")

if __name__ == "__main__":
    # This allows the module to be run directly
    show_settings()
