from flask import Flask, render_template, request
import pickle
import requests
from utils import health_advice

app = Flask(__name__)

# ---------------- LOAD MODEL ----------------
try:
    with open("model/model.pkl", "rb") as f:
        model = pickle.load(f)
    print("✅ Model loaded successfully")

except Exception as e:
    print("❌ Error loading model:", e)
    model = None


# ---------------- API KEY ----------------
API_KEY = "5376c7e5383bd9e554f0c0e200d3ea0f"


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- PREDICT ----------------
@app.route("/predict", methods=["GET", "POST"])
def predict():

    result = None
    advice = None

    city = None
    state = None

    pm25 = pm10 = no2 = co = so2 = o3 = None
    temperature = humidity = weather_desc = None

    if request.method == "POST":

        try:

            city = request.form.get("city")
            state = request.form.get("state")

            # ---------------- GET LATITUDE & LONGITUDE ----------------

            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},IN&limit=1&appid={API_KEY}"

            geo_response = requests.get(geo_url).json()

            if len(geo_response) == 0:

                return render_template(
                    "predict.html",
                    result=None,
                    advice="❌ City not found",
                    city=city,
                    state=state
                )

            lat = geo_response[0]["lat"]
            lon = geo_response[0]["lon"]

            # ---------------- LIVE AQI API ----------------

            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"

            aqi_response = requests.get(aqi_url).json()

            components = aqi_response["list"][0]["components"]

            pm25 = components.get("pm2_5", 0)
            pm10 = components.get("pm10", 0)
            no2 = components.get("no2", 0)
            co = components.get("co", 0)
            so2 = components.get("so2", 0)
            o3 = components.get("o3", 0)

            # ---------------- AQI PREDICTION ----------------

            if model:

                input_data = [[
                    pm25,
                    pm10,
                    no2,
                    co,
                    so2,
                    o3
                ]]

                result = int(model.predict(input_data)[0])

            else:
                result = 100

            # ---------------- HEALTH ADVICE ----------------

            advice = health_advice(result)

            # ---------------- WEATHER API ----------------

            weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

            weather_response = requests.get(weather_url).json()

            if "main" in weather_response:

                temperature = weather_response["main"]["temp"]
                humidity = weather_response["main"]["humidity"]
                weather_desc = weather_response["weather"][0]["description"]

        except Exception as e:

            print("❌ Prediction Error:", e)

            advice = "Error fetching AQI data"

    return render_template(

        "predict.html",

        result=result,
        advice=advice,

        city=city,
        state=state,

        pm25=pm25,
        pm10=pm10,
        no2=no2,
        co=co,
        so2=so2,
        o3=o3,

        temperature=temperature,
        humidity=humidity,
        weather_desc=weather_desc
    )
# ---------------- ANALYTICS ----------------
@app.route("/analytics", methods=["GET", "POST"])
def analytics():

    dates = None
    aqi_values = None
    selected_city = None
    selected_state = None

    if request.method == "POST":

        selected_city = request.form.get("city")
        selected_state = request.form.get("state")

        # 7 days
        dates = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Different AQI graph data for every capital city
        city_aqi_data = {

            "Amaravati": [95, 100, 105, 110, 108, 102, 98],
            "Itanagar": [45, 50, 48, 52, 55, 50, 47],
            "Dispur": [70, 75, 80, 82, 78, 74, 72],
            "Patna": [220, 230, 240, 250, 245, 238, 225],
            "Raipur": [130, 135, 140, 145, 142, 138, 132],
            "Panaji": [40, 42, 45, 43, 41, 39, 40],
            "Gandhinagar": [120, 125, 130, 135, 132, 128, 122],
            "Chandigarh": [150, 155, 160, 165, 158, 152, 148],
            "Shimla": [35, 38, 40, 42, 39, 36, 35],
            "Ranchi": [140, 145, 150, 155, 148, 142, 138],
            "Bangalore": [70, 75, 80, 78, 72, 69, 74],
            "Thiruvananthapuram": [50, 52, 55, 58, 56, 53, 50],
            "Bhopal": [120, 125, 130, 128, 122, 118, 115],
            "Mumbai": [140, 150, 155, 160, 145, 138, 142],
            "Imphal": [55, 58, 60, 62, 59, 56, 54],
            "Shillong": [35, 38, 40, 42, 39, 37, 35],
            "Aizawl": [30, 32, 35, 36, 34, 31, 30],
            "Kohima": [40, 42, 45, 47, 44, 41, 40],
            "Bhubaneswar": [110, 115, 120, 125, 122, 118, 112],
            "Jaipur": [130, 140, 145, 150, 148, 142, 135],
            "Gangtok": [28, 30, 32, 35, 33, 30, 28],
            "Chennai": [95, 100, 105, 110, 108, 102, 98],
            "Hyderabad": [100, 105, 110, 115, 108, 102, 98],
            "Agartala": [60, 62, 65, 68, 66, 63, 60],
            "Lucknow": [180, 190, 200, 210, 205, 195, 185],
            "Dehradun": [85, 88, 90, 92, 89, 86, 84],
            "Kolkata": [160, 165, 170, 175, 168, 162, 158],
            "New Delhi": [250, 270, 260, 280, 300, 290, 275]

        }

        # Get AQI graph according to selected city
        aqi_values = city_aqi_data.get(
            selected_city,
            [80, 85, 90, 88, 84, 82, 80]
        )

    return render_template(

        "analytics.html",

        dates=dates,
        aqi_values=aqi_values,

        selected_city=selected_city,
        selected_state=selected_state

    )



    
        # ---------------- RUN ----------------
if __name__ == "__main__":

    print("🚀 Flask server started")

    app.run(debug=True)