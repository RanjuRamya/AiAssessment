import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from math import ceil

# Add paths to import custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_all_appointments():
    """Display all appointments with priority highlighting based on dates and times."""
    st.title("All Appointments")
    
    # Initialize session state if needed (for cases when this page is accessed directly)
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
    if 'appointments_df' not in st.session_state:
        st.session_state.appointments_df = data_processor.load_appointment_data()
    if 'doctors_df' not in st.session_state:
        st.session_state.doctors_df = data_processor.load_doctor_data()
    
    appointments_df = st.session_state.appointments_df
    doctors_df = st.session_state.doctors_df
    
    if appointments_df.empty or doctors_df.empty:
        st.error("No appointment or doctor data available. Please check data sources.")
        return
    
    # Add date difference from current date to appointments
    appointments_df['date_diff'] = appointments_df['appointment_date'].apply(
        lambda x: (x - current_datetime.date()).days
    )
    
    # Merge appointments with doctor information
    merged_data = appointments_df.merge(
        doctors_df[['doctor_id', 'doctor_name', 'specialty', 'avg_consultation_time', 'is_available']],
        on='doctor_id',
        how='left'
    )
    
    # Filters section
    st.subheader("Filter Appointments")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Date range filter
        date_range = st.selectbox(
            "Date Range", 
            options=[
                "All Dates", 
                "Today", 
                "This Week", 
                "This Month", 
                "Past Appointments", 
                "Future Appointments"
            ],
            index=0
        )
    
    with col2:
        # Specialty filter
        specialties = ["All Specialties"] + sorted(doctors_df['specialty'].unique().tolist())
        selected_specialty = st.selectbox("Specialty", specialties)
    
    with col3:
        # Priority filter
        priority_options = ["All Priorities", "High Priority", "Medium Priority", "Low Priority"]
        selected_priority = st.selectbox("Priority", priority_options)
    
    # Apply filters
    filtered_data = merged_data.copy()
    
    # Date range filter
    if date_range == "Today":
        filtered_data = filtered_data[filtered_data['appointment_date'] == current_datetime.date()]
    elif date_range == "This Week":
        # Current day to next 7 days
        filtered_data = filtered_data[
            (filtered_data['date_diff'] >= 0) & 
            (filtered_data['date_diff'] < 7)
        ]
    elif date_range == "This Month":
        # Current day to next 30 days
        filtered_data = filtered_data[
            (filtered_data['date_diff'] >= 0) & 
            (filtered_data['date_diff'] < 30)
        ]
    elif date_range == "Past Appointments":
        filtered_data = filtered_data[filtered_data['date_diff'] < 0]
    elif date_range == "Future Appointments":
        filtered_data = filtered_data[filtered_data['date_diff'] >= 0]
    
    # Specialty filter
    if selected_specialty != "All Specialties":
        filtered_data = filtered_data[filtered_data['specialty'] == selected_specialty]
    
    # Calculate priority scores
    def calculate_priority(row):
        # Base priority score based on date proximity
        date_diff = row['date_diff']
        
        if date_diff == 0:  # Today
            date_score = 100
        elif 0 < date_diff <= 3:  # Next 3 days
            date_score = 80
        elif 3 < date_diff <= 7:  # Within a week
            date_score = 60
        elif 7 < date_diff <= 14:  # Within two weeks
            date_score = 40
        elif date_diff < 0:  # Past appointments
            date_score = 20
        else:  # More than two weeks away
            date_score = 30
        
        # Adjust score based on early arrival status
        if row['arrived_early']:
            date_score += 10
        
        # Adjust score based on wait time
        wait_time = row['wait_time_minutes']
        if wait_time > 30:
            date_score += 15
        
        # Determine priority category
        if date_score >= 75:
            return "High", date_score
        elif date_score >= 50:
            return "Medium", date_score
        else:
            return "Low", date_score
    
    # Apply priority calculation
    priority_data = []
    for _, row in filtered_data.iterrows():
        priority_category, priority_score = calculate_priority(row)
        
        # Create a combined row with priority information
        combined_row = row.to_dict()
        combined_row['priority_category'] = priority_category
        combined_row['priority_score'] = priority_score
        
        priority_data.append(combined_row)
    
    # Convert back to DataFrame
    priority_df = pd.DataFrame(priority_data)
    
    # Apply priority filter
    if selected_priority != "All Priorities":
        priority_category = selected_priority.split()[0]  # Extract "High", "Medium", or "Low"
        priority_df = priority_df[priority_df['priority_category'] == priority_category]
    
    # Sort by date and priority
    priority_df = priority_df.sort_values(['date_diff', 'priority_score'], ascending=[True, False])
    
    # Dashboard metrics
    st.subheader("Appointment Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_count = len(priority_df)
        st.metric("Total Appointments", total_count)
    
    with col2:
        high_priority = len(priority_df[priority_df['priority_category'] == "High"])
        high_percentage = (high_priority / total_count * 100) if total_count > 0 else 0
        st.metric("High Priority", f"{high_priority} ({high_percentage:.1f}%)")
    
    with col3:
        today_count = len(priority_df[priority_df['date_diff'] == 0])
        st.metric("Today's Appointments", today_count)
    
    with col4:
        upcoming_count = len(priority_df[priority_df['date_diff'] > 0])
        st.metric("Upcoming Appointments", upcoming_count)
    
    # Visualize appointments by date
    st.subheader("Appointments by Date")
    
    # Create date count data
    if not priority_df.empty:
        # Group by date and count
        date_counts = priority_df.groupby(['appointment_date', 'priority_category']).size().reset_index(name='count')
        
        # Create date chart
        fig = px.bar(
            date_counts,
            x='appointment_date',
            y='count',
            color='priority_category',
            color_discrete_map={
                'High': 'red',
                'Medium': 'orange',
                'Low': 'green'
            },
            labels={
                'appointment_date': 'Date',
                'count': 'Number of Appointments',
                'priority_category': 'Priority'
            },
            title="Appointments by Date and Priority"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No appointment data available for the selected filters.")
    
    # List all appointments with priority highlighting
    st.subheader(f"All Appointments ({len(priority_df)})")
    
    if not priority_df.empty:
        # Group appointments by date
        dates = priority_df['appointment_date'].unique()
        
        for date in sorted(dates):
            date_appointments = priority_df[priority_df['appointment_date'] == date]
            
            # Format date for display
            date_str = date.strftime("%A, %B %d, %Y")
            
            # Calculate date difference from current date
            date_diff = (date - current_datetime.date()).days
            
            if date_diff == 0:
                date_badge = "📌 TODAY"
            elif date_diff > 0:
                date_badge = f"⏳ In {date_diff} days"
            else:
                date_badge = f"⌛ {abs(date_diff)} days ago"
            
            st.markdown(f"### {date_str} {date_badge}")
            
            # Display appointments for this date
            for i, (_, appointment) in enumerate(date_appointments.iterrows()):
                # Format appointment time
                appt_time = appointment['appointment_time']
                time_str = f"{appt_time.hour:02d}:{appt_time.minute:02d}"
                
                # Define priority colors
                priority_colors = {
                    "High": "red",
                    "Medium": "orange",
                    "Low": "green"
                }
                
                priority_color = priority_colors[appointment['priority_category']]
                
                # Format doctor availability
                doctor_status = "✅ Available" if appointment['is_available'] else "❌ Unavailable"
                
                # Create the appointment card
                with st.expander(f"{time_str} - Patient {appointment['patient_id']} - Dr. {appointment['doctor_name']} - **{appointment['priority_category']} Priority**"):
                    # Main details in a grid
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Patient ID:** {appointment['patient_id']}")
                        st.markdown(f"**Appointment Time:** {time_str}")
                        st.markdown(f"**Wait Time Estimate:** {appointment['wait_time_minutes']} minutes")
                        
                        # Early arrival indicator
                        if appointment['arrived_early']:
                            st.markdown("🏃 **Patient tends to arrive early**")
                    
                    with col2:
                        st.markdown(f"**Doctor:** Dr. {appointment['doctor_name']} ({doctor_status})")
                        st.markdown(f"**Specialty:** {appointment['specialty']}")
                        st.markdown(f"**Expected Duration:** {appointment['avg_consultation_time']} minutes")
                        st.markdown(f"**Priority Score:** {appointment['priority_score']}")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(f"Send Reminder #{i}", key=f"remind_{appointment['appointment_id']}"):
                            st.success(f"Reminder sent to patient {appointment['patient_id']}")
                    
                    with col2:
                        if st.button(f"Reschedule #{i}", key=f"resc_{appointment['appointment_id']}"):
                            st.success(f"Patient {appointment['patient_id']} flagged for rescheduling")
                    
                    with col3:
                        if st.button(f"Cancel #{i}", key=f"cancel_{appointment['appointment_id']}"):
                            st.error(f"Appointment for patient {appointment['patient_id']} cancelled")
                    
                    # Display priority reason
                    st.markdown(f"""
                    **Priority Notes:**
                    - Date proximity: {'Today' if date_diff == 0 else f'{abs(date_diff)} days {"away" if date_diff > 0 else "ago"}'}
                    - Estimated wait time: {appointment['wait_time_minutes']} minutes
                    - Early arrival: {'Yes' if appointment['arrived_early'] else 'No'}
                    """)
    else:
        st.info("No appointments found with the selected filters.")
    
    # Priority explanation
    with st.expander("Understanding Priority Levels"):
        st.markdown("""
        ### Priority Levels Explained
        
        Appointments are automatically assigned priority levels based on the following factors:
        
        **High Priority**
        - Today's appointments
        - Appointments within the next 3 days
        - Appointments with long estimated wait times (>30 min)
        
        **Medium Priority**
        - Appointments within 4-7 days
        - Patients who typically arrive early
        
        **Low Priority**
        - Appointments more than 7 days away
        - Past appointments
        
        The priority system helps staff focus on the most urgent appointments for better patient care.
        """)

if __name__ == "__main__":
    # This allows the module to be run directly
    show_all_appointments()