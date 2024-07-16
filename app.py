from flask import Flask, request, render_template, jsonify
import pickle
import os
import googlemaps
from datetime import datetime

API_KEY = 'AIzaSyD52GY-dsG6mjbXSukZIsmuOxE2w3X80iQ'
ORIGIN = 'Tåsenveien 127, 0880'
gmaps = googlemaps.Client(key=API_KEY)

app = Flask(__name__)

# Load prisliste_dict from pickle file
with open('prisliste_data.pkl', 'rb') as f:
    prisliste_dict = pickle.load(f)

vanskelighet_dict = {"Enkel": 0, "Vanskelig": 0.7, "Trapp": 0.7, "Bratt": 0.7}

def calc(d, n, v):
    diameterpris = prisliste_dict[d]
    if n == 1:
        x = diameterpris
    else:
        x = diameterpris + (n - 1) * diameterpris * 0.5
    y = diameterpris * vanskelighet_dict[v]
    return x + y

def calculate_distance(destination, origin=ORIGIN):
    # Request directions via driving
    directions_result = gmaps.directions(origin,
                                         destination,
                                         mode="driving",
                                         departure_time=datetime.now())
    # Extract distance
    distance_text = directions_result[0]['legs'][0]['distance']['text']
    distance_val = directions_result[0]['legs'][0]['distance']['value']
    duration = directions_result[0]['legs'][0]['duration']['text']

    return distance_text, distance_val, duration


def final_dist_cost(destination):
    distance ,distance_val, duration = calculate_distance(destination)
    final_cost = (distance_val/1000) * 100     
    return final_cost, distance


@app.route('/', methods=['GET'])
def index():
    diameters = list(prisliste_dict.keys())
    diffclts = list(vanskelighet_dict.keys())
    return render_template('index.html', diameters=diameters, diffclts=diffclts)

@app.route('/calculate', methods=['POST'])
def calculate_price_ajax():
    adr = request.form['address']
    post = request.form['postnr']
    final_adress = adr + ', ' + post
    diameter = int(request.form['diameter'])
    n = int(request.form['num_stumps'])
    difficulty = request.form['difficulty']
    result_1 = calc(diameter, n, difficulty)
    dist_cost, distance = final_dist_cost(final_adress)
    result = result_1 + dist_cost

    return jsonify(price=result, result_1=result_1, dist_cost=dist_cost, distance=distance)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


