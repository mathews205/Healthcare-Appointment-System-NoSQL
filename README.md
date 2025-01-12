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
pip install pymongo neo4j redis pandas
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
mongo_uri = "mongodb+srv://<username>:<password>@cluster-url/"
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
    host="host",
    port=18475,
    password="password",
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

### 5. **Integrated Queries**

#### Example Query 1: Find all appointments for a patient (MongoDB) and their status (Redis):
```python
patient_id = 29872499824296.0
appointments = collection.find({"PatientId": patient_id})
for appointment in appointments:
    key = f"appointment:{appointment['AppointmentID']}:status"
    status = redis_client.get(key)
    print(f"Appointment ID: {appointment['AppointmentID']}, Status: {status}")
```

#### Example Query 2: Find missed appointments for a date (Neo4j):
```cypher
MATCH (p:Patient)-[:HAS_APPOINTMENT]->(a:Appointment)
WHERE a.appointment_day = "2016-04-29T00:00:00Z" AND a.no_show = "Yes"
RETURN p.id, a.id;
```

---

## **Conclusion**
This project demonstrates the power of combining NoSQL databases:
- **MongoDB** for storing structured appointment data.
- **Neo4j** for analyzing relationships.
- **Redis** for caching and real-time data access.

With these integrations, the system achieves both scalability and performance, making it a robust solution for managing medical appointments.

