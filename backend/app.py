from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from geopy.geocoders import Nominatim
import folium
from langchain_community.llms import Ollama
from langchain_community.tools import DuckDuckGoSearchRun
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)
CORS(app)

# --- CORSIG ---
OLLAMA_MODEL = "llama3.1:8b"
FEMA_API_URL = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"

# --- Helper: Haversine Distance ---
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3958.8  # Radius of Earth in miles
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# --- 1. Convert Address to Coordinates ---
def geocode_address(address):
    geolocator = Nominatim(user_agent="property_risk_app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude, location.address
    else:
        return None, None, None

# --- 2. Get FEMA Disaster History Near Property ---
def get_fema_disasters(lat, lon, radius_miles=50):
    params = {
        "$format": "json",
        "$top": 5000
    }
    response = requests.get(FEMA_API_URL, params=params)
    data = response.json()

    disasters = []
    if 'DisasterDeclarationsSummaries' in data:
        for d in data['DisasterDeclarationsSummaries']:
            try:
                d_lat = float(d.get('designatedAreaLatitude', 0))
                d_lon = float(d.get('designatedAreaLongitude', 0))
                if d_lat == 0 or d_lon == 0:
                    continue

                distance = haversine_distance(lat, lon, d_lat, d_lon)
                if distance <= radius_miles:
                    disasters.append({
                        'disasterType': d['incidentType'],
                        'title': d['declarationTitle'],
                        'date': d['incidentBeginDate'],
                        'distance_miles': round(distance, 1)
                    })
            except Exception as e:
                continue

    return disasters

# --- 3. Perform Web Search about Disasters ---
def search_disasters(address):
    search = DuckDuckGoSearchRun()
    query = f"{address} flood disaster OR storm damage OR wildfire OR earthquake OR other diaster that affects the property"
    results = search.run(query)
    return results

# --- 4. Summarize Risk Using Ollama ---
def summarize_risk(full_address, fema_disasters, search_results):
    llm = Ollama(model=OLLAMA_MODEL)
    fema_text = "\n".join([f"- {d['disasterType']} at {d['distance_miles']} miles ({d['date']})" for d in fema_disasters])

    prompt = f"""
You are an insurance risk analyst.

Assess the property at {full_address}.

Here is FEMA disaster data nearby:
{fema_text if fema_text else 'No FEMA disasters found.'}

And here are real-time web search results:
{search_results}

Tasks:
- Identify major risks (flood, storm, wildfire, etc.)
- Rate overall risk (Low, Medium, High)
- Provide underwriting recommendations (exclusions, premium loading, etc.)

Summary:
"""
    response = llm.invoke(prompt)
    return response

@app.route('/api/analyze', methods=['POST'])
def analyze():
    
    data = request.json
    address = data.get('address')
    print(address)
    if not address:
        return jsonify({"error": "Address is required"}), 400
    
    try:
        # Geocode address
        lat, lon, full_address = geocode_address(address)
        if not lat:
            return jsonify({"error": "Address not found"}), 404
        
        # Get FEMA disasters
        fema_disasters = get_fema_disasters(lat, lon)
        
        # Search web for additional info
        search_results = search_disasters(full_address)
        
        # Summarize risk
        risk_summary = summarize_risk(full_address, fema_disasters, search_results)
        
        # Return results
        return jsonify({
            "coordinates": {"lat": lat, "lon": lon},
            "fullAddress": full_address,
            "femaDisasters": fema_disasters,
            "riskSummary": risk_summary
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/hello')
def hello():
    return {"Hello": "World"}
if __name__ == "__main__":
    
    app.run(debug=True, port=5555, host="0.0.0.0")