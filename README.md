Markdown
# 🛰️ Enterprise Digital Twin of an Oil Pipeline (PostGIS + Streamlit)

A real-time industrial Digital Twin solution designed for monitoring oil pipeline infrastructure, calculating environmental risks dynamically, and logging telemetry data into a secure spatial database.

---

## 🚀 Project Overview

This project simulates a real-time IoT sensor network deployed across critical pipeline segments. It integrates geospatial analysis (via PostGIS) with object-oriented physical modeling in Python to assess infrastructure risks (such as thermal expansion and water contamination hazards) without causing "alarm fatigue."

### Key Architectural Highlights:
* **Anti-Alarm Fatigue Logic:** Detects underwater river crossings (`[River Crossing]`) using spatial proximity data and dynamically adjusts threshold limits to prevent false-positive critical alerts.
* **Production-Ready Streamlit UI:** Uses dynamic element placeholders (`st.empty()`) and page reruns (`st.rerun()`) instead of unstable infinite loops, preventing browser memory leaks.
* **Enterprise Security:** Implements decoupling of sensitive credentials using environment variables via `python-dotenv`.

---

## 🛠️ Tech Stack

* **Frontend/Dashboard:** Streamlit (Python)
* **Database Layer:** PostgreSQL with PostGIS extension
* **ORM/Driver:** SQLAlchemy
* **Data Science & Processing:** Pandas, NumPy
* **Environment Management:** Python-Dotenv

---

## 🏗️ Architecture & Features

### 1. Spatial Database Layer (PostGIS)
The system fetches live coordinates and segments from PostgreSQL, calculating exact distances to nearby environmental objects (lakes and rivers) using native spatial queries:
```sql
SELECT s.segment_id,
       (SELECT MIN(ST_Distance(s.geometry, l.geometry)) FROM lakes l) AS lake_dist_m
FROM pipeline_segments s;
2. Digital Twin Object-Oriented Simulation
Each pipeline segment is instantiated as an independent object tracking its own state, proximity flags, and historical telemetry data.

3. Secure Credential Isolation
Database credentials are completely stripped out of the codebase and managed strictly via a local .env file, adhering to industry security standards.

💻 Installation & Setup
Clone the repository:

Bash
git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/yourusername/your-repo-name.git)
cd your-repo-name
Install dependencies:

Bash
pip install -r requirements.txt
Configure Environment Variables:
Create a .env file in the root directory and append your local database configuration:

Plaintext
DB_USER=your_postgres_user
DB_PASS=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fort_mcmurray_db
Run the Application:

Bash
streamlit run app.py