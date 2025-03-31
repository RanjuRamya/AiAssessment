import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_wait_time_chart(predictions_df):
    """
    Create a line chart of predicted wait times.
    
    Parameters:
    -----------
    predictions_df : pandas.DataFrame
        DataFrame with hour and predicted wait times
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure with the chart
    """
    if predictions_df.empty:
        # Create empty figure with message
        fig = go.Figure()
        fig.update_layout(
            title="No prediction data available",
            xaxis_title="Hour",
            yaxis_title="Predicted Wait Time (minutes)",
            height=400
        )
        return fig
    
    # Create line chart with markers
    fig = px.line(
        predictions_df,
        x='hour_label',
        y='predicted_wait_time',
        markers=True,
        labels={
            'hour_label': 'Hour',
            'predicted_wait_time': 'Predicted Wait Time (minutes)'
        },
        title="Predicted Wait Times"
    )
    
    # Add color zones for different wait time levels
    fig.add_hrect(
        y0=0, y1=15,
        fillcolor="green", opacity=0.1,
        layer="below", line_width=0,
    )
    
    fig.add_hrect(
        y0=15, y1=30,
        fillcolor="orange", opacity=0.1,
        layer="below", line_width=0,
    )
    
    fig.add_hrect(
        y0=30, y1=100,
        fillcolor="red", opacity=0.1,
        layer="below", line_width=0,
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Hour",
        yaxis_title="Predicted Wait Time (minutes)",
        height=400,
        yaxis=dict(range=[0, max(predictions_df['predicted_wait_time']) * 1.2])
    )
    
    # Add hover information
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Predicted wait: %{y} minutes<extra></extra>"
    )
    
    return fig

def create_patient_flow_chart(flow_df):
    """
    Create a bar chart of patient flow by hour.
    
    Parameters:
    -----------
    flow_df : pandas.DataFrame
        DataFrame with hourly patient counts
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure with the chart
    """
    if flow_df.empty:
        # Create empty figure with message
        fig = go.Figure()
        fig.update_layout(
            title="No patient flow data available",
            xaxis_title="Hour",
            yaxis_title="Number of Patients",
            height=400
        )
        return fig
    
    # Define peak hours (5 PM - 8 PM)
    peak_hours = list(range(17, 21))
    
    # Create colors list for highlighting peak hours
    colors = ['#1e88e5' if hour not in peak_hours else '#ff5252' for hour in flow_df['hour']]
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=flow_df['hour_label'],
            y=flow_df['patient_count'],
            marker_color=colors,
            hovertemplate="<b>%{x}</b><br>Patients: %{y}<extra></extra>"
        )
    ])
    
    # Add annotation for peak hours
    fig.add_annotation(
        x="17:00", y=flow_df['patient_count'].max(),
        text="Peak Hours",
        showarrow=True,
        arrowhead=1,
        ax=0, ay=-40
    )
    
    # Update layout
    fig.update_layout(
        title="Patient Flow by Hour",
        xaxis_title="Hour",
        yaxis_title="Number of Patients",
        height=400,
        bargap=0.2
    )
    
    return fig

def create_doctor_availability_chart(doctors_df):
    """
    Create a horizontal bar chart of doctor availability.
    
    Parameters:
    -----------
    doctors_df : pandas.DataFrame
        DataFrame with doctor information including availability
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure with the chart
    """
    if doctors_df.empty:
        # Create empty figure with message
        fig = go.Figure()
        fig.update_layout(
            title="No doctor data available",
            xaxis_title="Hours Available",
            yaxis_title="Doctor",
            height=500
        )
        return fig
    
    # Prepare data for the chart
    # Note: In a real system, this would use actual availability data
    # For simulation, we'll generate random availability hours
    chart_data = []
    
    for _, doctor in doctors_df.iterrows():
        # Simulate available hours (between 1 and 8)
        availability_hours = np.random.randint(1, 9)
        
        chart_data.append({
            'doctor_name': f"Dr. {doctor['doctor_name']}",
            'specialty': doctor['specialty'],
            'hours_available': availability_hours,
            'color': 'red' if availability_hours < 3 else 'orange' if availability_hours < 5 else 'green'
        })
    
    # Convert to DataFrame
    chart_df = pd.DataFrame(chart_data)
    
    # Sort by specialty and hours available
    chart_df = chart_df.sort_values(['specialty', 'hours_available'], ascending=[True, False])
    
    # Create horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            y=chart_df['doctor_name'],
            x=chart_df['hours_available'],
            orientation='h',
            marker_color=chart_df['color'],
            text=chart_df['specialty'],
            hovertemplate="<b>%{y}</b><br>Specialty: %{text}<br>Hours available: %{x}<extra></extra>"
        )
    ])
    
    # Update layout
    fig.update_layout(
        title="Doctor Availability Today",
        xaxis_title="Hours Available",
        yaxis_title="Doctor",
        height=500
    )
    
    return fig

def create_wait_time_heatmap(historical_data):
    """
    Create a heatmap of historical wait times by day and hour.
    
    Parameters:
    -----------
    historical_data : pandas.DataFrame
        DataFrame with historical appointment information
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure with the heatmap
    """
    if historical_data.empty:
        # Create empty figure with message
        fig = go.Figure()
        fig.update_layout(
            title="No historical data available",
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            height=400
        )
        return fig
    
    # Prepare data for heatmap
    # Group by day of week and hour of day
    heatmap_data = historical_data.groupby(['day_of_week', 'hour_of_day'])['wait_time_minutes'].mean().reset_index()
    
    # Create pivot table
    pivot_data = heatmap_data.pivot(index='day_of_week', columns='hour_of_day', values='wait_time_minutes')
    
    # Day of week names
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_names = [day_names[i] for i in pivot_data.index]
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=day_names,
        colorscale='RdYlGn_r',  # Red for high wait times, green for low
        colorbar=dict(title="Wait Time (min)"),
        hovertemplate="Day: %{y}<br>Hour: %{x}:00<br>Wait Time: %{z:.1f} min<extra></extra>"
    ))
    
    # Update layout
    fig.update_layout(
        title="Historical Wait Times by Day and Hour",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=400
    )
    
    return fig

def create_early_arrival_chart(historical_data):
    """
    Create a bar chart showing early arrival patterns.
    
    Parameters:
    -----------
    historical_data : pandas.DataFrame
        DataFrame with historical appointment information
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure with the chart
    """
    if historical_data.empty or 'arrived_early' not in historical_data.columns:
        # Create empty figure with message
        fig = go.Figure()
        fig.update_layout(
            title="No early arrival data available",
            xaxis_title="Hour of Day",
            yaxis_title="Early Arrival Percentage",
            height=400
        )
        return fig
    
    # Group by hour of day
    hour_data = historical_data.groupby('hour_of_day').agg(
        total_appointments=('appointment_id', 'count'),
        early_arrivals=('arrived_early', 'sum')
    ).reset_index()
    
    # Calculate percentage
    hour_data['early_percentage'] = (hour_data['early_arrivals'] / hour_data['total_appointments']) * 100
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=hour_data['hour_of_day'],
            y=hour_data['early_percentage'],
            marker_color='#1e88e5',
            hovertemplate="<b>%{x}:00</b><br>Early arrivals: %{y:.1f}%<extra></extra>"
        )
    ])
    
    # Update layout
    fig.update_layout(
        title="Early Arrival Patterns by Hour",
        xaxis_title="Hour of Day",
        yaxis_title="Early Arrival Percentage (%)",
        height=400
    )
    
    # Set x-axis tick marks for each hour
    fig.update_xaxes(tickvals=list(range(9, 21)))
    
    return fig
