import pandas as pd
import requests
from datetime import datetime

def fetch_weather_data(latitude, longitude, start_date, end_date):
    """
    Fetch historical weather data from Open-Meteo API with additional parameters
    """
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "rain_sum",
            "windspeed_10m_max",
            "winddirection_10m_dominant",
            "weathercode",  # Adding weather condition codes
            "sunrise",
            "sunset",
            "sunshine_duration",  # Hours of sunshine
            "precipitation_hours"  # Hours of precipitation
        ],
        "timezone": "auto"
    }
    
    response = requests.get(base_url, params=params)
    return response.json()

def main():
    # Read your health metrics data from CSV
    health_data = pd.read_csv("health_metrics.csv")
    print("Successfully loaded health data")
    
    # Ensure the date column is in datetime format
    health_data['date'] = pd.to_datetime(health_data['date'], errors='coerce')
    
    # Get the date range from your health data
    start_date = health_data['date'].min()
    end_date = health_data['date'].max()
    
    # For demonstration, using Istanbul's coordinates
    # You'll need to adjust this based on your actual locations
    istanbul_coords = {
        "latitude": 41.0082,
        "longitude": 28.9784
    }
    
    weather_data = fetch_weather_data(
        istanbul_coords["latitude"],
        istanbul_coords["longitude"],
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    
    # Convert the weather data to a DataFrame
    weather_df = pd.DataFrame(weather_data['daily'])
    
    # Save the weather data
    weather_df.to_csv("weather_data.csv", index=False)
    print("Weather data has been saved to weather_data.csv")

if __name__ == "__main__":
    main() 