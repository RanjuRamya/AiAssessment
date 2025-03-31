import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def show_patient_queue():
    """Display the patient queue management page."""
    st.title("Patient Queue Management")
    
    # Initialize session state if needed
    if 'current_date' not in st.session_state:
        st.session_state.current_date = datetime(2023, 9, 15).date()
    
    if 'current_time' not in st.session_state:
        st.session_state.current_time = datetime.strptime("17:30", "%H:%M").time()
    
    # Get current datetime from session state
    current_datetime = datetime.combine(
        st.session_state.current_date,
        st.session_state.current_time
    )
    
    # Initialize required components if needed
    if 'data_processor' not in st.session_state:
        from utils.data_processor import DataProcessor
        st.session_state.data_processor = DataProcessor()
        
    if 'wait_time_predictor' not in st.session_state:
        from models.wait_time_predictor import WaitTimePredictor
        st.session_state.wait_time_predictor = WaitTimePredictor()
        
    if 'schedule_optimizer' not in st.session_state:
        from models.schedule_optimizer import ScheduleOptimizer
        st.session_state.schedule_optimizer = ScheduleOptimizer()
    
    # Access data processor from session state
    data_processor = st.session_state.data_processor
    
    # Load data
    appointments_df = data_processor.load_appointment_data()
    doctors_df = data_processor.load_doctor_data()
    
    if appointments_df.empty or doctors_df.empty:
        st.error("No appointment or doctor data available. Please check data sources.")
        return
    
    # Filter appointments for today
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    
    # Get all available dates in the data
    available_dates = sorted(appointments_df['appointment_date'].unique())
    
    # Show date selector
    st.subheader("Select Date")
    selected_date = st.selectbox(
        "Choose a date to view appointments",
        options=available_dates,
        index=available_dates.index(current_date) if current_date in available_dates else 0,
        format_func=lambda x: x.strftime("%A, %B %d, %Y")
    )
    
    # Update the working date
    current_date = selected_date
    current_time = current_datetime.time()  # Keep the same time
    
    # Get appointments for selected date
    today_appointments = appointments_df[appointments_df['appointment_date'] == current_date]
    
    if today_appointments.empty:
        st.warning(f"No appointments scheduled for {current_date.strftime('%A, %B %d, %Y')}.")
        return
    
    # Split into two columns for filters
    col1, col2 = st.columns(2)
    
    with col1:
        # Filter by specialty
        specialties = ['All Specialties'] + sorted(doctors_df['specialty'].unique().tolist())
        selected_specialty = st.selectbox("Filter by Specialty", specialties)
    
    with col2:
        # Filter by queue status
        queue_status = st.selectbox(
            "Queue Status",
            ['All Appointments', 'Waiting', 'Completed', 'Upcoming']
        )
    
    # Filter appointments based on selections
    filtered_appointments = today_appointments.copy()
    
    # Apply specialty filter
    if selected_specialty != 'All Specialties':
        doctor_ids = doctors_df[doctors_df['specialty'] == selected_specialty]['doctor_id'].tolist()
        filtered_appointments = filtered_appointments[filtered_appointments['doctor_id'].isin(doctor_ids)]
    
    # Apply queue status filter
    if queue_status == 'Waiting':
        # Appointments before current time but not completed
        two_hours_ago = (datetime.combine(current_date, current_time) - timedelta(hours=2)).time()
        filtered_appointments = filtered_appointments[
            (filtered_appointments['appointment_time'] >= two_hours_ago) & 
            (filtered_appointments['appointment_time'] <= current_time)
        ]
    elif queue_status == 'Completed':
        # Appointments before current time
        filtered_appointments = filtered_appointments[filtered_appointments['appointment_time'] < current_time]
    elif queue_status == 'Upcoming':
        # Appointments after current time
        filtered_appointments = filtered_appointments[filtered_appointments['appointment_time'] > current_time]
    
    # Merge with doctor information
    merged_data = filtered_appointments.merge(
        doctors_df[['doctor_id', 'doctor_name', 'specialty', 'avg_consultation_time']],
        on='doctor_id',
        how='left'
    )
    
    # Sort appointments
    if queue_status == 'Upcoming':
        merged_data = merged_data.sort_values('appointment_time')
    else:
        merged_data = merged_data.sort_values('appointment_time', ascending=False)
    
    # Display current queue summary
    st.subheader("Queue Summary")
    
    # Calculate queue metrics
    waiting_count = len(today_appointments[
        (today_appointments['appointment_time'] >= (datetime.combine(current_date, current_time) - timedelta(hours=2)).time()) & 
        (today_appointments['appointment_time'] <= current_time)
    ])
    
    completed_count = len(today_appointments[today_appointments['appointment_time'] < current_time])
    upcoming_count = len(today_appointments[today_appointments['appointment_time'] > current_time])
    
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Currently Waiting", waiting_count)
    
    with col2:
        st.metric("Completed Today", completed_count)
    
    with col3:
        st.metric("Upcoming Today", upcoming_count)
    
    # Display wait time by specialty
    st.subheader("Current Wait Times by Specialty")
    
    # Get specialty wait time data
    specialty_data = data_processor.get_specialty_queue_data(current_datetime)
    
    if not specialty_data.empty:
        # Create wait time chart
        fig = px.bar(
            specialty_data,
            x='specialty',
            y='avg_wait_time',
            color='avg_wait_time',
            color_continuous_scale=['green', 'yellow', 'red'],
            labels={
                'specialty': 'Specialty',
                'avg_wait_time': 'Average Wait Time (minutes)'
            },
            title="Current Wait Times by Specialty"
        )
        
        # Add patient count as text
        fig.add_trace(
            go.Scatter(
                x=specialty_data['specialty'],
                y=specialty_data['avg_wait_time'],
                text=specialty_data['patients_waiting'].apply(lambda x: f"{x} patients"),
                mode='text',
                textposition='top center',
                showlegend=False
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No current wait time data available.")
    
    # Display patient queue
    st.subheader(f"Patient Queue ({len(merged_data)} patients)")
    
    if not merged_data.empty:
        # Create expandable section for each patient in queue
        for i, (_, appointment) in enumerate(merged_data.iterrows(), 1):
            # Format appointment time
            appt_time = appointment['appointment_time']
            time_str = f"{appt_time.hour:02d}:{appt_time.minute:02d}"
            
            # Calculate time relative to current time
            appointment_datetime = datetime.combine(current_date, appt_time)
            time_diff = appointment_datetime - datetime.combine(current_date, current_time)
            minutes_diff = int(time_diff.total_seconds() / 60)
            
            # Format time difference
            if minutes_diff > 0:
                time_status = f"📅 In {minutes_diff} minutes"
                color = "blue"
            elif minutes_diff < -60:
                time_status = f"⏰ {abs(minutes_diff)} minutes ago"
                color = "gray"
            else:
                time_status = f"⚠️ {abs(minutes_diff)} minutes overdue"
                color = "red"
            
            # Calculate estimated wait time
            wait_time = appointment['wait_time_minutes']
            if wait_time > 30:
                wait_status = f"🔴 {wait_time} min wait"
            elif wait_time > 15:
                wait_status = f"🟠 {wait_time} min wait"
            else:
                wait_status = f"🟢 {wait_time} min wait"
            
            # Create expandable section
            with st.expander(f"Patient {appointment['patient_id']} - {time_str} - Dr. {appointment['doctor_name']} ({appointment['specialty']}) - {wait_status}"):
                # Two columns for patient details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Patient ID:** {appointment['patient_id']}")
                    st.markdown(f"**Appointment Time:** {time_str}")
                    st.markdown(f"**Status:** {time_status}")
                    
                    # Early arrival indicator
                    if appointment['arrived_early']:
                        st.markdown("🏃 **Patient arrived early**")
                
                with col2:
                    st.markdown(f"**Doctor:** Dr. {appointment['doctor_name']}")
                    st.markdown(f"**Specialty:** {appointment['specialty']}")
                    st.markdown(f"**Expected Duration:** {appointment['avg_consultation_time']} minutes")
                    st.markdown(f"**Wait Time:** {wait_time} minutes")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"Send Notification #{i}", key=f"notify_{appointment['appointment_id']}"):
                        st.success(f"Notification sent to patient {appointment['patient_id']}")
                
                with col2:
                    if st.button(f"Mark as Completed #{i}", key=f"complete_{appointment['appointment_id']}"):
                        st.success(f"Patient {appointment['patient_id']} marked as completed")
                
                with col3:
                    if st.button(f"Reschedule #{i}", key=f"reschedule_{appointment['appointment_id']}"):
                        st.success(f"Patient {appointment['patient_id']} flagged for rescheduling")
    else:
        st.info("No patients match the selected filters.")
    
    # Early arrival management section
    st.subheader("Early Arrival Management")
    
    # Calculate early arrival statistics
    early_arrivals = today_appointments[today_appointments['arrived_early'] == True]
    early_arrival_rate = len(early_arrivals) / len(today_appointments) * 100 if len(today_appointments) > 0 else 0
    
    st.write(f"Today's early arrival rate: {early_arrival_rate:.1f}% ({len(early_arrivals)} patients)")
    
    # Recommendations for handling early arrivals
    st.markdown("### Recommendations for Early Arrivals")
    
    recommendations = [
        "**Dynamic Queue Adjustment:** Patients who arrive 20-30 minutes early can be accommodated if there are gaps in the schedule.",
        "**Wait Time Transparency:** Provide realistic wait time estimates to early arrivals based on current doctor availability.",
        "**Priority System:** Consider a hybrid system that respects scheduled times but allows flexibility for early arrivals during non-peak hours."
    ]
    
    for rec in recommendations:
        st.markdown(f"- {rec}")
    
    # Option to adjust queue for early arrivals
    st.markdown("### Early Arrival Queue Adjustment")
    adjustment_enabled = st.checkbox("Enable dynamic queue adjustment for early arrivals", value=True)
    
    if adjustment_enabled:
        st.success("Dynamic queue adjustment is enabled. Early arrivals will be accommodated when possible without disrupting scheduled appointments.")
    else:
        st.info("Dynamic queue adjustment is disabled. All patients will be seen according to their scheduled appointment time.")
