from flask import Flask, request, render_template, jsonify
import os
import smtplib
from calc import Calculator

EMAIL_PROVIDER_SMTP_ADDRESS = "smtp.gmail.com"
MY_EMAIL = 'p.13.gulin@gmail.com'
MY_PASSWORD = 'nycr bvgj ikxd zekc'

app = Flask(__name__)
calculator = Calculator()


def calculate_price(address, postnr, diameter, num_stumps, difficulty):
    final_address = address + ', ' + postnr
    calculator.calc(int(diameter), int(num_stumps), difficulty)
    distanse ,_ ,_ = calculator.distance_calc(final_address) # _, _ = distanse_variabel og estimert tid (muligens brukbart senere) 
    jobb_kostnad = calculator.result_job
    kjore_kostnad = calculator.result_vei
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

    result, result_1, dist_cost, distance = calculate_price(address, postnr, diameter, num_stumps, difficulty)
    body = calculator.create_email_body(data, result, result_1, dist_cost, distance)
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


