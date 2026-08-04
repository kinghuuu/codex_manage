"""天气查询服务：使用 Open-Meteo 公共接口，无需申请 API Key"""
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.utils.cache_conf import get_json_cache, set_cache
from app.utils.logger import get_logger

logger = get_logger(__name__)

GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CACHE_PREFIX = "tools:weather:"
WEATHER_CACHE_TTL = 600
REQUEST_TIMEOUT = 10.0

# WMO 天气代码 -> 中文描述
WEATHER_CODE_TEXT = {
    0: "晴",
    1: "大部晴朗",
    2: "局部多云",
    3: "阴",
    45: "雾",
    48: "雾凇",
    51: "小毛毛雨",
    53: "毛毛雨",
    55: "强毛毛雨",
    56: "冻毛毛雨",
    57: "强冻毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "冻雨",
    67: "强冻雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "米雪",
    80: "小阵雨",
    81: "阵雨",
    82: "强阵雨",
    85: "小阵雪",
    86: "强阵雪",
    95: "雷暴",
    96: "雷暴伴小冰雹",
    99: "雷暴伴大冰雹",
}


def _get_weather_text(weather_code: int | None) -> str:
    return WEATHER_CODE_TEXT.get(weather_code, "未知")


async def _get_city_location(city: str) -> dict[str, Any] | None:
    """通过 Open-Meteo 地理编码接口获取城市坐标。"""
    params = {
        "name": city,
        "count": 1,
        "language": "zh",
        "format": "json",
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(GEOCODING_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        logger.error("城市定位失败: city=%s, error=%s", city, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="天气服务暂时不可用，请稍后重试",
        ) from exc

    results = data.get("results") or []
    if not results:
        return None

    location = results[0]
    latitude = location.get("latitude")
    longitude = location.get("longitude")
    if latitude is None or longitude is None:
        return None

    return {
        "city": location.get("name") or city,
        "region": location.get("admin1") or location.get("admin2"),
        "country": location.get("country"),
        "latitude": latitude,
        "longitude": longitude,
        "timezone": location.get("timezone", "auto"),
    }


async def _fetch_weather_data(location: dict[str, Any]) -> dict[str, Any]:
    """根据城市坐标获取实时天气和未来三天预报。"""
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,"
            "precipitation,weather_code,wind_speed_10m,wind_direction_10m,surface_pressure"
        ),
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,sunrise,sunset,uv_index_max"
        ),
        "forecast_days": 3,
        "timezone": location["timezone"],
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(WEATHER_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        logger.error("天气查询失败: city=%s, error=%s", location["city"], exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="天气服务暂时不可用，请稍后重试",
        ) from exc

    if not isinstance(data, dict) or not data.get("current"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="天气服务返回数据异常，请稍后重试",
        )

    return data


def _format_weather_data(
        location: dict[str, Any],
        weather_data: dict[str, Any],
) -> dict[str, Any]:
    """把 Open-Meteo 返回数据整理成前端友好的驼峰结构。"""
    current = weather_data.get("current") or {}
    current_units = weather_data.get("current_units") or {}
    daily = weather_data.get("daily") or {}

    forecast_days = []
    for date, weather_code, temp_max, temp_min, precip_probability, sunrise, sunset, uv_index in zip(
        daily.get("time", []),
        daily.get("weather_code", []),
        daily.get("temperature_2m_max", []),
        daily.get("temperature_2m_min", []),
        daily.get("precipitation_probability_max", []),
        daily.get("sunrise", []),
        daily.get("sunset", []),
        daily.get("uv_index_max", []),
    ):
        forecast_days.append(
            {
                "date": date,
                "weatherCode": weather_code,
                "weatherText": _get_weather_text(weather_code),
                "temperatureMax": temp_max,
                "temperatureMin": temp_min,
                "precipitationProbabilityMax": precip_probability,
                "sunrise": sunrise,
                "sunset": sunset,
                "uvIndexMax": uv_index,
            }
        )

    return {
        "city": location["city"],
        "region": location.get("region"),
        "country": location.get("country"),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "timezone": location["timezone"],
        "current": {
            "time": current.get("time"),
            "weatherCode": current.get("weather_code"),
            "weatherText": _get_weather_text(current.get("weather_code")),
            "temperature": current.get("temperature_2m"),
            "temperatureUnit": current_units.get("temperature_2m", "°C"),
            "feelsLike": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "precipitationUnit": current_units.get("precipitation", "mm"),
            "windSpeed": current.get("wind_speed_10m"),
            "windDirection": current.get("wind_direction_10m"),
            "pressure": current.get("surface_pressure"),
            "isDay": bool(current.get("is_day")),
        },
        "daily": forecast_days,
    }


async def query_weather(city: str) -> dict[str, Any]:
    """查询城市天气，优先读取缓存，未命中时调用第三方接口。"""
    cache_key = f"{WEATHER_CACHE_PREFIX}{city}"
    cached = await get_json_cache(cache_key)
    if cached:
        return cached

    location = await _get_city_location(city)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该城市，请检查城市名称",
        )

    weather_data = await _fetch_weather_data(location)
    data = _format_weather_data(location, weather_data)

    await set_cache(cache_key, data, WEATHER_CACHE_TTL)
    return data
