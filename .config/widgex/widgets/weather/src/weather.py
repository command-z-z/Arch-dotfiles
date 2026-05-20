#!/usr/bin/env python3
"""Weather JSON source using Open-Meteo API (free, no key required)."""
import json
import subprocess
import sys
from datetime import datetime
from urllib.parse import quote

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search?name={}&count=1&language=en&format=json"
FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&current=temperature_2m,weathercode,is_day,windspeed_10m,relativehumidity_2m"
    "&hourly=temperature_2m,weathercode,is_day"
    "&daily=weathercode,temperature_2m_max,temperature_2m_min"
    "&forecast_days=5&timezone=auto"
)

# WMO weather code → icon (daytime)
ICON_DAY = {
    0: "☀", 1: "☀", 2: "☁", 3: "☁",
    45: "≋", 48: "≋",
    51: "☂", 53: "☂", 55: "☂", 56: "☂", 57: "☂",
    61: "☂", 63: "☂", 65: "☂", 66: "☂", 67: "☂",
    71: "❄", 73: "❄", 75: "❄", 77: "❄",
    80: "☂", 81: "☂", 82: "☂",
    85: "❄", 86: "❄",
    95: "⚡", 96: "⚡", 99: "⚡",
}

# Night overrides — only clear sky shows moon, rest same as day
ICON_NIGHT = {0: "☽", 1: "☽"}

ICON_COLOR_DEFAULT = "var(--ctp-overlay2)"
ICON_COLOR_DAY = {
    0: "var(--ctp-yellow)", 1: "var(--ctp-yellow)",
    2: "var(--ctp-sky)", 3: "var(--ctp-blue)",
    45: "var(--ctp-overlay2)", 48: "var(--ctp-overlay2)",
    51: "var(--ctp-sapphire)", 53: "var(--ctp-sapphire)", 55: "var(--ctp-sapphire)",
    56: "var(--ctp-sapphire)", 57: "var(--ctp-sapphire)",
    61: "var(--ctp-sapphire)", 63: "var(--ctp-sapphire)", 65: "var(--ctp-sapphire)",
    66: "var(--ctp-sapphire)", 67: "var(--ctp-sapphire)",
    71: "var(--ctp-teal)", 73: "var(--ctp-teal)", 75: "var(--ctp-teal)", 77: "var(--ctp-teal)",
    80: "var(--ctp-sapphire)", 81: "var(--ctp-sapphire)", 82: "var(--ctp-sapphire)",
    85: "var(--ctp-teal)", 86: "var(--ctp-teal)",
    95: "var(--ctp-peach)", 96: "var(--ctp-peach)", 99: "var(--ctp-peach)",
}
ICON_COLOR_NIGHT = {0: "var(--ctp-yellow)", 1: "var(--ctp-yellow)"}

WMO_DESC = {
    0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Fog", 48: "Fog",
    51: "Light Drizzle", 53: "Drizzle", 55: "Heavy Drizzle",
    56: "Freezing Drizzle", 57: "Freezing Drizzle",
    61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
    66: "Freezing Rain", 67: "Freezing Rain",
    71: "Light Snow", 73: "Snow", 75: "Heavy Snow", 77: "Snow",
    80: "Showers", 81: "Showers", 82: "Heavy Showers",
    85: "Snow Showers", 86: "Snow Showers",
    95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
}


