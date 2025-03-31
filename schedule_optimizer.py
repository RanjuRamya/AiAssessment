import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ScheduleOptimizer:
    """
    AI-powered scheduler that optimizes appointment slots based on 
    predicted wait times and doctor availability.
    """
    
    def __init__(self):
        self.optimization_window_days = 7  # How many days ahead to optimize
        self.peak_start_hour = 17  # 5 PM
        self.peak_end_hour = 20    # 8 PM
    
    def calculate_optimal_slots(self, current_datetime, appointments_df, doctors_df):
        """
        Calculate optimal appointment slots based on historical data and current load.
        
        Parameters:
        -----------
        current_datetime : datetime
            Current date and time
        appointments_df : pandas.DataFrame
            DataFrame of all appointments
        doctors_df : pandas.DataFrame
            DataFrame of all doctors
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame of optimized available slots
        """
        if appointments_df.empty or doctors_df.empty:
            return pd.DataFrame()
            
        # Consider scheduling window (current date + next 7 days)
        start_date = current_datetime.date()
        end_date = start_date + timedelta(days=self.optimization_window_days)
        
        # Filter doctors who are available
        available_doctors = doctors_df[doctors_df['is_available'] == True].copy()
        
        if available_doctors.empty:
            return pd.DataFrame()
        
        # Define working hours (9 AM to 8 PM)
        working_hours = list(range(9, 21))
        
        # Create empty list to store slots
        optimal_slots = []
        
        # For each doctor and each day in the scheduling window
        for _, doctor in available_doctors.iterrows():
            consultation_time = doctor['avg_consultation_time']
            
            # Calculate slots per hour based on consultation time
            slots_per_hour = max(1, int(60 / consultation_time))
            
            for day_offset in range(self.optimization_window_days):
                slot_date = start_date + timedelta(days=day_offset)
                day_of_week = slot_date.weekday()
                
                # Skip if it's a weekend (Assuming 5 and 6 are weekend days)
                if day_of_week >= 5:
                    continue
                
                # Get existing appointments for this doctor on this day
                existing_appointments = appointments_df[
                    (appointments_df['doctor_id'] == doctor['doctor_id']) & 
                    (appointments_df['appointment_date'] == slot_date)
                ]
                
                # Calculate busy hours based on existing appointments
                busy_hours = {}
                for _, appt in existing_appointments.iterrows():
                    hour = appt['appointment_time'].hour
                    if hour in busy_hours:
                        busy_hours[hour] += 1
                    else:
                        busy_hours[hour] = 1
                
                # Generate optimal slots
                for hour in working_hours:
                    # Skip fully booked hours
                    current_bookings = busy_hours.get(hour, 0)
                    if current_bookings >= slots_per_hour:
                        continue
                    
                    remaining_slots = slots_per_hour - current_bookings
                    
                    # Determine slot priority based on peak hours
                    # During peak hours (5PM-8PM), prioritize specialists with shorter consultation times
                    is_peak_hour = (hour >= self.peak_start_hour and hour < self.peak_end_hour)
                    
                    # Calculate base priority
                    if is_peak_hour:
                        priority = 100 - consultation_time  # Higher priority for shorter consultations
                    else:
                        priority = 50  # Normal priority for non-peak hours
                        
                    # If doctor has high backlog, reduce priority
                    backlog_factor = self.calculate_doctor_backlog(doctor['doctor_id'], 
                                                                 current_datetime, 
                                                                 appointments_df)
                    priority -= backlog_factor * 10
                    
                    # Add each remaining slot
                    for slot_index in range(remaining_slots):
                        # Calculate minutes offset within the hour
                        minutes_offset = (60 // slots_per_hour) * slot_index
                        
                        slot_time = f"{hour:02d}:{minutes_offset:02d}"
                        
                        optimal_slots.append({
                            'doctor_id': doctor['doctor_id'],
                            'doctor_name': doctor['doctor_name'],
                            'specialty': doctor['specialty'],
                            'date': slot_date,
                            'time': slot_time,
                            'expected_duration': consultation_time,
                            'priority': priority,
                            'is_peak_hour': is_peak_hour
                        })
        
        # Convert to DataFrame and sort by priority
        if optimal_slots:
            slots_df = pd.DataFrame(optimal_slots)
            return slots_df.sort_values('priority', ascending=False)
        else:
            return pd.DataFrame()
    
    def calculate_doctor_backlog(self, doctor_id, current_datetime, appointments_df):
        """
        Calculate how backed up a doctor is based on their current appointment load.
        
        Parameters:
        -----------
        doctor_id : int
            Doctor's ID
        current_datetime : datetime
            Current date and time reference
        appointments_df : pandas.DataFrame
            DataFrame of all appointments
            
        Returns:
        --------
        float
            Backlog factor (0-5 scale, higher means more backlog)
        """
        # Filter to get today's appointments for this doctor
        today = current_datetime.date()
        doctor_appointments = appointments_df[
            (appointments_df['doctor_id'] == doctor_id) & 
            (appointments_df['appointment_date'] == today)
        ]
        
        if doctor_appointments.empty:
            return 0
        
        # Count remaining appointments for today
        current_time = current_datetime.time()
        remaining_appointments = doctor_appointments[
            doctor_appointments['appointment_time'] >= current_time
        ]
        
        # Calculate backlog factor (0-5 scale)
        remaining_count = len(remaining_appointments)
        if remaining_count <= 2:
            return 0
        elif remaining_count <= 5:
            return 1
        elif remaining_count <= 8:
            return 2
        elif remaining_count <= 12:
            return 3
        elif remaining_count <= 15:
            return 4
        else:
            return 5
    
    def get_recommendations(self, current_datetime, appointments_df, doctors_df):
        """
        Generate AI recommendations for optimizing patient flow.
        
        Parameters:
        -----------
        current_datetime : datetime
            Current date and time
        appointments_df : pandas.DataFrame
            DataFrame of all appointments
        doctors_df : pandas.DataFrame
            DataFrame of all doctors
            
        Returns:
        --------
        list
            List of recommendation strings
        """
        recommendations = []
        
        if appointments_df.empty or doctors_df.empty:
            return ["Insufficient data to generate recommendations."]
        
        # 1. Identify overbooked doctors
        today = current_datetime.date()
        
        # Get today's appointments
        today_appointments = appointments_df[
            appointments_df['appointment_date'] == today
        ]
        
        if today_appointments.empty:
            recommendations.append("No appointments scheduled for today.")
            return recommendations
        
        # Count appointments by doctor
        doctor_appointment_counts = today_appointments['doctor_id'].value_counts()
        
        # Check which doctors have high appointment counts
        for doctor_id, count in doctor_appointment_counts.items():
            doctor_info = doctors_df[doctors_df['doctor_id'] == doctor_id].iloc[0]
            avg_time = doctor_info['avg_consultation_time']
            
            # Calculate theoretical max patients per day
            working_hours = 9  # 9 hours (9 AM - 6 PM)
            theoretical_max = (working_hours * 60) / avg_time
            
            # If doctor is overbooked
            if count > theoretical_max * 0.85:  # 85% of theoretical maximum
                rec = (f"Dr. {doctor_info['doctor_name']} ({doctor_info['specialty']}) has {count} appointments today, "
                       f"which may lead to delays. Consider redistributing patients to other {doctor_info['specialty']} doctors.")
                recommendations.append(rec)
        
        # 2. Check for peak hour congestion
        current_hour = current_datetime.hour
        
        # If current time is during peak hours
        if self.peak_start_hour <= current_hour < self.peak_end_hour:
            # Count upcoming appointments in the next 2 hours
            next_2_hours = current_datetime + timedelta(hours=2)
            upcoming_appointments = appointments_df[
                (appointments_df['appointment_date'] == today) &
                (appointments_df['appointment_time'] >= current_datetime.time()) &
                (appointments_df['appointment_time'] < next_2_hours.time())
            ]
            
            upcoming_count = len(upcoming_appointments)
            
            if upcoming_count > 30:  # Arbitrary threshold for high load
                rec = (f"High congestion detected: {upcoming_count} patients scheduled in the next 2 hours. "
                       f"Consider sending SMS notifications about potential delays.")
                recommendations.append(rec)
        
        # 3. Check for underutilized specialists
        for _, doctor in doctors_df.iterrows():
            doctor_id = doctor['doctor_id']
            doctor_appointments = today_appointments[today_appointments['doctor_id'] == doctor_id]
            
            # If doctor has few appointments and is available
            if len(doctor_appointments) < 5 and doctor['is_available']:
                rec = (f"Dr. {doctor['doctor_name']} ({doctor['specialty']}) has only {len(doctor_appointments)} appointments today. "
                       f"Consider rescheduling patients from busier doctors with the same specialty.")
                recommendations.append(rec)
        
        # 4. Check for early arrival patterns
        if not today_appointments.empty and 'arrived_early' in today_appointments.columns:
            early_arrivals = today_appointments[today_appointments['arrived_early'] == True]
            early_arrival_percentage = (len(early_arrivals) / len(today_appointments)) * 100
            
            if early_arrival_percentage > 40:  # If over 40% arrive early
                rec = (f"{early_arrival_percentage:.1f}% of patients today arrived early. "
                       f"Consider adjusting scheduled times by 15 minutes to account for this pattern.")
                recommendations.append(rec)
        
        # 5. Recommend load balancing if appropriate
        specialties = doctors_df['specialty'].unique()
        for specialty in specialties:
            specialty_doctors = doctors_df[doctors_df['specialty'] == specialty]
            if len(specialty_doctors) > 1:  # Only if there are multiple doctors of this specialty
                specialty_appointments = today_appointments.merge(
                    doctors_df[['doctor_id', 'specialty']], 
                    on='doctor_id', 
                    how='inner'
                )
                specialty_appointments = specialty_appointments[specialty_appointments['specialty'] == specialty]
                
                if not specialty_appointments.empty:
                    appointments_per_doctor = specialty_appointments['doctor_id'].value_counts()
                    max_appointments = appointments_per_doctor.max()
                    min_appointments = appointments_per_doctor.min()
                    
                    # If there's a significant imbalance
                    if max_appointments > 2 * min_appointments:
                        rec = (f"Significant load imbalance detected among {specialty} doctors. "
                               f"Consider redistributing patients more evenly.")
                        recommendations.append(rec)
        
        # Limit to top recommendations if there are many
        if len(recommendations) > 5:
            return recommendations[:5]
        elif len(recommendations) == 0:
            return ["No optimization recommendations needed at this time. Patient flow appears to be balanced."]
        
        return recommendations
