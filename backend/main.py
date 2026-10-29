import math
from datetime import datetime, timedelta, time, timezone
from datetime import date 
import asyncio

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import os

FRONTEND_URL = os.getenv("FRONTEND_URL", "").rstrip("/")

origins = [
    "http://localhost:5173",
    "http://localhost:8080",
    "https://wind-forecast-analysis-7k2m-fronten.vercel.app",
]

if FRONTEND_URL and FRONTEND_URL not in origins:
    origins.append(FRONTEND_URL)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "gridbricks-wind-api",
    }


@app.get("/api/actuals")
async def get_actuals(
    start_date: date = Query(default=date(2026, 1, 1)),
    end_date: date = Query(default=date(2026, 1, 31)),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must not be after end_date",
        )

    # Include a buffer because actuals may be published
    # after their delivery interval.
    params = {
        "publishDateTimeFrom": f"{start_date.isoformat()}T00:00:00Z",
        "publishDateTimeTo": f"{end_date.isoformat()}T23:59:59Z",
    }

    url = f"{BASE_URL}/datasets/FUELHH/stream"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not retrieve Elexon actuals: {exc}",
        ) from exc

    records = data if isinstance(data, list) else data.get("data", [])

    # Filter on delivery date, not publication date.
    records = [
        row for row in records
        if row.get("fuelType") == "WIND"
        and row.get("startTime")
        and start_date.isoformat()
        <= row["startTime"][:10]
        <= end_date.isoformat()
        and row.get("generation") is not None
    ]

    # Keep the latest published version for each interval.
    latest_by_interval = {}

    for row in sorted(
        records,
        key=lambda item: item.get("publishTime", ""),
    ):
        latest_by_interval[row["startTime"]] = row

    results = [
        {
            "startTime": row["startTime"],
            "publishTime": row.get("publishTime"),
            "generation": row["generation"],
        }
        for row in latest_by_interval.values()
    ]

    results.sort(key=lambda row: row["startTime"])

    return {
        "dataset": "FUELHH",
        "fuelType": "WIND",
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "count": len(results),
        "data": results,
    }


@app.get("/api/forecasts")
async def get_forecasts(
    start_date: date = Query(default=date(2026, 1, 1)),
    end_date: date = Query(default=date(2026, 1, 31)),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must not be after end_date",
        )

    params = {
        "publishDateTimeFrom": f"{start_date.isoformat()}T00:00:00Z",
        "publishDateTimeTo": f"{end_date.isoformat()}T23:59:59Z",
    }

    url = f"{BASE_URL}/datasets/WINDFOR/stream"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not retrieve Elexon forecasts: {exc}",
        ) from exc

    records = data if isinstance(data, list) else data.get("data", [])

    # Keep forecasts targeting the requested delivery dates.
    records = [
        {
            "startTime": row["startTime"],
            "publishTime": row["publishTime"],
            "generation": row["generation"],
        }
        for row in records
        if row.get("startTime")
        and row.get("publishTime")
        and row.get("generation") is not None
        and start_date.isoformat()
        <= row["startTime"][:10]
        <= end_date.isoformat()
    ]

    records.sort(
        key=lambda row: (row["startTime"], row["publishTime"])
    )

    return {
        "dataset": "WINDFOR",
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "count": len(records),
        "data": records,
    }


