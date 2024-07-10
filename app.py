from flask import Flask, request, render_template, jsonify
import pickle

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

@app.route('/', methods=['GET'])
def index():
    diameters = list(prisliste_dict.keys())
    diffclts = list(vanskelighet_dict.keys())
    return render_template('index.html', diameters=diameters, diffclts=diffclts)

@app.route('/calculate', methods=['POST'])
def calculate_price_ajax():
    d = int(request.form['diameter'])
    n = int(request.form['num_stumps'])
    v = request.form['difficulty']
    result = calc(d, n, v)
    return jsonify(price=result)

if __name__ == '__main__':
    app.run(debug=True)
