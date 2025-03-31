import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime, timedelta

class WaitTimePredictor:
    """
    Machine learning model to predict wait times for patients based on
    historical appointment data and current clinic conditions.
    """
    
    def __init__(self):
        self.model = None
        self.model_trained = False
        self.model_path = 'models/wait_time_model.joblib'
        self.feature_importance = None
        
        # Try to load a previously trained model if it exists
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.model_trained = True
            except:
                self.model_trained = False
    
    def preprocess_data(self, appointments_df, doctors_df):
        """
        Preprocess the appointment data for training or prediction.
        
        Parameters:
        -----------
        appointments_df : pandas.DataFrame
            DataFrame containing appointment information
        doctors_df : pandas.DataFrame
            DataFrame containing doctor information
            
        Returns:
        --------
        X : pandas.DataFrame
            Feature matrix
        y : pandas.Series
            Target variable (wait times)
        """
        # Merge appointments with doctor information
        if not appointments_df.empty and not doctors_df.empty:
            merged_df = appointments_df.merge(doctors_df, on='doctor_id', how='left')
            
            # Extract features for prediction
            X = merged_df[['hour_of_day', 'day_of_week', 'specialty', 'doctor_experience',
                          'avg_consultation_time', 'scheduled_patients_count', 'arrived_early']]
            
            # Target variable is the wait time
            y = merged_df['wait_time_minutes']
            
            return X, y
        else:
            # Return empty DataFrames if no data
            return pd.DataFrame(), pd.Series()
    
    def train(self, appointments_df, doctors_df):
        """
        Train the wait time prediction model with historical data.
        
        Parameters:
        -----------
        appointments_df : pandas.DataFrame
            DataFrame containing historical appointment information
        doctors_df : pandas.DataFrame
            DataFrame containing doctor information
        """
        if appointments_df.empty or doctors_df.empty:
            return False
        
        # Preprocess data
        X, y = self.preprocess_data(appointments_df, doctors_df)
        
        if X.empty or len(y) == 0:
            return False
        
        # Define categorical features for encoding
        categorical_features = ['specialty', 'day_of_week']
        numerical_features = ['hour_of_day', 'doctor_experience', 'avg_consultation_time', 
                             'scheduled_patients_count', 'arrived_early']
        
        # Create preprocessing pipeline
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', categorical_transformer, categorical_features),
                ('num', 'passthrough', numerical_features)
            ])
        
        # Create and train the model
        self.model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        
        # Split data for training and validation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        # Store feature importance
        regressor = self.model.named_steps['regressor']
        self.feature_importance = pd.DataFrame(
            regressor.feature_importances_,
            index=self.model.named_steps['preprocessor'].get_feature_names_out(),
            columns=['importance']
        ).sort_values('importance', ascending=False)
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        
        self.model_trained = True
        return True
    
    def predict(self, features):
        """
        Predict wait time for a given set of features.
        
        Parameters:
        -----------
        features : pandas.DataFrame
            Features for prediction
            
        Returns:
        --------
        float
            Predicted wait time in minutes
        """
        if not self.model_trained or self.model is None:
            return 30  # Default prediction if model is not trained
        
        try:
            prediction = self.model.predict(features)
            return max(0, float(prediction[0]))  # Ensure non-negative wait time
        except Exception as e:
            print(f"Prediction error: {e}")
            return 30  # Default prediction on error
    
    def get_feature_importance(self):
        """
        Return the feature importance from the trained model.
        
        Returns:
        --------
        pandas.DataFrame
            Feature importance data
        """
        if not self.model_trained or self.feature_importance is None:
            return pd.DataFrame()
        
        return self.feature_importance
    
    def predict_batch(self, current_time, appointments_df, doctors_df):
        """
        Generate predictions for multiple appointments based on current time.
        
        Parameters:
        -----------
        current_time : datetime
            Current time to consider for predictions
        appointments_df : pandas.DataFrame
            Current appointment data
        doctors_df : pandas.DataFrame
            Doctor data
            
        Returns:
        --------
        pandas.DataFrame
            DataFrame with appointment IDs and predicted wait times
        """
        if not self.model_trained or self.model is None:
            # Return default predictions if no model
            results = appointments_df.copy()
            results['predicted_wait_time'] = 30
            return results
        
        # Filter appointments for today and upcoming
        current_date = current_time.date()
        current_time_only = current_time.time()
        
        today_appointments = appointments_df[
            (appointments_df['appointment_date'] == current_date) &
            (appointments_df['appointment_time'] >= current_time_only)
        ].copy()
        
        if today_appointments.empty:
            return pd.DataFrame()
        
        # Create feature matrix for each appointment
        merged_data = today_appointments.merge(doctors_df, on='doctor_id', how='left')
        
        # Extract features in the same format as training data
        features = merged_data[['hour_of_day', 'day_of_week', 'specialty', 'doctor_experience',
                               'avg_consultation_time', 'scheduled_patients_count', 'arrived_early']]
        
        # Generate predictions
        predictions = self.model.predict(features)
        
        # Add predictions to results
        results = today_appointments.copy()
        results['predicted_wait_time'] = predictions
        
        # Ensure non-negative wait times
        results['predicted_wait_time'] = results['predicted_wait_time'].apply(lambda x: max(0, x))
        
        return results
