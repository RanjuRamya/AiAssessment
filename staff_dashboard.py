import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import random

def show_staff_dashboard():
    """Display the staff efficiency dashboard with gamification elements."""
    st.title("Staff Efficiency Dashboard")
    
    # Add staff selection dropdown in the sidebar
    st.sidebar.subheader("Staff Selection")
    staff_role = st.sidebar.selectbox(
        "Select Role",
        ["Doctor", "Nurse", "Receptionist", "All Staff"]
    )
    
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
    
    # Create staff performance data
    staff_data = generate_staff_performance_data(current_datetime, appointments_df, doctors_df)
    
    # Display gamification header
    st.header("🏆 Performance Leaderboard")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Weekly Stats", "Achievement Badges", "Improvement Targets"])
    
    with tab1:
        display_performance_metrics(staff_data, staff_role)
    
    with tab2:
        display_achievement_badges(staff_data, staff_role)
    
    with tab3:
        display_improvement_targets(staff_data, staff_role)

def generate_staff_performance_data(current_datetime, appointments_df, doctors_df):
    """
    Generate staff performance data for the dashboard.
    In a real implementation, this would pull from actual staff activity logs.
    
    Parameters:
    -----------
    current_datetime : datetime
        Current date and time
    appointments_df : pandas.DataFrame
        Appointment data
    doctors_df : pandas.DataFrame
        Doctor data
        
    Returns:
    --------
    pandas.DataFrame
        Staff performance data
    """
    # Filter to recent appointments (last 7 days)
    start_date = (current_datetime - timedelta(days=7)).date()
    recent_appointments = appointments_df[appointments_df['appointment_date'] >= start_date]
    
    # Create staff data for doctors based on actual doctors in the system
    staff_data = []
    
    for _, doctor in doctors_df.iterrows():
        doctor_id = doctor['doctor_id']
        doctor_name = doctor['doctor_name']
        specialty = doctor['specialty']
        
        # Get appointments for this doctor
        doctor_appointments = recent_appointments[recent_appointments['doctor_id'] == doctor_id]
        
        if len(doctor_appointments) > 0:
            # Calculate metrics based on appointments
            avg_wait_time = doctor_appointments['wait_time_minutes'].mean()
            patients_seen = len(doctor_appointments)
            on_time_rate = (doctor_appointments['wait_time_minutes'] <= 15).mean() * 100
            early_arrival_handled = (doctor_appointments['arrived_early'] == True).mean() * 100
            
            # Generate efficiency score (higher is better) - inversely related to wait time
            efficiency_score = max(50, 100 - avg_wait_time * 1.5)
            
            # Generate patient satisfaction (simulated based on wait time and other factors)
            base_satisfaction = max(60, 100 - avg_wait_time * 2)
            variation = np.random.normal(0, 5)  # Add some random variation
            patient_satisfaction = min(100, max(0, base_satisfaction + variation))
            
            # Achievements (simulated)
            achievements = []
            if efficiency_score > 90:
                achievements.append("Efficiency Star")
            if patient_satisfaction > 90:
                achievements.append("Patient Favorite")
            if on_time_rate > 90:
                achievements.append("Punctuality Pro")
            if patients_seen > 15:
                achievements.append("High Volume")
            if early_arrival_handled > 80:
                achievements.append("Early Bird Handler")
                
            # Weekly improvement (simulated)
            weekly_improvement = np.random.normal(2, 5)
            
            staff_data.append({
                'staff_id': doctor_id,
                'staff_name': doctor_name,
                'role': 'Doctor',
                'department': specialty,
                'efficiency_score': efficiency_score,
                'patient_satisfaction': patient_satisfaction,
                'patients_seen': patients_seen,
                'wait_time_minutes': avg_wait_time,
                'on_time_rate': on_time_rate,
                'achievements': achievements,
                'weekly_improvement': weekly_improvement,
                'weekly_points': int(efficiency_score * 10 + patient_satisfaction * 5),
                'streak_days': np.random.randint(1, 10)
            })
    
    # Add simulated data for nurses and receptionists
    for role, count in [('Nurse', 10), ('Receptionist', 5)]:
        for i in range(1, count + 1):
            # Generate synthetic metrics for non-doctor staff
            efficiency_score = np.random.uniform(70, 95)
            patient_satisfaction = np.random.uniform(75, 98)
            
            # Achievements
            achievements = []
            if efficiency_score > 90:
                achievements.append("Efficiency Star")
            if patient_satisfaction > 90:
                achievements.append("Patient Favorite")
            if np.random.random() > 0.7:
                achievements.append("Team Player")
            if np.random.random() > 0.8:
                achievements.append("Quick Responder")
                
            # Department assignment
            if role == 'Nurse':
                departments = list(doctors_df['specialty'].unique())
                department = np.random.choice(departments)
            else:
                department = 'Front Desk'
                
            # Weekly improvement
            weekly_improvement = np.random.normal(2, 5)
            
            staff_data.append({
                'staff_id': f"{role[0]}{i}",
                'staff_name': f"{role} {i}",
                'role': role,
                'department': department,
                'efficiency_score': efficiency_score,
                'patient_satisfaction': patient_satisfaction,
                'patients_seen': np.random.randint(20, 50) if role == 'Nurse' else np.random.randint(40, 100),
                'wait_time_minutes': np.random.uniform(5, 15),
                'on_time_rate': np.random.uniform(80, 98),
                'achievements': achievements,
                'weekly_improvement': weekly_improvement,
                'weekly_points': int(efficiency_score * 8 + patient_satisfaction * 7),
                'streak_days': np.random.randint(1, 15)
            })
    
    return pd.DataFrame(staff_data)

