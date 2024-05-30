import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime


class WeatherScraper:
    def __init__(self, url):
        self.url = url

    def fetch_weather_data(self):
        response = requests.get(self.url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        forecast_items = soup.find_all('div', class_='DailyContent--DailyContent--1yRkH"')
        weather_data = []
        for item in forecast_items[:10]:
            date = item.find('h2', class_='DDailyContent--daypartName--3emSU').text
            temp_high = item.find('span', class_='DailyContent--temp--1s3a7">25<span class="DailyContent--degreeSymbol--EbEpi').text
            temp_low = item.find('span', class_='DailyContent--temp--1s3a7 DailyContent--tempN--33RmW').text
            precipitation = "Да" if item.find('span', class_='DetailsSummary--precip--1a9xq') else "Нет"
            wind_speed = item.find('span', class_='Wind--windWrapper--3Ly7c').text
            wind_direction = item.find('span', class_='DailyContent--value--1Jers').text
            weather_data.append((date, temp_low, temp_high, precipitation, wind_speed, wind_direction))
        return weather_data


class WeatherDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS weather
                                (date TEXT, temp_low TEXT, temp_high TEXT, precipitation TEXT, wind_speed TEXT, wind_direction TEXT)''')

    def insert_weather_data(self, weather_data):
        with self.conn:
            self.conn.executemany('INSERT INTO weather VALUES (?, ?, ?, ?, ?, ?)', weather_data)

    def fetch_weather_summary(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute('''SELECT date, MIN(temp_low), MAX(temp_high) FROM weather GROUP BY date''')
            return cur.fetchall()


class DateWeather:
    def __init__(self, date, temp_low, temp_high):
        self.date = date
        self.temp_low = temp_low
        self.temp_high = temp_high

    def __str__(self):
        return f"Date: {self.date}, Min Temp: {self.temp_low}, Max Temp: {self.temp_high}"


def main():
    url = 'https://weather.com/uk-UA/weather/tenday/l/a59084885e0fe4cd572a618fa1f01dc522c6ae0565f4c782b7b8d3a7ca3f7c0c'
    scraper = WeatherScraper(url)
    weather_data = scraper.fetch_weather_data()

    db = WeatherDatabase('weather.db')
    db.insert_weather_data(weather_data)

    weather_summaries = db.fetch_weather_summary()

    weather_objects = [DateWeather(date, temp_low, temp_high) for date, temp_low, temp_high in weather_summaries]

    for weather in weather_objects:
        print(weather)


if __name__ == "__main__":
    main()
