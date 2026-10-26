
import asyncio
import json
import httpx

print("Elexon inspection script started", flush=True)

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"

START = "2025-12-31T23:00:00Z"
END = "2026-02-01T01:00:00Z"


def print_date_ranges(records):
    for field in ("publishTime", "startTime"):
        values = [row[field] for row in records if row.get(field)]
        if values:
            print(f"{field} range: {min(values)} to {max(values)}")


async def inspect_dataset(name: str):
    url = f"{BASE_URL}/datasets/{name}/stream"
    params = {
        "publishDateTimeFrom": START,
        "publishDateTimeTo": END,
    }

    print(f"\n--- Inspecting {name} ---")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(url, params=params)
            print("HTTP status:", response.status_code)
            response.raise_for_status()
            data = response.json()

        records = data if isinstance(data, list) else data.get("data", [])

        print("Records returned:", len(records))

        if name == "FUELHH":
            records = [
                row for row in records
                if row.get("fuelType") == "WIND"
                and "2026-01-01" <= row.get("startTime", "")[:10] <= "2026-01-31"
            ]

            # Keep the latest published record for each delivery interval.
            latest_by_interval = {}

            for row in sorted(
                records,
                key=lambda item: item.get("publishTime", "")
            ):
                latest_by_interval[row["startTime"]] = row

            records = sorted(
                latest_by_interval.values(),
                key=lambda item: item["startTime"]
            )

        print("Records after filtering:", len(records))
        print_date_ranges(records)

        if records:
            print("First record:")
            print(json.dumps(records[0], indent=2))
            print("Last record:")
            print(json.dumps(records[-1], indent=2))
        else:
            print("No matching records.")

    except (httpx.HTTPError, ValueError) as exc:
        print(f"Request failed: {exc}")


async def main():
    await inspect_dataset("FUELHH")
    await inspect_dataset("WINDFOR")


if __name__ == "__main__":
    asyncio.run(main())