def fetch_json(url):
    out = subprocess.check_output(
        ["curl", "-fsS", "--max-time", "6", url],
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return json.loads(out)


def weather_icon(code, is_day=1):
    if not is_day and code in ICON_NIGHT:
        return ICON_NIGHT[code]
    return ICON_DAY.get(code, "≋")

def weather_icon_color(code, is_day=1):
    if not is_day and code in ICON_COLOR_NIGHT:
        return ICON_COLOR_NIGHT[code]
    return ICON_COLOR_DAY.get(code, ICON_COLOR_DEFAULT)


def fallback(message="Weather unavailable"):
    result = {
        "icon": "≋", "icon_color": ICON_COLOR_DEFAULT, "temp": "--°", "condition": message,
        "place": "Local weather", "range": "H --°  L --°",
        "wind": "Wind --", "humidity": "Humidity --",
    }
    for i in range(1, 6):
        result[f"hour{i}_time"] = "--:--"
        result[f"hour{i}_icon"] = "≋"
        result[f"hour{i}_icon_color"] = ICON_COLOR_DEFAULT
        result[f"hour{i}_temp"] = "--°"
    for i in range(1, 6):
        result[f"day{i}_name"] = "---"
        result[f"day{i}_icon"] = "≋"
        result[f"day{i}_icon_color"] = ICON_COLOR_DEFAULT
        result[f"day{i}_low"] = "--°"
        result[f"day{i}_high"] = "--°"
        result[f"day{i}_bar_start"] = "10"
        result[f"day{i}_bar_end"] = "90"
    return result


def arg_value(flag):
    try:
        index = sys.argv.index(flag)
        return sys.argv[index + 1]
    except (ValueError, IndexError):
        return ""


def main():
    location = next((a for a in sys.argv[1:] if not a.startswith("--") and a != arg_value("--label")), "Shanghai")
    display_label = arg_value("--label")
    debug = "--debug" in sys.argv

    try:
        # Step 1: geocode city name → lat/lon
        geo = fetch_json(GEOCODE_URL.format(quote(location)))
        geo_res = geo["results"][0]
        lat = geo_res["latitude"]
        lon = geo_res["longitude"]
        city = geo_res.get("name", location)
        admin = geo_res.get("admin1", "")
        place_label = display_label or (f"{city}, {admin}" if admin else city)

        # Step 2: fetch forecast
        data = fetch_json(FORECAST_URL.format(lat=lat, lon=lon))

        # Current conditions
        current = data["current"]
        curr_code = current["weathercode"]
        curr_is_day = current["is_day"]
        curr_temp = round(current["temperature_2m"])
        wind = round(current["windspeed_10m"])
        humidity = current["relativehumidity_2m"]

        # Today's high/low from daily[0]
        daily = data["daily"]
        today_max = round(daily["temperature_2m_max"][0])
        today_min = round(daily["temperature_2m_min"][0])

        result = {
            "icon": weather_icon(curr_code, curr_is_day),
            "icon_color": weather_icon_color(curr_code, curr_is_day),
            "temp": f"{curr_temp}°",
            "condition": WMO_DESC.get(curr_code, "Weather"),
            "place": place_label,
            "range": f"H {today_max}°  L {today_min}°",
            "wind": f"Wind {wind} km/h",
            "humidity": f"Humidity {humidity}%",
        }

        # Next 5 individual hours (true hourly data)
        hourly = data["hourly"]
        times = hourly["time"]
        h_temps = hourly["temperature_2m"]
        h_codes = hourly["weathercode"]
        h_is_day = hourly["is_day"]

        now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
        try:
            start = times.index(now_str) + 1
        except ValueError:
            now_prefix = datetime.now().strftime("%Y-%m-%dT%H")
            start = next((i for i, t in enumerate(times) if t >= now_prefix), 0) + 1

        entries = []
        for i in range(start, min(start + 5, len(times))):
            entries.append({
                "time": times[i][11:16],  # "HH:MM"
                "icon": weather_icon(h_codes[i], h_is_day[i]),
                "icon_color": weather_icon_color(h_codes[i], h_is_day[i]),
                "temp": f"{round(h_temps[i])}°",
            })

        for n in range(1, 6):
            e = entries[n - 1] if n - 1 < len(entries) else {}
            result[f"hour{n}_time"] = e.get("time", "--:--")
            result[f"hour{n}_icon"] = e.get("icon", "≋")
            result[f"hour{n}_icon_color"] = e.get("icon_color", ICON_COLOR_DEFAULT)
            result[f"hour{n}_temp"] = e.get("temp", "--°")

        # 3-day daily forecast with normalised temperature bar
        d_codes = daily["weathercode"]
        d_maxs = [round(v) for v in daily["temperature_2m_max"][:5]]
        d_mins = [round(v) for v in daily["temperature_2m_min"][:5]]
        d_times = daily["time"]

        g_min = min(d_mins)
        g_max = max(d_maxs)
        span = max(g_max - g_min, 1)

        for i in range(5):
            n = i + 1
            try:
                name = datetime.strptime(d_times[i], "%Y-%m-%d").strftime("%a")
            except Exception:
                name = "---"
            bar_start = int((d_mins[i] - g_min) / span * 100)
            bar_end = int((d_maxs[i] - g_min) / span * 100)
            result[f"day{n}_name"] = name
            result[f"day{n}_icon"] = weather_icon(d_codes[i], 1)
            result[f"day{n}_icon_color"] = weather_icon_color(d_codes[i], 1)
            result[f"day{n}_low"] = f"{d_mins[i]}°"
            result[f"day{n}_high"] = f"{d_maxs[i]}°"
            result[f"day{n}_bar_start"] = str(bar_start)
            result[f"day{n}_bar_end"] = str(bar_end)

    except Exception as e:
        result = fallback(str(e) if debug else "Weather unavailable")

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
