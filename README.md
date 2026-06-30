# The Proactive-Reactive Divide

## Analysing Citizen Engagement Patterns with Aadhaar Updates

A data analytics project that quantifies the behavioral divide between citizens who proactively maintain their Aadhaar information versus those who reactively engage only during crisis periods.

---

## Final Report

For quick review of major outcomes, see **[FINAL_REPORT.md](FINAL_REPORT.md)**.

---

## Project Overview

This project builds a **Proactive-Reactive Score (PRS)** system to analyse citizen engagement patterns with Aadhaar enrollment and updates across India. The system identifies populations at risk of authentication failures based on their update behavior patterns.

### Core Research Question

> How do we distinguish between populations that proactively maintain their biometric and demographic information versus those that only update when authentication failures threaten access to essential services?

---

## Tech Stack

| Category             | Technologies                      |
| -------------------- | --------------------------------- |
| **Data Processing**  | Polars, Pandas, NumPy             |
| **Machine Learning** | TensorFlow, Scikit-learn, XGBoost |
| **Validation**       | Pandera, Great Expectations       |
| **Storage**          | Parquet (PyArrow)                 |
| **Visualization**    | Plotly, Matplotlib                |
| **Dashboard**        | Dash, Streamlit                   |

---

## Project Structure

```
├── Proactive_Reactive_Divide_Analysis.ipynb   # Main analysis notebook
├── Implementation_Plan.md                      # Detailed implementation plan
├── requirements.txt                            # Python dependencies
├── datasets/
│   └── aadhar_datasets/
│       ├── api_data_aadhar_enrolment/         # Enrollment data
│       ├── api_data_aadhar_demographic/       # Demographic updates
│       └── api_data_aadhar_biometric/         # Biometric updates
└── outputs/
    ├── parquet/                               # Optimized data storage
    │   ├── master_dataset.parquet
    │   ├── enrolment_clean.parquet
    │   ├── demographic_clean.parquet
    │   └── biometric_clean.parquet
    ├── reports/
    │   └── day1_quality_report.json           # Data quality report
    └── master_dataset.csv                     # CSV export
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Analysis

Open `Proactive_Reactive_Divide_Analysis.ipynb` in Jupyter or VS Code and run all cells.

---

## Implementation Progress

### Day 1: Data Preparation ✅

- Loaded ~5M records across 3 datasets using Polars
- Validated data quality with Pandera schemas
- Created master dataset at district-month level
- Exported to Parquet format (60%+ smaller than CSV)

### Day 2-6: Coming Soon

- PRS calculation engine (Time, Behavior, Trend components)
- Classification into 5 behavioral tiers
- Geographic visualizations
- Interactive dashboard

---

## PRS Methodology

The Proactive-Reactive Score ranges from 0 (proactive) to 1 (reactive):

| Component | Weight | Description                         |
| --------- | ------ | ----------------------------------- |
| Time      | 37.5%  | Update lag against expected windows |
| Behavior  | 43.75% | Demographic/biometric update ratio  |
| Trend     | 18.75% | Month-over-month changes            |

### Classification Tiers

| Tier                 | PRS Range | Description               |
| -------------------- | --------- | ------------------------- |
| Proactive Leaders    | 0.0 - 0.3 | Exemplary engagement      |
| Transition Districts | 0.3 - 0.5 | Moderate proactive        |
| Reactive Majority    | 0.5 - 0.7 | Wait-and-respond          |
| Crisis-Dependent     | 0.7 - 0.9 | Engagement under pressure |
| System Failure Zones | > 0.9     | Collapsed mechanism       |

---

## Data Sources

| Dataset     | Records | Description                               |
| ----------- | ------- | ----------------------------------------- |
| Enrollment  | ~1M     | New Aadhaar registrations                 |
| Demographic | ~2M     | Low-friction updates (address, phone)     |
| Biometric   | ~1.8M   | High-friction updates (fingerprint, iris) |

**Analysis Period:** March - July 2025

---

## License

This project is for analytical purposes only.

