import requests
import pandas as pd
from urllib.parse import quote

def fetch_weather_data(city, api_key):
    """
    Lấy dữ liệu thời tiết từ OpenWeatherMap API cho các khung giờ cụ thể.
    """
    city_encoded = quote(city)
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_encoded}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_list = data["list"]

        # Lọc các khung giờ cụ thể (3h, 6h, 9h, 12h)
        filtered_data = [
            {
                "timestamp": entry["dt_txt"],
                "temperature": entry["main"]["temp"],
                "temperature_min": entry["main"]["temp_min"],
                "temperature_max": entry["main"]["temp_max"],
                "humidity": entry["main"]["humidity"],
                "pressure": entry["main"]["pressure"]
            }
            for entry in weather_list
            if pd.Timestamp(entry["dt_txt"]).hour in [3, 6, 9, 12]
        ]

        # Tạo DataFrame từ dữ liệu đã lọc
        return pd.DataFrame(filtered_data)
    else:
        raise Exception(f"API Error: {response.status_code}, {response.json()}")
