from flask import Flask, request, render_template, jsonify
import pickle
import os
import googlemaps
from datetime import datetime
import smtplib

EMAIL_PROVIDER_SMTP_ADDRESS = "smtp.gmail.com"
MY_EMAIL = 'pahasss131313@gmail.com'
MY_PASSWORD = 'gnuqlzfvpsuzwfcn'

API_KEY = 'AIzaSyD52GY-dsG6mjbXSukZIsmuOxE2w3X80iQ'
ORIGIN = 'Tåsenveien 127, 0880'
gmaps = googlemaps.Client(key=API_KEY)

vanskelighet_dict = {"Enkel": 0, "Vanskelig": 0.7, "Trapp": 0.7, "Bratt": 0.7}

app = Flask(__name__)

# prisliste
with open('prisliste_data.pkl', 'rb') as f:
    prisliste_dict = pickle.load(f)

#kalkulerings logikk
def calc(d, n, v):
    diameterpris = prisliste_dict[d]
    if n == 1:
        x = diameterpris
    else:
        x = diameterpris + (n - 1) * diameterpris * 0.5
    y = diameterpris * vanskelighet_dict[v]
    return x + y

def calculate_distance(destination, origin=ORIGIN):
    #kjøreavstand
    directions_result = gmaps.directions(origin,
                                         destination,
                                         mode="driving",
                                         departure_time=datetime.now())
    #avstand variabler
    distance_text = directions_result[0]['legs'][0]['distance']['text']
    distance_val = directions_result[0]['legs'][0]['distance']['value']
    duration = directions_result[0]['legs'][0]['duration']['text']

    return distance_text, distance_val, duration


def final_dist_cost(destination):
    distance ,distance_val, duration = calculate_distance(destination)
    final_cost = (distance_val/1000) * 100     
    return final_cost, distance

def calculate_price(address, postnr, diameter, num_stumps, difficulty):
    final_address = address + ', ' + postnr
    diameter = int(diameter)
    num_stumps = int(num_stumps)
    result_1 = calc(diameter, num_stumps, difficulty)
    dist_cost, distance = final_dist_cost(final_address)
    result = result_1 + dist_cost
    return result, result_1, dist_cost, distance


@app.route('/', methods=['GET'])
def index():
    diameters = list(prisliste_dict.keys())
    diffclts = list(vanskelighet_dict.keys())
    return render_template('index.html', diameters=diameters, diffclts=diffclts)

@app.route('/calculate', methods=['POST'])
def calculate_price_ajax():
    address = request.form['address']
    postnr = request.form['postnr']
    diameter = request.form['diameter']
    num_stumps = request.form['num_stumps']
    difficulty = request.form['difficulty']

    result, result_1, dist_cost, distance = calculate_price(address, postnr, diameter, num_stumps, difficulty)

    return jsonify(price=result, result_1=result_1, dist_cost=dist_cost, distance=distance)



@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.get_json()
    
    name = data['fname']
    ename = data['lname']
    email = data['email']
    phone = data['phone']
    address = data['address']
    postnr = data['postnr']
    diameter = data['diameter']
    num_stumps = data['num_stumps']
    difficulty = data['difficulty']

    result, result_1, dist_cost, distance = calculate_price(address, postnr, diameter, num_stumps, difficulty)

    subject = "Stubbefresing"
    body = f"""
    Hei {name},

    Her er informasjonen om din forespørsel:
    Fornavn: {name}
    Email: {email}
    Telefon: {phone}
    Gateadresse: {address}
    Postnummer: {postnr}
    Diameter: {diameter} cm
    Antall stubber: {num_stumps}
    Tilkomst: {difficulty}
    Stubbefresing kost totalt: {result_1} Kr
    Transportkostnad: {dist_cost} Kr
    Kjørelengde: {distance}
    Estimert totalpris: {result} Kr

    Takk for at du bruker vår priskalkulator!

    Med vennlig hilsen,
    Norsk Trefelling
    """

    email_message = f"Subject: {subject}\n\n{body}".encode('utf-8')

    try:
        with smtplib.SMTP(EMAIL_PROVIDER_SMTP_ADDRESS) as connection:
            connection.starttls()
            connection.login(MY_EMAIL, MY_PASSWORD)
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=[email, MY_EMAIL],
                msg=email_message
            )
        return jsonify(status="Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(status="Error sending email", message=str(e)), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5500))
    app.run(host='0.0.0.0', port=port, debug=True)


