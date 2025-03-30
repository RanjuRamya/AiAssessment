import streamlit as st

st.title("Clinic Management System Test Page")
st.write("This is a simple test page to verify the Streamlit app is running correctly.")

st.success("If you can see this message, the app is working properly!")

st.header("Basic Information")
st.write("This AI-powered system is designed to help Jayanagar Specialty Clinic reduce wait times by 30% during peak hours (5-8pm).")

st.header("System Features")
features = [
    "Wait time prediction using machine learning",
    "Intelligent appointment scheduling",
    "Real-time queue management",
    "Doctor load balancing",
    "Peak hour congestion management"
]

for feature in features:
    st.write(f"- {feature}")