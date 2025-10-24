# EtlProject

# 📊 ETL Ads Performance Project

This project is a **two-step Streamlit application** designed for validating and visualizing **advertising performance data** through an **ETL (Extract, Transform, Load)** pipeline.

It includes:
1. **Data Validation App (`validate_app.py`)** — checks CSV files using a Pydantic data model.
2. **Performance Dashboard (`dashboard_app.py`)** — builds an interactive dashboard with KPIs, charts, and insights.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [How It Works](#how-it-works)
- [Setup and Execution](#setup-and-execution)
- [Dashboard Features](#dashboard-features)
- [Future Improvements](#future-improvements)
- [Author](#author)
- [License](#license)

---

## 🚀 Overview

The goal of this project is to **validate marketing campaign data** and generate **interactive insights** such as:
- Spending and conversion trends  
- Lead performance by day of the week  
- CPA (Cost per Acquisition) distribution  
- Top-performing AdSets and creatives  

It ensures the data structure is consistent **before visualization**, preventing incorrect metrics or dashboard errors.

---

## 🧩 Architecture


---

## 🧰 Technologies Used

| Library | Purpose |
|----------|----------|
| **Streamlit** | Front-end UI for validation and dashboard |
| **Pandas** | Data manipulation and preprocessing |
| **Plotly Express** | Interactive charts |
| **NumPy** | Mathematical operations |
| **Pydantic** | Schema validation of data records |
| **Python 3.10+** | Core language |

---

## ⚙️ How It Works

### 1️⃣ Data Validation (`validate_app.py`)
- The user uploads a **CSV file** (e.g. ad performance data).
- Each row is validated against the schema defined in `validator.py`.
- Validation checks include:
  - Required fields  
  - Numeric formats (float, int)  
  - Non-negative values (`Amount_spent >= 0`)
- The app returns:
  - Total records processed  
  - Valid vs invalid counts  
  - Detailed error report with row and field names  

When all data passes validation, the CSV can be safely used in the dashboard.

---

### 2️⃣ Dashboard Visualization (`dashboard_app.py`)
- The user uploads the **validated CSV**.
- The app:
  - Fills missing values for `Conversions` and `Amount_spent`
  - Calculates **CPA** (Cost per Acquisition)
  - Aggregates metrics by month, weekday, and AdSet
  - Displays KPIs and six interactive charts using Plotly

---

## 💻 Setup and Execution

### 1. Clone the repository
```bash
git clone https://github.com/kikzz569/EtlProject.git
cd EtlProject
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.\.venv\Scripts\activate    # Windows
pip install -r requirements.txt
streamlit run validate_app.py
streamlit run dashboard_app.py
