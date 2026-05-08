def health_advice(aqi):
    if aqi <= 50:
        return "Good: Air is safe 😊"
    elif aqi <= 100:
        return "Moderate: Sensitive people take care"
    elif aqi <= 200:
        return "Poor: Avoid outdoor activities"
    elif aqi <= 300:
        return "Very Poor: Wear mask"
    else:
        return "Severe: Stay indoors"