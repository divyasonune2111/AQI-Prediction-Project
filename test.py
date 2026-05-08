import requests

api_key = "5376c7e5383bd9e554f0c0e200d3ea0f"
city = "Pune"

url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

response = requests.get(url)
print(response.json())