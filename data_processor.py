import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from random import randint, choice, random, seed
import string

class DataProcessor:
    """
    Handles data loading, processing, and generation of insights for the clinic management system.
    """
    
    def __init__(self):
        """Initialize data processor with required data structures."""
        # Set seed for reproducibility
        seed(42)
        
        self.appointment_data_path = 'data/sample_appointment_data.csv'
        self.doctor_data_path = 'data/sample_doctor_data.csv'
        
        # Generate sample data if not available
        self.generate_sample_data_if_needed()
    
    def generate_sample_data_if_needed(self):
        """Generate sample data files if they don't exist."""
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Generate doctor data if needed
        if not os.path.exists(self.doctor_data_path):
            self.generate_doctor_data()
            
        # Generate appointment data if needed
        if not os.path.exists(self.appointment_data_path):
            self.generate_appointment_data()
    
    def generate_doctor_data(self):
        """Generate sample doctor data for demonstration."""
        # Define specialties and their typical consultation times
        specialties = {
            'Cardiology': (15, 22),
            'Dermatology': (10, 18),
            'Orthopedics': (12, 20),
            'Pediatrics': (8, 15),
            'Gynecology': (15, 20),
            'Internal Medicine': (10, 18),
            'ENT': (8, 15),
            'Ophthalmology': (10, 15),
            'Neurology': (15, 22),
            'Psychiatry': (20, 30)
        }
        
        # First names and last names for generating doctor names
        first_names = ['Aditya', 'Ravi', 'Priya', 'Neha', 'Sanjay', 'Meera', 'Vikram', 
                      'Ananya', 'Rahul', 'Deepa', 'Arjun', 'Kavita', 'Rajesh', 'Sunita', 'Amit']
        
        last_names = ['Sharma', 'Patel', 'Reddy', 'Singh', 'Kumar', 'Rao', 'Joshi', 
                     'Malhotra', 'Gupta', 'Nair', 'Iyer', 'Menon', 'Das', 'Pillai', 'Desai']
        
        # Create 15 doctors
        doctors = []
        for i in range(1, 16):
            specialty = list(specialties.keys())[i % len(specialties)]
            min_time, max_time = specialties[specialty]
            
            doctors.append({
                'doctor_id': i,
                'doctor_name': f"{choice(first_names)} {choice(last_names)}",
                'specialty': specialty,
                'avg_consultation_time': randint(min_time, max_time),
                'doctor_experience': randint(1, 25),
                'is_available': True
            })
        
        # Create DataFrame and save to CSV
        doctors_df = pd.DataFrame(doctors)
        doctors_df.to_csv(self.doctor_data_path, index=False)
    
    def generate_appointment_data(self):
        """Generate sample appointment data for demonstration."""
        # Load doctor data first
        doctors_df = pd.read_csv(self.doctor_data_path)
        
        # Generate 3 months of appointment data (90 days)
        start_date = datetime.now().date() - timedelta(days=60)  # 60 days in the past
        end_date = start_date + timedelta(days=120)  # 60 days into the future
        
        appointments = []
        appointment_id = 1
        
        # For each day in the range
        current_date = start_date
        while current_date < end_date:
            # Skip appointments for weekends
            if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                current_date += timedelta(days=1)
                continue
            
            # Each doctor gets several appointments per day
            for _, doctor in doctors_df.iterrows():
                doctor_id = doctor['doctor_id']
                
                # Determine number of appointments (more on certain days)
                base_appointments = randint(5, 15)
                
                # More appointments in the evening (peak hours)
                morning_appointments = int(base_appointments * 0.4)  # 40% in morning
                evening_appointments = int(base_appointments * 0.6)  # 60% in evening
                
                # Generate morning appointments (9 AM - 1 PM)
                for _ in range(morning_appointments):
                    hour = randint(9, 13)
                    minute = choice([0, 15, 30, 45])
                    
                    # Generate early arrival pattern
                    arrived_early = random() < 0.3  # 30% chance of early arrival
                    
                    # Generate wait time (correlated with time of day and doctor's consult time)
                    base_wait = randint(5, 15)
                    
                    # Peak hour adjustment - more waiting during busy hours
                    if 17 <= hour <= 19:  # 5PM-7PM
                        peak_factor = 2.0
                    elif hour >= 14:  # Afternoon
                        peak_factor = 1.5
                    else:  # Morning
                        peak_factor = 1.0
                    
                    # Wait time calculation
                    wait_time = int(base_wait * peak_factor * (1 + doctor['avg_consultation_time']/20))
                    
                    # Add some randomness
                    wait_time = max(0, wait_time + randint(-5, 10))
                    
                    appointments.append({
                        'appointment_id': appointment_id,
                        'doctor_id': doctor_id,
                        'patient_id': f"P{randint(1000, 9999)}",
                        'appointment_date': current_date,
                        'appointment_time': f"{hour:02d}:{minute:02d}",
                        'hour_of_day': hour,
                        'day_of_week': current_date.weekday(),
                        'scheduled_patients_count': base_appointments,
                        'arrived_early': arrived_early,
                        'wait_time_minutes': wait_time,
                        'status': 'completed' if current_date < datetime.now().date() else 'scheduled'
                    })
                    
                    appointment_id += 1
                
                # Generate evening appointments (2 PM - 8 PM)
                for _ in range(evening_appointments):
                    hour = randint(14, 20)
                    minute = choice([0, 15, 30, 45])
                    
                    # Generate early arrival pattern
                    arrived_early = random() < 0.5  # 50% chance of early arrival during evening
                    
                    # Generate wait time (correlated with time of day and doctor's consult time)
                    base_wait = randint(10, 25)
                    
                    # Peak hour adjustment - more waiting during busy hours
                    if 17 <= hour <= 19:  # 5PM-7PM
                        peak_factor = 2.5
                    elif hour >= 14:  # Afternoon
                        peak_factor = 1.8
                    else:  # Morning
                        peak_factor = 1.0
                    
                    # Wait time calculation
                    wait_time = int(base_wait * peak_factor * (1 + doctor['avg_consultation_time']/20))
                    
                    # Add some randomness
                    wait_time = max(0, wait_time + randint(-5, 15))
                    
                    appointments.append({
                        'appointment_id': appointment_id,
                        'doctor_id': doctor_id,
                        'patient_id': f"P{randint(1000, 9999)}",
                        'appointment_date': current_date,
                        'appointment_time': f"{hour:02d}:{minute:02d}",
                        'hour_of_day': hour,
                        'day_of_week': current_date.weekday(),
                        'scheduled_patients_count': base_appointments,
                        'arrived_early': arrived_early,
                        'wait_time_minutes': wait_time,
                        'status': 'completed' if current_date < datetime.now().date() else 'scheduled'
                    })
                    
                    appointment_id += 1
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Create DataFrame and save to CSV
        appointments_df = pd.DataFrame(appointments)
        
        # Convert date and time columns to appropriate formats
        appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date']).dt.date
        
        # Convert appointment_time from string to time for proper sorting
        appointments_df['appointment_time'] = pd.to_datetime(appointments_df['appointment_time'], format='%H:%M').dt.time
        
        appointments_df.to_csv(self.appointment_data_path, index=False)
    
    def load_appointment_data(self):
        """
        Load appointment data from CSV.
        
        Returns:
        --------
        pandas.DataFrame
            DataFrame containing appointment information
        """
        try:
            # Read the CSV file
            df = pd.read_csv(self.appointment_data_path)
            
            # Convert date and time columns to appropriate formats
            df['appointment_date'] = pd.to_datetime(df['appointment_date']).dt.date
            df['appointment_time'] = pd.to_datetime(df['appointment_time'], format='%H:%M').dt.time
            
            return df
        except Exception as e:
            print(f"Error loading appointment data: {e}")
            return pd.DataFrame()
    
    def load_doctor_data(self):
        """
        Load doctor data from CSV.
        
        Returns:
        --------
        pandas.DataFrame
            DataFrame containing doctor information
        """
        try:
            return pd.read_csv(self.doctor_data_path)
        except Exception as e:
            print(f"Error loading doctor data: {e}")
            return pd.DataFrame()
    
    def get_summary_metrics(self, current_datetime):
        """
        Calculate summary metrics for the dashboard.
        
        Parameters:
        -----------
        current_datetime : datetime
            Current date and time
            
        Returns:
        --------
        dict
            Dictionary of summary metrics
        """
        # Load data if not already loaded
        appointments_df = self.load_appointment_data()
        doctors_df = self.load_doctor_data()
        
        # Get current date and time
        current_date = current_datetime.date()
        current_time = current_datetime.time()
        
        # Initialize metrics
        metrics = {
            'avg_wait_time': 0,
            'wait_time_delta': 0,
            'patients_in_queue': 0,
            'queue_delta': 0,
            'available_doctors': 0,
            'total_doctors': len(doctors_df),
            'total_appointments': 0,
            'completed_appointments': 0
        }
        
        if appointments_df.empty or doctors_df.empty:
            return metrics
        
        # Filter today's appointments
        today_appointments = appointments_df[appointments_df['appointment_date'] == current_date]
        
        if today_appointments.empty:
            return metrics
        
        # Calculate total appointments for today
        metrics['total_appointments'] = len(today_appointments)
        
        # Calculate completed appointments (before current time)
        completed = today_appointments[today_appointments['appointment_time'] < current_time]
        metrics['completed_appointments'] = len(completed)
        
        # Calculate patients in queue (after current time)
        current_queue = today_appointments[today_appointments['appointment_time'] >= current_time]
        metrics['patients_in_queue'] = len(current_queue)
        
        # Calculate queue delta (compared to same time yesterday)
        yesterday = current_date - timedelta(days=1)
        yesterday_queue = appointments_df[
            (appointments_df['appointment_date'] == yesterday) & 
            (appointments_df['appointment_time'] >= current_time)
        ]
        metrics['queue_delta'] = metrics['patients_in_queue'] - len(yesterday_queue)
        
        # Calculate average wait time for past hour (simulation)
        past_hour_start = (datetime.combine(current_date, current_time) - timedelta(hours=1)).time()
        past_hour_appointments = today_appointments[
            (today_appointments['appointment_time'] >= past_hour_start) & 
            (today_appointments['appointment_time'] < current_time)
        ]
        
        if len(past_hour_appointments) > 0:
            metrics['avg_wait_time'] = int(past_hour_appointments['wait_time_minutes'].mean())
        else:
            # If no recent appointments, use average of the day
            if len(completed) > 0:
                metrics['avg_wait_time'] = int(completed['wait_time_minutes'].mean())
            else:
                # Default value
                metrics['avg_wait_time'] = 25 if current_time.hour >= 17 else 15
        
        # Calculate wait time delta (compared to same time yesterday)
        yesterday_past_hour = appointments_df[
            (appointments_df['appointment_date'] == yesterday) & 
            (appointments_df['appointment_time'] >= past_hour_start) & 
            (appointments_df['appointment_time'] < current_time)
        ]
        
        if len(yesterday_past_hour) > 0:
            yesterday_avg_wait = int(yesterday_past_hour['wait_time_minutes'].mean())
            metrics['wait_time_delta'] = metrics['avg_wait_time'] - yesterday_avg_wait
        
        # Calculate available doctors
        # In a real system, this would come from a status tracker
        # For simulation, we'll say all doctors are available
        metrics['available_doctors'] = metrics['total_doctors']
        
        return metrics
    
    def get_wait_time_predictions(self, current_datetime):
        """
        Generate wait time predictions for the next few hours.
        
        Parameters:
        -----------
        current_datetime : datetime
            Current date and time
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame with hour and predicted wait times
        """
        # Get current hour
        current_hour = current_datetime.hour
        
        # Create prediction hours (current hour + next 5 hours)
        prediction_hours = [h for h in range(current_hour, current_hour + 6) if h < 21]
        
        # Generate wait time predictions
        # In a real system, this would use machine learning models
        # For simulation, we'll use a predefined pattern
        predictions = []
        
        for hour in prediction_hours:
            # Base wait time depends on hour
            if 17 <= hour <= 19:  # Peak hours
                base_wait = 35
            elif 14 <= hour < 17 or hour > 19:  # Afternoon/Evening
                base_wait = 25
            else:  # Morning
                base_wait = 15
            
            # Add some variation
            predicted_wait = max(5, int(base_wait + randint(-5, 10)))
            
            predictions.append({
                'hour': hour,
                'hour_label': f"{hour}:00",
                'predicted_wait_time': predicted_wait
            })
        
        return pd.DataFrame(predictions)
    
    def get_patient_flow_data(self, current_date):
        """
        Get patient flow data by hour for the current date.
        
        Parameters:
        -----------
        current_date : date
            Current date
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame with hourly patient counts
        """
        # Load appointment data
        appointments_df = self.load_appointment_data()
        
        if appointments_df.empty:
            # Return empty dataframe with proper columns
            return pd.DataFrame(columns=['hour', 'hour_label', 'patient_count'])
        
        # Filter appointments for the current date
        today_appointments = appointments_df[appointments_df['appointment_date'] == current_date]
        
        if today_appointments.empty:
            # Return empty dataframe with proper columns
            return pd.DataFrame(columns=['hour', 'hour_label', 'patient_count'])
        
        # Count appointments by hour
        hour_counts = today_appointments['hour_of_day'].value_counts().reset_index()
        hour_counts.columns = ['hour', 'patient_count']
        hour_counts = hour_counts.sort_values('hour')
        
        # Add hour label
        hour_counts['hour_label'] = hour_counts['hour'].apply(lambda x: f"{x}:00")
        
        # Ensure all working hours are represented (9 AM to 8 PM)
        all_hours = pd.DataFrame({'hour': range(9, 21)})
        all_hours['hour_label'] = all_hours['hour'].apply(lambda x: f"{x}:00")
        
        # Merge with hour counts
        result = all_hours.merge(hour_counts, on=['hour', 'hour_label'], how='left')
        result['patient_count'] = result['patient_count'].fillna(0).astype(int)
        
        return result
    
    def get_specialty_queue_data(self, current_datetime):
        """
        Get current queue data by specialty.
        
        Parameters:
        -----------
        current_datetime : datetime
            Current date and time
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame with specialty queue information
        """
        # Load data
        appointments_df = self.load_appointment_data()
        doctors_df = self.load_doctor_data()
        
        if appointments_df.empty or doctors_df.empty:
            return pd.DataFrame(columns=['specialty', 'patients_waiting', 'avg_wait_time'])
        
        # Get current date and time
        current_date = current_datetime.date()
        current_time = current_datetime.time()
        
        # Filter upcoming appointments
        upcoming_appointments = appointments_df[
            (appointments_df['appointment_date'] == current_date) & 
            (appointments_df['appointment_time'] >= current_time)
        ]
        
        if upcoming_appointments.empty:
            return pd.DataFrame(columns=['specialty', 'patients_waiting', 'avg_wait_time'])
        
        # Merge with doctor data to get specialties
        merged_data = upcoming_appointments.merge(
            doctors_df[['doctor_id', 'specialty']], 
            on='doctor_id',
            how='inner'
        )
        
        # Group by specialty
        specialty_data = merged_data.groupby('specialty').agg(
            patients_waiting=('appointment_id', 'count'),
            avg_wait_time=('wait_time_minutes', 'mean')
        ).reset_index()
        
        # Round average wait time
        specialty_data['avg_wait_time'] = specialty_data['avg_wait_time'].round().astype(int)
        
        return specialty_data
    
    def create_specialty_chart(self, specialty_data):
        """
        Create a bar chart of queue status by specialty.
        
        Parameters:
        -----------
        specialty_data : pandas.DataFrame
            DataFrame with specialty queue information
            
        Returns:
        --------
        plotly.graph_objects.Figure
            Plotly figure with the chart
        """
        if specialty_data.empty:
            # Create empty figure
            fig = go.Figure()
            fig.update_layout(
                title="No queue data available",
                xaxis_title="Specialty",
                yaxis_title="Patients Waiting",
                height=400
            )
            return fig
        
        # Sort by patients waiting (descending)
        specialty_data = specialty_data.sort_values('patients_waiting', ascending=False)
        
        # Create color scale based on wait times
        colors = []
        for wait_time in specialty_data['avg_wait_time']:
            if wait_time < 15:
                colors.append('green')
            elif wait_time < 30:
                colors.append('orange')
            else:
                colors.append('red')
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=specialty_data['specialty'],
                y=specialty_data['patients_waiting'],
                marker_color=colors,
                text=specialty_data['avg_wait_time'].apply(lambda x: f"{x} min wait"),
                hovertemplate="<b>%{x}</b><br>Patients waiting: %{y}<br>Average wait: %{text}<extra></extra>"
            )
        ])
        
        # Update layout
        fig.update_layout(
            title="Current Queue by Specialty",
            xaxis_title="Specialty",
            yaxis_title="Patients Waiting",
            height=400
        )
        
        return fig
    
    def get_recent_notifications(self, current_datetime):
        """
        Generate simulated recent patient notifications.
        
        Parameters:
        -----------
        current_datetime : datetime
            Current date and time
            
        Returns:
        --------
        list
            List of notification dictionaries
        """
        # Load appointment data
        appointments_df = self.load_appointment_data()
        
        if appointments_df.empty:
            return []
        
        # Get current date
        current_date = current_datetime.date()
        
        # Filter today's appointments
        today_appointments = appointments_df[appointments_df['appointment_date'] == current_date]
        
        if today_appointments.empty:
            return []
        
        # Generate recent notifications (last 5 appointments)
        recent_appointments = today_appointments.sort_values('appointment_time', ascending=False).head(5)
        
        notifications = []
        
        for _, appt in recent_appointments.iterrows():
            # Generate a time stamp slightly before appointment time
            hour, minute = appt['appointment_time'].hour, appt['appointment_time'].minute
            notification_time = f"{hour:02d}:{max(0, minute-10):02d}"
            
            # Generate message based on wait time
            wait_time = appt['wait_time_minutes']
            
            if wait_time > 30:
                message = f"Your appointment may be delayed by approximately {wait_time} minutes."
            elif wait_time > 15:
                message = f"Please expect a wait time of approximately {wait_time} minutes."
            else:
                message = "Your doctor is on schedule. Please arrive 10 minutes before your appointment."
            
            notifications.append({
                'patient_id': appt['patient_id'],
                'time': notification_time,
                'message': message
            })
        
        return notifications
