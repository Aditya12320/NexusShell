import requests

class WeatherCommand:
    def __init__(self, shell):
        self.shell = shell
        self.api_key = '03098a5feebc1fd3a3efa36c7025e187'  # Replace with actual API key

    def weather_command(self, args):
        """Fetch weather for a given city"""
        if not args:
            print("Usage: weather -city 'City Name'")
            return

        # Parse city from arguments
        try:
            city_index = args.index('-city')
            city = args[city_index + 1].strip('"')
        except (ValueError, IndexError):
            print("Invalid city specification")
            return

        try:
            # API call to OpenWeatherMap
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric'
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                temp = data['main']['temp']
                condition = data['weather'][0]['description']
                humidity = data['main']['humidity']

                print(f"Weather in {city}:")
                print(f"Temp: {temp}°C")
                print(f"Condition: {condition.capitalize()}")
                print(f"Humidity: {humidity}%")
            else:
                print(f"Error fetching weather: {data.get('message', 'Unknown error')}")
        
        except requests.RequestException as e:
            print(f"Network error: {e}")