def display_performance_metrics(staff_data, selected_role):
    """Display performance metrics for the selected staff role."""
    # Filter data based on selected role
    if selected_role != "All Staff":
        filtered_data = staff_data[staff_data['role'] == selected_role]
    else:
        filtered_data = staff_data
    
    if filtered_data.empty:
        st.warning(f"No data available for {selected_role}")
        return
    
    # Sort by weekly points (descending)
    leaderboard_data = filtered_data.sort_values('weekly_points', ascending=False)
    
    # Create leaderboard
    st.subheader("Weekly Performance Leaderboard")
    
    # Display top 3 with special formatting
    top3_cols = st.columns(3)
    
    for i, (idx, staff) in enumerate(leaderboard_data.head(3).iterrows()):
        with top3_cols[i]:
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            st.markdown(f"### {medal} {staff['staff_name']}")
            st.markdown(f"**Role:** {staff['role']}")
            st.markdown(f"**Department:** {staff['department']}")
            st.markdown(f"**Points:** {staff['weekly_points']}")
            
            # Create a small gauge chart for efficiency
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = staff['efficiency_score'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Efficiency"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 60], 'color': "red"},
                        {'range': [60, 80], 'color': "orange"},
                        {'range': [80, 100], 'color': "green"}
                    ]
                }
            ))
            fig.update_layout(height=150, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
    
    # Display the rest of the leaderboard
    st.markdown("### Rest of the Leaderboard")
    
    # Create a DataFrame for display
    display_data = leaderboard_data.iloc[3:][['staff_name', 'role', 'department', 'weekly_points', 'efficiency_score', 'patient_satisfaction']]
    display_data = display_data.reset_index(drop=True)
    display_data.index = display_data.index + 4  # Start from position 4
    
    # Format the table
    st.dataframe(
        display_data.style.format({
            'efficiency_score': '{:.1f}',
            'patient_satisfaction': '{:.1f}'
        }).background_gradient(
            subset=['weekly_points'], 
            cmap='Blues'
        ),
        use_container_width=True
    )
    
    # Streak counter
    st.subheader("🔥 Consistency Streaks")
    streak_data = filtered_data.sort_values('streak_days', ascending=False).head(5)
    
    for _, staff in streak_data.iterrows():
        streak_emojis = "🔥" * min(5, staff['streak_days'])
        st.markdown(f"**{staff['staff_name']}**: {streak_emojis} {staff['streak_days']} day streak")
    
    # Create charts
    st.subheader("Performance Metrics")
    col1, col2 = st.columns(2)
    
    with col1:
        # Efficiency score by department
        dept_efficiency = filtered_data.groupby('department')['efficiency_score'].mean().reset_index()
        fig = px.bar(
            dept_efficiency,
            x='department',
            y='efficiency_score',
            title="Average Efficiency by Department",
            color='efficiency_score',
            color_continuous_scale=px.colors.sequential.Blues,
            labels={'department': 'Department', 'efficiency_score': 'Efficiency Score'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Patient satisfaction by staff role
        role_satisfaction = filtered_data.groupby('role')['patient_satisfaction'].mean().reset_index()
        fig = px.bar(
            role_satisfaction,
            x='role',
            y='patient_satisfaction',
            title="Average Patient Satisfaction by Role",
            color='patient_satisfaction',
            color_continuous_scale=px.colors.sequential.Greens,
            labels={'role': 'Role', 'patient_satisfaction': 'Patient Satisfaction'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Improvement chart
    improvement_data = filtered_data.sort_values('weekly_improvement', ascending=False).head(10)
    fig = px.bar(
        improvement_data,
        x='staff_name',
        y='weekly_improvement',
        title="Top Weekly Improvements",
        color='weekly_improvement',
        color_continuous_scale=px.colors.diverging.RdYlGn,
        labels={'staff_name': 'Staff', 'weekly_improvement': 'Improvement %'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def display_achievement_badges(staff_data, selected_role):
    """Display achievement badges for staff."""
    # Filter data based on selected role
    if selected_role != "All Staff":
        filtered_data = staff_data[staff_data['role'] == selected_role]
    else:
        filtered_data = staff_data
    
    if filtered_data.empty:
        st.warning(f"No data available for {selected_role}")
        return
    
    st.subheader("Achievement Badges")
    
    # Define badge descriptions and colors
    badge_info = {
        "Efficiency Star": {
            "description": "Consistently maintains high efficiency in patient processing",
            "color": "#1E88E5",
            "icon": "⭐"
        },
        "Patient Favorite": {
            "description": "Receives exceptional feedback from patients",
            "color": "#FFC107",
            "icon": "😃"
        },
        "Punctuality Pro": {
            "description": "Maintains excellent on-time rates for appointments",
            "color": "#4CAF50",
            "icon": "⏰"
        },
        "High Volume": {
            "description": "Handles a high number of patients while maintaining quality",
            "color": "#9C27B0",
            "icon": "📈"
        },
        "Early Bird Handler": {
            "description": "Efficiently accommodates patients who arrive early",
            "color": "#2196F3",
            "icon": "🐦"
        },
        "Team Player": {
            "description": "Consistently helps colleagues and improves team performance",
            "color": "#FF5722",
            "icon": "🤝"
        },
        "Quick Responder": {
            "description": "Addresses patient needs promptly and efficiently",
            "color": "#F44336",
            "icon": "⚡"
        }
    }
    
    # Count achievements by type
    all_achievements = []
    for _, staff in filtered_data.iterrows():
        all_achievements.extend(staff['achievements'])
    
    achievement_counts = pd.Series(all_achievements).value_counts().reset_index()
    achievement_counts.columns = ['achievement', 'count']
    
    # Display achievement counts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not achievement_counts.empty:
            fig = px.bar(
                achievement_counts,
                x='achievement',
                y='count',
                title="Achievement Distribution",
                color='achievement',
                labels={'achievement': 'Badge Type', 'count': 'Number of Staff'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No achievements data available")
    
    with col2:
        st.markdown("### Badge Guide")
        for badge, info in badge_info.items():
            st.markdown(f"""
            <div style="background-color:{info['color']}20; padding:8px; border-radius:5px; margin-bottom:8px;">
                <b>{info['icon']} {badge}</b><br>
                {info['description']}
            </div>
            """, unsafe_allow_html=True)
    
    # Display individual achievement showcases
    st.subheader("Staff Achievement Showcases")
    
    # Filter staff with achievements
    staff_with_badges = filtered_data[filtered_data['achievements'].apply(len) > 0]
    
    if staff_with_badges.empty:
        st.info("No staff members have earned badges yet")
    else:
        # Sort by number of achievements (descending)
        staff_with_badges = staff_with_badges.assign(
            badge_count=staff_with_badges['achievements'].apply(len)
        ).sort_values('badge_count', ascending=False)
        
        # Display in a grid
        cols = st.columns(3)
        
        for i, (_, staff) in enumerate(staff_with_badges.iterrows()):
            with cols[i % 3]:
                st.markdown(f"### {staff['staff_name']}")
                st.markdown(f"**Role:** {staff['role']} | **Dept:** {staff['department']}")
                
                # Display badges
                badges_html = ""
                for badge in staff['achievements']:
                    if badge in badge_info:
                        info = badge_info[badge]
                        badges_html += f"""
                        <span style="background-color:{info['color']}; color:white; padding:3px 8px; border-radius:10px; margin-right:5px; display:inline-block; margin-bottom:5px;">
                            {info['icon']} {badge}
                        </span>
                        """
                
                st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
                
                # Progress to next badge
                if len(staff['achievements']) < len(badge_info):
                    progress = min(0.95, (len(staff['achievements']) / len(badge_info)) + 0.1)
                    st.progress(progress)
                    st.caption(f"Progress to next badge: {int(progress * 100)}%")
                else:
                    st.success("All badges achieved!")
                
                st.markdown("---")

def display_improvement_targets(staff_data, selected_role):
    """Display improvement targets for staff."""
    # Filter data based on selected role
    if selected_role != "All Staff":
        filtered_data = staff_data[staff_data['role'] == selected_role]
    else:
        filtered_data = staff_data
    
    if filtered_data.empty:
        st.warning(f"No data available for {selected_role}")
        return
    
    st.subheader("Personal Improvement Targets")
    
    # Select a specific staff member
    staff_list = filtered_data['staff_name'].tolist()
    selected_staff = st.selectbox("Select Staff Member", staff_list)
    
    if selected_staff:
        staff_info = filtered_data[filtered_data['staff_name'] == selected_staff].iloc[0]
        
        st.markdown(f"### Targets for {staff_info['staff_name']}")
        st.markdown(f"**Role:** {staff_info['role']} | **Department:** {staff_info['department']}")
        
        # Current metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Efficiency Score",
                value=f"{staff_info['efficiency_score']:.1f}",
                delta=f"{staff_info['weekly_improvement']:.1f}%"
            )
        
        with col2:
            st.metric(
                label="Patient Satisfaction",
                value=f"{staff_info['patient_satisfaction']:.1f}",
                delta=f"{np.random.uniform(-2, 4):.1f}%"
            )
        
        with col3:
            st.metric(
                label="On-Time Rate",
                value=f"{staff_info['on_time_rate']:.1f}%",
                delta=f"{np.random.uniform(-1, 3):.1f}%"
            )
        
        # Generate improvement targets
        st.markdown("### Suggested Improvement Areas")
        
        improvement_areas = []
        
        # Logic for determining improvement areas
        if staff_info['efficiency_score'] < 85:
            improvement_areas.append({
                'area': 'Efficiency',
                'current': staff_info['efficiency_score'],
                'target': min(100, staff_info['efficiency_score'] + 10),
                'suggestions': [
                    "Optimize patient documentation workflow",
                    "Utilize quick reference protocols for common cases",
                    "Coordinate with support staff to prepare for appointments"
                ]
            })
        
        if staff_info['patient_satisfaction'] < 90:
            improvement_areas.append({
                'area': 'Patient Satisfaction',
                'current': staff_info['patient_satisfaction'],
                'target': min(100, staff_info['patient_satisfaction'] + 8),
                'suggestions': [
                    "Enhance communication about wait times",
                    "Personalize patient interactions",
                    "Follow up with patients who experienced delays"
                ]
            })
        
        if staff_info['on_time_rate'] < 90:
            improvement_areas.append({
                'area': 'Punctuality',
                'current': staff_info['on_time_rate'],
                'target': min(100, staff_info['on_time_rate'] + 7),
                'suggestions': [
                    "Pre-process patient information before appointments",
                    "Implement buffer time between complex cases",
                    "Use AI predictions to adjust appointment durations"
                ]
            })
        
        # If no improvement areas identified, add general suggestions
        if not improvement_areas:
            improvement_areas.append({
                'area': 'Skill Development',
                'current': 85,
                'target': 95,
                'suggestions': [
                    "Cross-train in related specialties",
                    "Mentor junior staff members",
                    "Participate in process improvement initiatives"
                ]
            })
        
        # Display improvement areas
        for area in improvement_areas:
            expander = st.expander(f"📈 {area['area']}: {area['current']:.1f} → {area['target']:.1f}")
            with expander:
                # Progress bar
                progress = area['current'] / 100
                st.progress(progress)
                
                # Calculate days to target based on current improvement rate
                if 'weekly_improvement' in staff_info:
                    improvement_rate = max(0.5, staff_info['weekly_improvement'])
                    days_to_target = int((area['target'] - area['current']) / improvement_rate * 7)
                    st.write(f"Estimated time to reach target: **{days_to_target} days** at current improvement rate")
                
                # Suggestions
                st.markdown("**Suggested Actions:**")
                for suggestion in area['suggestions']:
                    st.markdown(f"- {suggestion}")
        
        # Weekly goal tracker
        st.markdown("### Weekly Goal Tracker")
        
        # Generate random goals based on staff role
        goals = []
        
        if staff_info['role'] == 'Doctor':
            goals = [
                {"goal": "Reduce average wait time by 5 minutes", "progress": np.random.uniform(0, 1)},
                {"goal": "Handle early arrivals efficiently", "progress": np.random.uniform(0, 1)},
                {"goal": "Document patient interactions promptly", "progress": np.random.uniform(0, 1)},
                {"goal": "Participate in team coordination meetings", "progress": np.random.uniform(0, 1)}
            ]
        elif staff_info['role'] == 'Nurse':
            goals = [
                {"goal": "Prepare patients efficiently for consultations", "progress": np.random.uniform(0, 1)},
                {"goal": "Update patient records within 10 minutes", "progress": np.random.uniform(0, 1)},
                {"goal": "Coordinate with doctors on scheduling", "progress": np.random.uniform(0, 1)},
                {"goal": "Complete patient follow-up calls", "progress": np.random.uniform(0, 1)}
            ]
        elif staff_info['role'] == 'Receptionist':
            goals = [
                {"goal": "Keep queue wait times under 5 minutes", "progress": np.random.uniform(0, 1)},
                {"goal": "Verify patient information at check-in", "progress": np.random.uniform(0, 1)},
                {"goal": "Manage early arrivals appropriately", "progress": np.random.uniform(0, 1)},
                {"goal": "Coordinate with clinical staff on schedule changes", "progress": np.random.uniform(0, 1)}
            ]
        
        # Display goals with progress bars
        for goal in goals:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(goal["goal"])
                st.progress(goal["progress"])
            with col2:
                st.caption("Progress")
                st.write(f"{int(goal['progress'] * 100)}%")
        
        # Reward tracking
        st.markdown("### 🎁 Reward Progress")
        
        # Calculate reward points
        reward_points = int(staff_info['weekly_points'] * 0.5)
        next_reward = 100
        
        # Progress to next reward
        reward_progress = min(1.0, reward_points / next_reward)
        st.progress(reward_progress)
        st.write(f"Reward Points: **{reward_points}/{next_reward}** needed for next reward")
        
        # Reward options
        st.markdown("**Available Rewards:**")
        st.markdown("- 100 points: Extra break time ☕")
        st.markdown("- 250 points: Premium parking spot 🚗")
        st.markdown("- 500 points: Lunch voucher 🍱")
        st.markdown("- 1000 points: Schedule flexibility day 📅")