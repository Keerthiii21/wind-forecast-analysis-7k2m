# Gridbricks — Wind Generation Intelligence

A full-stack energy analytics dashboard that compares Great Britain’s wind generation forecasts with actual generation for January 2026. Built to help energy teams understand forecast accuracy and make better-informed operational decisions.

## Features

- Actual wind generation data from the Elexon BMRS `FUELHH` endpoint, filtered to `WIND`.
- Wind generation forecasts from the Elexon BMRS `WINDFOR` endpoint.
- Hourly forecast-versus-actual comparison.
- Forecast performance metrics:
  - Mean Absolute Error (MAE)
  - Root Mean Square Error (RMSE)
  - Forecast bias
- Interactive daily-average generation chart.
- Daily generation breakdown table with forecast, actual, and forecast gap.
- Date-range filtering.
- Decision insights and comparison methodology.

## Technology Stack

**Frontend**
- React
- TypeScript
- Vite
- Recharts
- CSS

**Backend**
- Python
- FastAPI
- Elexon BMRS API

## Data Sources

The application uses the Elexon BMRS API:

- **Actual generation:** `FUELHH`, filtered to the `WIND` fuel type.
- **Forecast generation:** `WINDFOR`.

The analysis covers the selected date range and aligns actual generation and forecasts to hourly intervals.

## Forecast Comparison Methodology

1. Retrieve half-hourly actual wind generation.
2. Aggregate the two half-hourly actual intervals into an hourly average.
3. Select the latest eligible forecast available before the configured decision cutoff.
4. Match forecast and actual values by hourly interval.
5. Calculate forecast error and performance metrics.

The current implementation assumes a decision cutoff of **09:50 UTC on the previous day**. This is an analytical assumption and should not be interpreted as a verified Gridbricks business rule.

Forecast error is calculated as:

`Forecast − Actual`

- **MAE:** Average absolute forecast error.
- **RMSE:** Square root of the average squared forecast error.
- **Bias:** Average signed forecast error. A positive value indicates over-forecasting on average; a negative value indicates under-forecasting.

## Project Structure

```text
gridbricks-challenge/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   └── App.css
│   ├── package.json
│   └── ...
├── README.md
└── ...
```

## Run Locally

### Prerequisites

- Python 3
- Node.js and npm

### 1. Start the backend

Open a terminal at the project root:

```powershell
cd backend
python -m venv .venv
```

Activate the virtual environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start FastAPI:

```powershell
python -m uvicorn main:app --reload --port 8000
```

The backend will be available at `http://127.0.0.1:8000`.

API health check: `http://127.0.0.1:8000/api/health`

### 2. Start the frontend

Open a second terminal at the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically `http://localhost:5173`.

## Configuration

The frontend currently connects to the local backend at `http://127.0.0.1:8000`.

For deployment, configure the frontend to use the deployed backend URL and ensure the backend CORS settings allow the deployed frontend origin.

## Deployment

Deployment URL: **To be added**

The frontend and backend need to be deployed with their respective configuration and dependencies. Update this section with the live URLs once deployment is complete.

## AI Tool Usage Disclosure

AI assistance was used during development for coding guidance, debugging, UI implementation, and documentation. The application’s data integration, forecast comparison methodology, and results should be reviewed and validated by the developer.

## Limitations

- The decision cutoff is an explicit assumption that should be validated against the intended business requirements.
- Forecast accuracy metrics describe the selected historical period and should not automatically be generalized to other periods.
- Operational decisions should consider additional system conditions and business context.

## Author

Developed as a full-stack software engineering assignment for Gridbricks.
