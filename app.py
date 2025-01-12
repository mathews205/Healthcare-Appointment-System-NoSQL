import streamlit as st
import pandas as pd
from pymongo import MongoClient
from neo4j import GraphDatabase
import redis

# MongoDB Configuration
mongo_uri = "mongodb+srv://followalong:Password123@cluster0.u58r5.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["HealthcareDB"]
collection = db["Appointments"]

# Neo4j Configuration
neo4j_uri = "bolt://localhost:7687"
neo4j_username = "neo4j"
neo4j_password = "password"
neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))

# Redis Configuration
redis_client = redis.StrictRedis(
    host="redis-18475.c339.eu-west-3-1.ec2.redns.redis-cloud.com",
    port=18475,
    password="joNXaZvraDJZ7WFU7biPJWcS4MdaUrTl",
    decode_responses=True
)

# Streamlit App
st.title("Medical Appointment Management System")

# Sidebar Navigation
page = st.sidebar.selectbox("Navigate", ["Home", "Patient Lookup", "Appointment Status", "Data Analysis"])

# Home Page
if page == "Home":
    st.header("Welcome to the Medical Appointment Management System")
    total_records = collection.count_documents({})
    no_show_count = collection.count_documents({"No-show": "Yes"})
    st.write(f"Total Appointments: {total_records}")
    st.write(f"No-Show Count: {no_show_count}")

# Patient Lookup
elif page == "Patient Lookup":
    st.header("Patient Lookup")
    patient_id = st.text_input("Enter Patient ID:")
    if st.button("Search"):
        patient_data = collection.find_one({"PatientId": patient_id})
        if patient_data:
            st.write("Patient Details:")
            st.json(patient_data)
        else:
            st.write("Patient not found!")

# Appointment Status
elif page == "Appointment Status":
    st.header("Appointment Status")
    appointment_id = st.text_input("Enter Appointment ID:")
    if st.button("Check Status"):
        status = redis_client.get(f"appointment:{appointment_id}:status")
        if status:
            st.write(f"Status of Appointment {appointment_id}: {status}")
        else:
            st.write("Appointment not found!")

# Data Analysis
elif page == "Data Analysis":
    st.header("Data Analysis and Visualization")
    st.write("Visualizations of no-show rates, appointments by day, etc.")
    
    # Example Visualization: No-Show Rate
    no_show_count = collection.count_documents({"No-show": "Yes"})
    show_count = collection.count_documents({"No-show": "No"})
    data = pd.DataFrame({
        "Category": ["No-show", "Show"],
        "Count": [no_show_count, show_count]
    })
    st.bar_chart(data.set_index("Category"))
