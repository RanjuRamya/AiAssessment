import streamlit as st
import pandas as pd
import os
import sys
import hashlib
import json
import random
from datetime import datetime

# Add paths to import custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def hash_password(password):
    """Create a SHA-256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_patient_data_if_needed():
    """Create patient data file if it doesn't exist"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    file_path = os.path.join(data_dir, 'patient_credentials.json')
    
    if not os.path.exists(file_path):
        # Create sample data
        sample_data = {
            "P1001": {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "password": hash_password("password123"),
                "phone": "555-123-4567"
            },
            "P1002": {
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "password": hash_password("password123"),
                "phone": "555-987-6543"
            }
        }
        
        # Save to JSON file
        with open(file_path, 'w') as f:
            json.dump(sample_data, f, indent=4)
            
    return file_path

def load_patient_data():
    """Load patient data from JSON file"""
    file_path = create_patient_data_if_needed()
    
    with open(file_path, 'r') as f:
        patient_data = json.load(f)
        
    return patient_data

def save_patient_data(patient_data):
    """Save patient data to JSON file"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    file_path = os.path.join(data_dir, 'patient_credentials.json')
    
    with open(file_path, 'w') as f:
        json.dump(patient_data, f, indent=4)

def show_login_signup():
    """Display the login and signup page"""
    
    # Initialize session state for authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    # If already authenticated, show logout option
    if st.session_state.authenticated:
        st.sidebar.success(f"Logged in as: {st.session_state.current_user['name']}")
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()
        return True
    
    # Display login/signup form
    st.title("Jayanagar Specialty Clinic")
    
    # Add logo
    st.image("generated-icon.png", width=150)
    
    st.markdown("""
    ### Patient Login & Registration
    Welcome to our clinic management system. Please login to your account or register as a new patient.
    """)
    
    # Create tabs for login and signup
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
    
    # Load patient data
    patient_data = load_patient_data()
    
    # Login tab
    with login_tab:
        st.subheader("Login to Your Account")
        
        login_id = st.text_input("Patient ID or Email", key="login_id")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if not login_id or not login_password:
                st.error("Please enter both ID/email and password")
            else:
                # Check if ID exists
                id_found = False
                for patient_id, patient in patient_data.items():
                    if (patient_id == login_id or patient['email'] == login_id) and patient['password'] == hash_password(login_password):
                        id_found = True
                        st.session_state.authenticated = True
                        st.session_state.current_user = {
                            'patient_id': patient_id,
                            'name': patient['name'],
                            'email': patient['email'],
                            'phone': patient['phone']
                        }
                        st.success(f"Welcome back, {patient['name']}!")
                        st.rerun()
                        break
                
                if not id_found:
                    st.error("Invalid ID/email or password. Please try again.")
    
    # Signup tab
    with signup_tab:
        st.subheader("Register as a New Patient")
        
        new_name = st.text_input("Full Name", key="new_name")
        new_email = st.text_input("Email Address", key="new_email")
        new_phone = st.text_input("Phone Number", key="new_phone")
        new_password = st.text_input("Create Password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("Register"):
            # Validate inputs
            if not new_name or not new_email or not new_phone or not new_password:
                st.error("Please fill out all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif '@' not in new_email or '.' not in new_email:
                st.error("Please enter a valid email address")
            else:
                # Check if email already exists
                email_exists = False
                for patient in patient_data.values():
                    if patient['email'] == new_email:
                        email_exists = True
                        break
                
                if email_exists:
                    st.error("This email is already registered. Please use a different email or try to login.")
                else:
                    # Generate a new patient ID
                    new_id = f"P{random.randint(1000, 9999)}"
                    while new_id in patient_data:
                        new_id = f"P{random.randint(1000, 9999)}"
                    
                    # Add new patient
                    patient_data[new_id] = {
                        "name": new_name,
                        "email": new_email,
                        "password": hash_password(new_password),
                        "phone": new_phone
                    }
                    
                    # Save updated data
                    save_patient_data(patient_data)
                    
                    # Log in the new user
                    st.session_state.authenticated = True
                    st.session_state.current_user = {
                        'patient_id': new_id,
                        'name': new_name,
                        'email': new_email,
                        'phone': new_phone
                    }
                    
                    st.success(f"Registration successful! Your Patient ID is {new_id}. Please remember this for future logins.")
                    st.rerun()
    
    # Footer information
    st.markdown("---")
    st.info("""
    **Need Help?**
    
    If you've forgotten your Patient ID or password, please contact our reception desk at 555-CLINIC.
    """)
    
    # Return authentication status
    return st.session_state.authenticated

if __name__ == "__main__":
    # This allows the module to be run directly
    show_login_signup()