# UK Wind Generation Forecast Accuracy — January 2026

A full-stack data analysis dashboard for evaluating UK wind generation forecasts against actual wind generation. Built as part of the Gridbricks Full Stack Software Engineer assignment.

## Overview

The application retrieves wind generation actuals and forecasts from the Elexon BMRS API, aligns the data by delivery interval, and calculates forecast error metrics for January 2026.

It provides an interactive dashboard to help energy analysts understand forecast performance, identify discrepancies between predicted and actual generation, and explore daily trends.

## Features

- **Forecast accuracy metrics:** Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and forecast bias.
- **Actual vs. forecast chart:** Compare hourly wind generation actuals and forecasts.
- **Date filtering:** Explore the available date range.
- **Daily summary:** Review daily average generation and forecast performance.
- **Decision insight:** Interpret forecast bias and error in operational terms.
- **Backend API:** Python endpoints for health checks, actuals, forecasts, and analysis.
- **Container support:** Dockerfiles for the frontend and backend.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite, Recharts |
| Backend | Python, FastAPI |
| Data processing | Pandas, NumPy |
| HTTP requests | HTTPX |
| Data source | Elexon BMRS API |
| Deployment | Docker; frontend and backend can be deployed separately |

## Data Source

The application uses the Elexon BMRS API:

- Actual generation: `FUELHH`, filtered to `WIND`.
- Wind generation forecasts: `WINDFOR`.

API base URL: https://data.elexon.co.uk/bmrs/api/v1

The data is retrieved from the external API rather than being hard-coded into the dashboard.

## Forecast Evaluation Methodology

1. Retrieve half-hourly actual wind generation for January 2026.
2. Retrieve the available wind forecast records for the corresponding delivery intervals.
3. Aggregate two half-hourly actual readings into hourly values.
4. Select the latest eligible forecast published before the configured forecast cutoff.
5. Match forecast and actual generation by delivery interval.
6. Calculate forecast error metrics over matched intervals.

### Metrics

- **MAE:** Average absolute difference between forecast and actual generation, measured in MW. Lower is better.
- **RMSE:** Square root of the average squared forecast error, measured in MW. This penalises larger errors more heavily.
- **Bias:** Average signed forecast error, calculated as forecast minus actual. Positive bias indicates over-forecasting; negative bias indicates under-forecasting.

### January 2026 Results

The current local analysis produced the following results:

| Metric | Result |
|---|---:|
| Matched hourly intervals | 744 |
| MAE | 2,122.81 MW |
| RMSE | 2,616.69 MW |
| Forecast bias | +1,840.30 MW |

These values are outputs of the current implementation and should be interpreted alongside the methodology and its assumptions.

**Important cutoff assumption:** The implementation uses 09:50 UTC on the preceding day as the forecast publication cutoff. This is an analytical assumption, not a verified Gridbricks business rule. It should be confirmed against the intended forecasting workflow before the results are used for operational decisions.

## Project Structure

```text
gridbricks-challenge/
├── backend/
│   ├── main.py
│   ├── test_main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   └── .dockerignore
├── .gitignore
└── README.md
```

## Local Setup

### Prerequisites

- Python 3.11 or newer
- Node.js and npm
- Internet access to retrieve Elexon API data

### 1. Start the backend

Open a terminal in the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Backend health check:

http://127.0.0.1:8000/api/health

Interactive API documentation:

http://127.0.0.1:8000/docs

### 2. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
```

Create a `frontend/.env.local` file containing:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the development server:

```powershell
npm run dev
```

Open the local URL printed by Vite, typically:

http://localhost:5173

### 3. Run backend tests

From the project root:

```powershell
cd backend
python -m pytest -v
```

The tests cover the health endpoint and validation of invalid or excessive date ranges.

### 4. Build the frontend

From the `frontend` directory:

```powershell
npm run build
```

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Backend health check |
| `GET /api/actuals` | Retrieve actual wind generation data |
| `GET /api/forecasts` | Retrieve wind forecast data |
| `GET /api/analysis` | Calculate forecast accuracy metrics |

The analysis, actuals, and forecast endpoints support date-range parameters. Refer to the interactive API documentation at `/docs` for the implemented parameter definitions.

## Deployment

The frontend and backend are designed to be deployed separately.

- **Frontend:** Vercel or another static frontend hosting provider.
- **Backend:** A Python-compatible hosting provider that supports FastAPI.
- **Configuration:** Set `VITE_API_URL` to the deployed backend URL when building the frontend, and set `FRONTEND_URL` on the backend to the deployed frontend origin for CORS.

Deployment URLs will be added here after deployment is completed and verified.

## Limitations and Future Improvements

- Confirm the forecast publication cutoff with the intended business requirements.
- Validate timestamp alignment, forecast selection, and aggregation rules against the official API definitions.
- Add explicit handling and reporting for missing intervals and incomplete API responses.
- Add integration tests for external API data and edge cases.
- Consider pagination, caching, and API response monitoring for production use.
- Add automated deployment and continuous integration.

## AI Tool Usage Disclosure

AI assistance was used during development for coding guidance, debugging, test creation, documentation, and implementation review. The application was run and tested locally, and the developer reviewed and integrated the generated suggestions.

## Author

Developed as a Full Stack Software Engineer assignment project for Gridbricks.
