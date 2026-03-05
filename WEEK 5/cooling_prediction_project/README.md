# ❄️ Cooling Demand Prediction using Decision Tree

A lightweight Streamlit dashboard that uses a **Decision Tree Classifier** to predict whether cooling is needed in different building zones based on temperature, occupancy, and humidity data.

---

## 📁 Project Structure

```
cooling_prediction_project/
├── app.py            # Streamlit dashboard
├── model.py          # Data generation + ML model
├── requirements.txt  # Dependencies
└── README.md         # This file
```

---

## 🚀 Run Instructions

```bash
cd cooling_prediction_project
pip install -r requirements.txt
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## 📊 Dashboard Sections

| Section | Description |
|---|---|
| **Dataset Preview** | KPI metrics + full data table |
| **Cooling Prediction** | Sliders for temperature, occupancy, humidity → instant prediction |
| **Zone Heatmap** | Seaborn heatmap of avg feature intensity per zone |

---

## 🧠 Model Details

- **Algorithm:** Decision Tree Classifier (`max_depth=4`)  
- **Features:** `temperature`, `occupancy`, `humidity`  
- **Target:** `cooling_needed` (0 = No, 1 = Yes)  
- **Split:** 80 % train / 20 % test  

---

## 📂 Custom Dataset (Optional)

Upload a CSV via the sidebar with these columns:

| zone | temperature | occupancy | humidity | cooling_needed |
|------|-------------|-----------|----------|----------------|
| Zone A | 29 | 15 | 60 | 1 |
| Zone B | 23 | 5 | 45 | 0 |

If no file is uploaded, a synthetic 100-row dataset is generated automatically.

---

*Built with Streamlit · Scikit-learn · Seaborn*
