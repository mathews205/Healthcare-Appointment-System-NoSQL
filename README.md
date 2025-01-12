# README: Medical Appointment Management System Using NoSQL Databases

## **Project Overview**
This project implements a **Medical Appointment Management System** using three types of NoSQL databases:

1. **MongoDB (Document Database):**
   - Stores patient and appointment information as documents.

2. **Neo4j (Graph Database):**
   - Models the relationships between patients and their appointments as a graph.

3. **Redis (Key-Value Store):**
   - Caches real-time data such as appointment statuses for fast retrieval.

## **Dataset**
The dataset used is the **"KaggleV2-May-2016"** dataset, which includes the following fields:
- **PatientId:** Unique identifier for each patient.
- **AppointmentID:** Unique identifier for each appointment.
- **Gender:** Gender of the patient.
- **ScheduledDay:** The date and time the appointment was scheduled.
- **AppointmentDay:** The date of the actual appointment.
- **Age:** Age of the patient.
- **Neighbourhood:** Location of the clinic.
- **Scholarship:** Indicates if the patient is enrolled in welfare programs.
- **Hipertension, Diabetes, Alcoholism, Handcap:** Health conditions of the patient.
- **SMS_received:** Whether the patient received a reminder.
- **No-show:** Indicates whether the patient showed up for the appointment.

## **Project Workflow**

### 1. **Setup and Dependencies**
#### Install Required Libraries:
```bash
pip install streamlit pymongo neo4j redis pandas
```

---

### 2. **MongoDB**
#### Connection and Data Loading:
- Connect to MongoDB using the connection string.
- Insert the dataset into the `HealthcareDB` database and `Appointments` collection.

**Code Snippet:**
```python
from pymongo import MongoClient
import pandas as pd

# MongoDB Connection
mongo_uri = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)

# Load Dataset
file_path = "dataset/KaggleV2-May-2016.csv"
data = pd.read_csv(file_path)

# Insert Data into MongoDB
db = client["HealthcareDB"]
collection = db["Appointments"]
data_dict = data.to_dict("records")
collection.insert_many(data_dict)
print("Data inserted into MongoDB successfully!")
```

#### Validation:
- Query MongoDB to verify data:
```python
print("Sample records from MongoDB:")
for record in collection.find().limit(5):
    print(record)
```

---

### 3. **Neo4j**
#### Connection and Data Loading:
- Use Neo4j to create a graph model for the data.
- Nodes represent `Patient` and `Appointment`, and the relationship `HAS_APPOINTMENT` links them.

**Code Snippet:**
```python
from neo4j import GraphDatabase

# Neo4j Connection
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"

driver = GraphDatabase.driver(uri, auth=(username, password))

# Insert Data into Neo4j
def load_data_to_neo4j():
    with driver.session() as session:
        for record in collection.find().limit(1000):
            session.run("""
                MERGE (p:Patient {id: $PatientId, gender: $Gender, age: $Age})
                MERGE (a:Appointment {id: $AppointmentID, scheduled_day: $ScheduledDay, appointment_day: $AppointmentDay, no_show: $NoShow})
                MERGE (p)-[:HAS_APPOINTMENT]->(a)
            """, {
                "PatientId": record["PatientId"],
                "Gender": record["Gender"],
                "Age": record["Age"],
                "AppointmentID": record["AppointmentID"],
                "ScheduledDay": record["ScheduledDay"],
                "AppointmentDay": record["AppointmentDay"],
                "NoShow": record["No-show"]
            })

load_data_to_neo4j()
```

#### Validation:
- Query Neo4j to validate:
```cypher
MATCH (p:Patient)-[:HAS_APPOINTMENT]->(a:Appointment)
RETURN p, a LIMIT 10;
```

---

### 4. **Redis**
#### Connection and Data Caching:
- Cache frequently accessed appointment statuses for fast retrieval.

**Code Snippet:**
```python
import redis

# Redis Connection
redis_client = redis.StrictRedis(
    host="redis-18475.c339.eu-west-3-1.ec2.redns.redis-cloud.com",
    port=18475,
    password="joNXaZvraDJZ7WFU7biPJWcS4MdaUrTl",
    decode_responses=True
)

# Cache Appointment Statuses
for record in collection.find().limit(1000):
    key = f"appointment:{record['AppointmentID']}:status"
    value = "no-show" if record["No-show"] == "Yes" else "confirmed"
    redis_client.set(key, value)

print("Appointment statuses loaded into Redis successfully!")
```

#### Validation:
- Verify data in Redis:
```python
key = "appointment:5572635:status"
status = redis_client.get(key)
print(f"Status of {key}: {status}")
```

---

### 5. **Streamlit Application**
#### Streamlit App Structure:
- **Home Page:** Overview of the system.
- **Patient Lookup:** Search for a patient using their `PatientId`.
- **Appointment Status:** Display real-time status of appointments.
- **Data Analysis:** Visualize no-show rates, appointments by day, etc.

**Code Snippet:**
```python
import streamlit as st
import pandas as pd
from pymongo import MongoClient
from neo4j import GraphDatabase
import redis

# MongoDB Connection
mongo_uri = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client["HealthcareDB"]
collection = db["Appointments"]

# Redis Connection
redis_client = redis.StrictRedis(
    host="redis-18475.c339.eu-west-3-1.ec2.redns.redis-cloud.com",
    port=18475,
    password="joNXaZvraDJZ7WFU7biPJWcS4MdaUrTl",
    decode_responses=True
)

# Neo4j Connection
neo4j_uri = "bolt://localhost:7687"
neo4j_username = "neo4j"
neo4j_password = "password"
neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))

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
    no_show_count = collection.count_documents({"No-show": "Yes"})
    show_count = collection.count_documents({"No-show": "No"})
    data = pd.DataFrame({
        "Category": ["No-show", "Show"],
        "Count": [no_show_count, show_count]
    })
    st.bar_chart(data.set_index("Category"))
```

---

## **Conclusion**
This project demonstrates the power of combining NoSQL databases:
- **MongoDB** for storing structured appointment data.
- **Neo4j** for analyzing relationships.
- **Redis** for caching and real-time data access.
- **Streamlit** for building an interactive web application.

With these integrations, the system achieves both scalability and performance, making it a robust solution for managing medical appointments.

