import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import random

# Add paths to import custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_appointment_booking():
    """Display the appointment booking interface."""
    st.title("Appointment Booking")
    
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
    
    # Date selection
    st.subheader("Select Appointment Date")
    
    # Get available dates from the data (start from current date onwards)
    available_dates = sorted(appointments_df['appointment_date'].unique())
    
    # Filter for dates that are current or future
    future_dates = [date for date in available_dates if date >= current_datetime.date()]
    
    if not future_dates:
        # If no future dates available, show all dates for demo purposes
        future_dates = available_dates
    
    # Show calendar for date selection
    selected_date = st.date_input(
        "Appointment Date",
        value=future_dates[0] if future_dates else available_dates[0],
        min_value=min(available_dates),
        max_value=max(available_dates)
    )
    
    # Doctor selection
    st.subheader("Select Doctor")
    
    # Filter by specialty
    specialties = sorted(doctors_df['specialty'].unique().tolist())
    selected_specialty = st.selectbox(
        "Specialty",
        options=specialties
    )
    
    # Filter doctors by selected specialty
    specialty_doctors = doctors_df[doctors_df['specialty'] == selected_specialty]
    
    if specialty_doctors.empty:
        st.warning(f"No doctors available for {selected_specialty}. Please select another specialty.")
        return
    
    # Create doctor selection with available status
    doctor_options = []
    for _, doctor in specialty_doctors.iterrows():
        available_status = "✅ Available" if doctor['is_available'] else "❌ Unavailable"
        doctor_options.append(f"Dr. {doctor['doctor_name']} ({available_status})")
    
    selected_doctor_option = st.selectbox(
        "Doctor",
        options=doctor_options
    )
    
    # Extract doctor name from the selected option
    selected_doctor_name = selected_doctor_option.split(" (")[0].replace("Dr. ", "")
    
    # Get doctor ID
    selected_doctor = doctors_df[doctors_df['doctor_name'] == selected_doctor_name].iloc[0]
    selected_doctor_id = selected_doctor['doctor_id']
    
    # Check if doctor is available
    is_available = selected_doctor['is_available']
    if not is_available:
        st.warning(f"Dr. {selected_doctor_name} is currently marked as unavailable. You can still book an appointment, but it may be subject to rescheduling.")
    
    # Show doctor details
    st.markdown(f"""
    **Selected Doctor:** Dr. {selected_doctor_name}  
    **Specialty:** {selected_specialty}  
    **Average Consultation Time:** {selected_doctor['avg_consultation_time']} minutes
    """)
    
    # Time slot selection
    st.subheader("Select Time Slot")
    
    # Get existing appointments for this doctor on the selected date
    doctor_appointments = appointments_df[
        (appointments_df['doctor_id'] == selected_doctor_id) & 
        (appointments_df['appointment_date'] == selected_date)
    ]
    
    # Create time slots (from 9 AM to 7 PM, in 30-minute intervals)
    slot_times = []
    current_time = time(9, 0)  # 9 AM
    end_time = time(19, 0)  # 7 PM
    
    while current_time < end_time:
        slot_times.append(current_time)
        # Add 30 minutes
        hour = current_time.hour
        minute = current_time.minute + 30
        if minute >= 60:
            hour += 1
            minute -= 60
        current_time = time(hour, minute)
    
    # Mark slots as available or booked
    available_slots = []
    for slot in slot_times:
        # Check if this slot overlaps with any existing appointment
        slot_datetime = datetime.combine(selected_date, slot)
        
        # Consider appointment duration (default to 30 minutes if not specified)
        appointment_duration = selected_doctor['avg_consultation_time']
        
        # Check if slot is booked
        is_booked = False
        for _, appt in doctor_appointments.iterrows():
            appt_time = appt['appointment_time']
            appt_datetime = datetime.combine(selected_date, appt_time)
            
            # If the slot starts during an existing appointment
            if (appt_datetime <= slot_datetime < appt_datetime + timedelta(minutes=appointment_duration)):
                is_booked = True
                break
            
            # If the slot would run into an existing appointment
            if (slot_datetime <= appt_datetime < slot_datetime + timedelta(minutes=appointment_duration)):
                is_booked = True
                break
        
        # Add slot with availability info
        slot_str = slot.strftime("%I:%M %p")
        if is_booked:
            available_slots.append(f"{slot_str} (Booked)")
        else:
            available_slots.append(f"{slot_str} (Available)")
    
    # Show time slot selection
    selected_slot = st.selectbox(
        "Available Time Slots",
        options=available_slots
    )
    
    # Check if selected slot is available
    if "Booked" in selected_slot:
        st.error("This slot is already booked. Please select another time slot.")
        can_book = False
    else:
        can_book = True
    
    # Extract time from selected slot
    selected_time_str = selected_slot.split(" (")[0]
    selected_time = datetime.strptime(selected_time_str, "%I:%M %p").time()
    
    # Calculate estimated wait time based on time of day
    hour = selected_time.hour
    if 17 <= hour < 20:  # 5-8 PM (peak hours)
        estimated_wait = f"{random.randint(20, 40)} minutes"
        peak_warning = """
        ⚠️ **Peak Hour Alert:** You've selected a time during our peak hours (5-8 PM).
        Wait times are typically longer during these hours.
        """
        st.warning(peak_warning)
    else:
        estimated_wait = f"{random.randint(5, 20)} minutes"
    
    # Show appointment summary
    st.subheader("Appointment Summary")
    
    # Create columns for patient information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Patient Information")
        patient_name = st.text_input("Full Name")
        patient_id = st.text_input("Patient ID (if existing)")
        patient_phone = st.text_input("Phone Number")
    
    with col2:
        st.markdown("### Appointment Details")
        st.markdown(f"**Date:** {selected_date.strftime('%A, %B %d, %Y')}")
        st.markdown(f"**Time:** {selected_time_str}")
        st.markdown(f"**Doctor:** Dr. {selected_doctor_name}")
        st.markdown(f"**Specialty:** {selected_specialty}")
        st.markdown(f"**Estimated Wait Time:** {estimated_wait}")
    
    # Reason for visit
    st.markdown("### Reason for Visit")
    visit_reason = st.text_area("Please describe the reason for your visit")
    
    # Early arrival option
    st.markdown("### Early Arrival")
    early_arrival = st.checkbox("I plan to arrive 15-30 minutes before my appointment time")
    
    if early_arrival:
        st.info("""
        ℹ️ Thank you for letting us know you plan to arrive early.
        
        During non-peak hours, we'll try to accommodate early arrivals when possible.
        However, during peak hours (5-8 PM), patients will generally be seen according to their scheduled time.
        """)
    
    # Submit button
    if st.button("Book Appointment", disabled=not can_book or not patient_name or not patient_phone):
        # Calculate new appointment ID
        new_appointment_id = appointments_df['appointment_id'].max() + 1 if not appointments_df.empty else 1
        
        # Generate patient ID if not provided
        if not patient_id:
            patient_id = f"P{random.randint(1000, 9999)}"
        
        # Create new appointment entry
        # In a real system, this would be saved to a database
        st.success(f"""
        ✅ Appointment successfully booked!
        
        **Appointment ID:** {new_appointment_id}
        **Patient:** {patient_name} ({patient_id})
        **Date & Time:** {selected_date.strftime('%A, %B %d, %Y')} at {selected_time_str}
        **Doctor:** Dr. {selected_doctor_name} ({selected_specialty})
        
        Please arrive 10-15 minutes before your appointment time for check-in.
        A confirmation SMS will be sent to {patient_phone}.
        """)
        
        # Show wait time reduction tips
        st.info("""
        **Tips to Reduce Your Wait Time:**
        
        1. Arrive 10-15 minutes early to complete any paperwork
        2. Have your insurance and ID ready at check-in
        3. Prepare a list of your current medications
        4. Write down specific questions for the doctor
        """)
    
    # Display appointment policies
    with st.expander("Appointment Policies"):
        st.markdown("""
        ### Cancellation Policy
        Please provide at least 24 hours notice if you need to cancel or reschedule your appointment.
        
        ### Late Arrival Policy
        If you arrive more than 15 minutes late for your appointment, you may be asked to reschedule.
        
        ### Early Arrival Policy
        While we appreciate patients arriving early, please note that during peak hours (5-8 PM),
        patients will generally be seen according to their scheduled appointment time.
        """)

if __name__ == "__main__":
    # This allows the module to be run directly
    show_appointment_booking()