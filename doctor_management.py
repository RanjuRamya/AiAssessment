import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def show_doctor_management():
    """Display the doctor management page."""
    st.title("Doctor Management")
    
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
    
    # Current date and time
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    
    # Get all available dates in the data
    available_dates = sorted(appointments_df['appointment_date'].unique())
    
    # Show date selector
    st.subheader("Select Date")
    selected_date = st.selectbox(
        "Choose a date to view doctor workload",
        options=available_dates,
        index=available_dates.index(current_date) if current_date in available_dates else 0,
        format_func=lambda x: x.strftime("%A, %B %d, %Y")
    )
    
    # Update the working date
    current_date = selected_date
    
    # Section: Doctor Overview
    st.subheader("Doctor Overview")
    
    # Filter controls
    col1, col2 = st.columns(2)
    
    with col1:
        # Filter by specialty
        specialties = ['All Specialties'] + sorted(doctors_df['specialty'].unique().tolist())
        selected_specialty = st.selectbox("Filter by Specialty", specialties, key="doc_specialty_filter")
    
    with col2:
        # Sort options
        sort_option = st.selectbox(
            "Sort Doctors By",
            ['Name', 'Specialty', 'Current Load', 'Average Wait Time'],
            index=2
        )
    
    # Filter doctors based on specialty
    if selected_specialty != 'All Specialties':
        filtered_doctors = doctors_df[doctors_df['specialty'] == selected_specialty]
    else:
        filtered_doctors = doctors_df
    
    # Get today's appointments
    today_appointments = appointments_df[appointments_df['appointment_date'] == current_date]
    
    # Calculate current load and average wait time for each doctor
    doctor_metrics = []
    
    for _, doctor in filtered_doctors.iterrows():
        doctor_id = doctor['doctor_id']
        
        # Get appointments for this doctor today
        doctor_appointments = today_appointments[today_appointments['doctor_id'] == doctor_id]
        
        # Calculate remaining appointments (current load)
        remaining_appointments = doctor_appointments[doctor_appointments['appointment_time'] >= current_time]
        current_load = len(remaining_appointments)
        
        # Calculate average wait time for this doctor today
        if len(doctor_appointments) > 0:
            avg_wait_time = doctor_appointments['wait_time_minutes'].mean()
        else:
            avg_wait_time = 0
        
        # Calculate completed appointments
        completed_appointments = len(doctor_appointments) - current_load
        
        doctor_metrics.append({
            'doctor_id': doctor_id,
            'doctor_name': doctor['doctor_name'],
            'specialty': doctor['specialty'],
            'avg_consultation_time': doctor['avg_consultation_time'],
            'is_available': doctor['is_available'],
            'current_load': current_load,
            'completed_today': completed_appointments,
            'avg_wait_time': round(avg_wait_time, 1)
        })
    
    # Convert to DataFrame
    doctor_metrics_df = pd.DataFrame(doctor_metrics)
    
    # Sort doctors based on selection
    if sort_option == 'Name':
        doctor_metrics_df = doctor_metrics_df.sort_values('doctor_name')
    elif sort_option == 'Specialty':
        doctor_metrics_df = doctor_metrics_df.sort_values('specialty')
    elif sort_option == 'Current Load':
        doctor_metrics_df = doctor_metrics_df.sort_values('current_load', ascending=False)
    elif sort_option == 'Average Wait Time':
        doctor_metrics_df = doctor_metrics_df.sort_values('avg_wait_time', ascending=False)
    
    # Display doctor cards
    if not doctor_metrics_df.empty:
        # Create three columns for doctor cards
        cols = st.columns(3)
        
        for i, (_, doctor) in enumerate(doctor_metrics_df.iterrows()):
            with cols[i % 3]:
                # Create card-like display
                availability_color = "green" if doctor['is_available'] else "red"
                load_color = "green" if doctor['current_load'] <= 3 else "orange" if doctor['current_load'] <= 6 else "red"
                wait_color = "green" if doctor['avg_wait_time'] <= 15 else "orange" if doctor['avg_wait_time'] <= 30 else "red"
                
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:10px;">
                    <h3>{doctor['doctor_name']}</h3>
                    <p><b>Specialty:</b> {doctor['specialty']}</p>
                    <p><b>Status:</b> <span style="color:{availability_color};">{'Available' if doctor['is_available'] else 'Unavailable'}</span></p>
                    <p><b>Current Load:</b> <span style="color:{load_color};">{doctor['current_load']} patients</span></p>
                    <p><b>Avg. Consultation:</b> {doctor['avg_consultation_time']} minutes</p>
                    <p><b>Avg. Wait Time:</b> <span style="color:{wait_color};">{doctor['avg_wait_time']} minutes</span></p>
                    <p><b>Completed Today:</b> {doctor['completed_today']} appointments</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No doctors match the selected criteria.")
    
    # Section: Doctor Load Analysis
    st.subheader("Doctor Load Analysis")
    
    # Create visualization of current doctor load
    if not doctor_metrics_df.empty:
        # Sort by current load for the chart
        chart_data = doctor_metrics_df.sort_values('current_load', ascending=False)
        
        # Create horizontal bar chart
        fig = px.bar(
            chart_data,
            y='doctor_name',
            x='current_load',
            color='avg_wait_time',
            color_continuous_scale=['green', 'yellow', 'red'],
            labels={
                'doctor_name': 'Doctor',
                'current_load': 'Remaining Appointments Today',
                'avg_wait_time': 'Average Wait Time (min)'
            },
            title="Current Doctor Load",
            orientation='h'
        )
        
        # Add specialty as text
        fig.add_trace(
            go.Scatter(
                x=chart_data['current_load'],
                y=chart_data['doctor_name'],
                text=chart_data['specialty'],
                mode='text',
                textposition='top right',
                showlegend=False
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No doctor load data available.")
    
    # Section: Load Balancing Recommendations
    st.subheader("Load Balancing Recommendations")
    
    # Calculate load imbalance by specialty
    specialty_loads = {}
    load_balancing_recommendations = []
    
    for specialty in doctors_df['specialty'].unique():
        specialty_doctors = doctors_df[doctors_df['specialty'] == specialty]
        doctor_ids = specialty_doctors['doctor_id'].tolist()
        
        # Skip if only one doctor in this specialty
        if len(doctor_ids) <= 1:
            continue
        
        # Get appointment counts for each doctor in this specialty
        doctor_loads = []
        for doctor_id in doctor_ids:
            doctor_name = doctors_df[doctors_df['doctor_id'] == doctor_id]['doctor_name'].iloc[0]
            
            # Count remaining appointments
            remaining = len(today_appointments[
                (today_appointments['doctor_id'] == doctor_id) & 
                (today_appointments['appointment_time'] >= current_time)
            ])
            
            doctor_loads.append({
                'doctor_id': doctor_id,
                'doctor_name': doctor_name,
                'remaining_appointments': remaining
            })
        
        # Check for imbalance
        if doctor_loads:
            max_load = max(d['remaining_appointments'] for d in doctor_loads)
            min_load = min(d['remaining_appointments'] for d in doctor_loads)
            
            # If significant imbalance (more than 3 patients difference)
            if max_load - min_load >= 3:
                # Find busiest and least busy doctors
                busiest = max(doctor_loads, key=lambda x: x['remaining_appointments'])
                least_busy = min(doctor_loads, key=lambda x: x['remaining_appointments'])
                
                # Calculate suggested transfers (half the difference, rounded down)
                transfers = (busiest['remaining_appointments'] - least_busy['remaining_appointments']) // 2
                
                if transfers > 0:
                    load_balancing_recommendations.append({
                        'specialty': specialty,
                        'from_doctor': busiest['doctor_name'],
                        'to_doctor': least_busy['doctor_name'],
                        'suggested_transfers': transfers,
                        'imbalance': max_load - min_load
                    })
    
    # Display load balancing recommendations
    if load_balancing_recommendations:
        # Sort by imbalance (descending)
        load_balancing_recommendations.sort(key=lambda x: x['imbalance'], reverse=True)
        
        for i, rec in enumerate(load_balancing_recommendations):
            st.markdown(f"""
            <div style="background-color:#f0f2f6; padding:10px; border-radius:5px; margin-bottom:10px;">
                <h4>Recommendation {i+1}: {rec['specialty']} Load Balancing</h4>
                <p>Transfer <b>{rec['suggested_transfers']} patients</b> from <b>Dr. {rec['from_doctor']}</b> to <b>Dr. {rec['to_doctor']}</b></p>
                <p>Current imbalance: <b>{rec['imbalance']} patients</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"Apply Recommendation #{i+1}", key=f"apply_rec_{i}"):
                    st.success(f"Recommendation applied. {rec['suggested_transfers']} patients will be transferred from Dr. {rec['from_doctor']} to Dr. {rec['to_doctor']}.")
            
            with col2:
                if st.button(f"Dismiss #{i+1}", key=f"dismiss_rec_{i}"):
                    st.info(f"Recommendation dismissed.")
    else:
        st.info("No load balancing recommendations at this time. Doctor workload appears balanced.")
    
    # Section: Schedule Optimization
    st.subheader("Schedule Optimization")
    
    # Get optimal slots from the schedule optimizer
    schedule_optimizer = st.session_state.schedule_optimizer
    optimal_slots = schedule_optimizer.calculate_optimal_slots(
        current_datetime,
        appointments_df,
        doctors_df
    )
    
    # Filter to just show today's slots
    if not optimal_slots.empty:
        today_slots = optimal_slots[optimal_slots['date'] == current_date]
        
        if not today_slots.empty:
            # Display optimal slots
            st.markdown("### Recommended Optimal Slots for Today")
            
            # Display at most 10 slots
            for i, (_, slot) in enumerate(today_slots.head(10).iterrows()):
                peak_indicator = "🔥 Peak hour" if slot['is_peak_hour'] else "⌛ Regular hour"
                
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:8px; border-radius:5px; margin-bottom:5px; display:flex; justify-content:space-between;">
                    <div>
                        <b>{slot['time']}</b> - Dr. {slot['doctor_name']} ({slot['specialty']})
                    </div>
                    <div>
                        {peak_indicator} | {slot['expected_duration']} min
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if len(today_slots) > 10:
                st.info(f"{len(today_slots) - 10} more slots available.")
        else:
            st.info("No optimal slots available for today.")
    else:
        st.info("No optimal slot data available.")
    
    # Doctor availability management
    st.subheader("Doctor Availability Management")
    
    # Create a form for updating doctor availability
    with st.form("doctor_availability_form"):
        st.markdown("### Update Doctor Availability")
        
        # Select doctor
        doctor_id = st.selectbox(
            "Select Doctor",
            options=doctors_df['doctor_id'].tolist(),
            format_func=lambda x: f"Dr. {doctors_df[doctors_df['doctor_id'] == x]['doctor_name'].iloc[0]} ({doctors_df[doctors_df['doctor_id'] == x]['specialty'].iloc[0]})"
        )
        
        # Current availability status
        current_status = doctors_df[doctors_df['doctor_id'] == doctor_id]['is_available'].iloc[0]
        
        # New availability status
        new_status = st.checkbox("Available", value=current_status)
        
        # Reason for change
        reason = st.text_area("Reason for Status Change (if any)")
        
        # Submit button
        submitted = st.form_submit_button("Update Availability")
        
        if submitted:
            st.success(f"Availability updated for Dr. {doctors_df[doctors_df['doctor_id'] == doctor_id]['doctor_name'].iloc[0]}")