@app.get("/api/analysis")
async def get_analysis(
    start_date: date = Query(default=date(2026, 1, 1)),
    end_date: date = Query(default=date(2026, 1, 31)),
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must not be after end_date",
        )

    if (end_date - start_date).days > 31:
        raise HTTPException(
            status_code=400,
            detail="Please request a date range of 32 days or less.",
        )

    actual_params = {
        "publishDateTimeFrom": f"{start_date.isoformat()}T00:00:00Z",
        "publishDateTimeTo": (
            f"{(end_date + timedelta(days=1)).isoformat()}T23:59:59Z"
        ),
    }

    forecast_params = {
        "publishDateTimeFrom": (
            f"{(start_date - timedelta(days=2)).isoformat()}T00:00:00Z"
        ),
        "publishDateTimeTo": (
            f"{end_date.isoformat()}T23:59:59Z"
        ),
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            actual_response, forecast_response = await asyncio.gather(
                client.get(
                    f"{BASE_URL}/datasets/FUELHH/stream",
                    params=actual_params,
                ),
                client.get(
                    f"{BASE_URL}/datasets/WINDFOR/stream",
                    params=forecast_params,
                ),
            )

            actual_response.raise_for_status()
            forecast_response.raise_for_status()

            actual_data = actual_response.json()
            forecast_data = forecast_response.json()

    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not retrieve analysis data: {exc}",
        ) from exc

    actual_rows = (
        actual_data if isinstance(actual_data, list)
        else actual_data.get("data", [])
    )
    forecast_rows = (
        forecast_data if isinstance(forecast_data, list)
        else forecast_data.get("data", [])
    )

    # Keep the latest published actual for each half-hour interval.
    actuals = {}

    for row in actual_rows:
        start = row.get("startTime")
        generation = row.get("generation")

        if (
            row.get("fuelType") != "WIND"
            or not start
            or generation is None
            or not start_date.isoformat()
            <= start[:10] <= end_date.isoformat()
        ):
            continue

        previous = actuals.get(start)
        published = row.get("publishTime", "")

        if previous is None or published > previous["publishTime"]:
            actuals[start] = {
                "startTime": start,
                "publishTime": published,
                "generation": float(generation),
            }

    # Convert half-hourly actuals to hourly average MW.
    actuals_by_hour = {}

    for row in actuals.values():
        dt = datetime.fromisoformat(
            row["startTime"].replace("Z", "+00:00")
        )
        hour_key = dt.replace(minute=0, second=0, microsecond=0)
        key = hour_key.isoformat().replace("+00:00", "Z")

        actuals_by_hour.setdefault(key, []).append(row["generation"])

    hourly_actuals = {}

    for hour_key, values in actuals_by_hour.items():
        # Require both half-hour readings for a complete hour.
        if len(values) == 2:
            hourly_actuals[hour_key] = round(sum(values) / 2, 2)

    # Select the latest forecast published before the previous-day
    # 09:50 UTC decision cutoff for each hourly delivery interval.
    forecasts = {}

    for row in forecast_rows:
        start = row.get("startTime")
        published = row.get("publishTime")
        generation = row.get("generation")

        if (
            not start
            or not published
            or generation is None
            or not start_date.isoformat()
            <= start[:10] <= end_date.isoformat()
        ):
            continue

        delivery_date = date.fromisoformat(start[:10])
        cutoff = datetime.combine(
            delivery_date - timedelta(days=1),
            time(9, 50),
            tzinfo=timezone.utc,
        )

        try:
            published_dt = datetime.fromisoformat(
                published.replace("Z", "+00:00")
            )
        except ValueError:
            continue

        if published_dt > cutoff:
            continue

        previous = forecasts.get(start)

        if previous is None or published > previous["publishTime"]:
            forecasts[start] = {
                "startTime": start,
                "publishTime": published,
                "generation": float(generation),
            }

    # Compare only identical hourly delivery intervals.
    matched = []

    for start, forecast in sorted(forecasts.items()):
        actual = hourly_actuals.get(start)

        if actual is None:
            continue

        error = forecast["generation"] - actual

        matched.append({
            "startTime": start,
            "forecastPublishTime": forecast["publishTime"],
            "forecast": forecast["generation"],
            "actual": actual,
            "error": round(error, 2),
            "absoluteError": round(abs(error), 2),
        })

    errors = [row["error"] for row in matched]

    metrics = None

    if errors:
        metrics = {
            "maeMW": round(
                sum(abs(error) for error in errors) / len(errors), 2
            ),
            "rmseMW": round(
                math.sqrt(
                    sum(error ** 2 for error in errors) / len(errors)
                ), 2
            ),
            "biasMW": round(sum(errors) / len(errors), 2),
        }

    return {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "decisionCutoff": "09:50 UTC on the previous day",
        "actualHalfHourlyIntervals": len(actuals),
        "completeHourlyActualIntervals": len(hourly_actuals),
        "eligibleForecastIntervals": len(forecasts),
        "matchedIntervals": len(matched),
        "metrics": metrics,
        "data": matched,
        "warning": (
            "Only complete hourly actuals and forecasts published by "
            "the assumed decision cutoff are compared. Verify the cutoff "
            "against the customer's actual decision process."
        ),
    }
