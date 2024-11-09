from flask import Flask, request, render_template, jsonify
import os
import smtplib
from calc import Calculator



EMAIL_PROVIDER_SMTP_ADDRESS = "smtp.gmail.com"
MY_EMAIL = 'Trefg.app@gmail.com'
MY_PASSWORD = 'vffl lhwv iogl novp'

app = Flask(__name__)
calculator = Calculator()


def calculate_price(address, postnr, diameter, num_stumps, difficulty):
    """
    Beregner den totale kostnaden for stubbefresing inkludert transportkostnad.

    Parametere:
    address (str): Gateadresse for hvor stubbene skal fjernes.
    postnr (str): Postnummeret til adressen.
    diameter (str): Diameteren på stubben i cm.
    num_stumps (str): Antall stubber som skal fjernes.
    difficulty (str): Vanskelighetsgraden på tilkomsten (Enkel, Vanskelig, Trapp, Bratt).

    Returnerer:
    tuple: En tuple bestående av total kostnad (float), jobb kostnad (float), kjøre kostnad (float), og distanse tekst (str).
    """
    country = "Norway"
    final_address = address + ', ' + postnr + ', ' + country
    calculator.calc(int(diameter), int(num_stumps), difficulty)
    distanse ,_ ,_ = calculator.distance_calc(final_address) # _, _ = distanse_variabel og estimert tid (muligens brukbart senere) 
    jobb_kostnad = calculator.result_job
    if int(postnr) in calculator.postnr:
        kjore_kostnad = round(calculator.result_vei * 0.5) #hvis postnummeret er i den oppgitte listen halveres kjørekostnaden.ç
    else:
        kjore_kostnad = round(calculator.result_vei)
    result = jobb_kostnad + kjore_kostnad
    return result, jobb_kostnad, kjore_kostnad, distanse


@app.route('/', methods=['GET'])
def index():
    diameters = list(calculator.prisliste_dict.keys())
    diffclts = list(calculator.vanskelighet_dict.keys())
    return render_template('index.html', diameters=diameters, diffclts=diffclts)

@app.route('/calculate', methods=['POST'])
def calculate_price_ajax():
    address = request.form['address']
    postnr = request.form['postnr']
    diameter = request.form['diameter']
    num_stumps = request.form['num_stumps']
    difficulty = request.form['difficulty']

    result, jobb_kostnad, kjore_kostnad, distanse = calculate_price(address, postnr, diameter, num_stumps, difficulty)

    return jsonify(price=result, result_1=jobb_kostnad, dist_cost=kjore_kostnad, distance=distanse)


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

    #result, result_1, dist_cost, distance = calculate_price(address, postnr, diameter, num_stumps, difficulty)
    print(postnr, address)
    #body = calculator.create_email_body(data, result, result_1, dist_cost, distance)
    subject = "Stubbefresing"
    

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


