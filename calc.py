import pickle
import googlemaps
from datetime import datetime

API_KEY = 'AIzaSyD52GY-dsG6mjbXSukZIsmuOxE2w3X80iQ'
ORIGIN = 'Tåsenveien 127, 0880'
gmaps = googlemaps.Client(key=API_KEY)


class Calculator:
    def __init__(self):
        self.vanskelighet_dict = {"Enkel": 0, "Vanskelig": 0.7, "Trapp": 0.7, "Bratt": 0.7}
        self.result_job = 0
        self.result_vei = 0
        with open('prisliste_data.pkl', 'rb') as f:
            self.prisliste_dict = pickle.load(f)


    def calc(self, diameter, num, vanske):
        diameterpris = self.prisliste_dict[diameter]
        if num == 1:
            x = diameterpris
        else:
            x = diameterpris + (num - 1) * diameterpris * 0.5
        y = diameterpris * self.vanskelighet_dict[vanske]
        self.result_job = x + y


    def distance_calc(self, destination, origin=ORIGIN):
        directions_result = gmaps.directions(origin,
                                         destination,
                                         mode="driving",
                                         departure_time=datetime.now())
        #avstand variabler
        distance_text = directions_result[0]['legs'][0]['distance']['text']
        distance_val = directions_result[0]['legs'][0]['distance']['value']
        duration = directions_result[0]['legs'][0]['duration']['text'] #brukes ikke foreløpig (estimert tid)
        self.result_vei = (distance_val/1000) * 100 

        return distance_text, distance_val, duration
    
    def create_email_body(data, result, result_1, dist_cost, distance):
        return f"""
        Hei {data['fname']},

        Her er informasjonen om din forespørsel:
        Fornavn: {data['fname']}
        Etternavn: {data['lname']}
        Email: {data['email']}
        Telefon: {data['phone']}
        Gateadresse: {data['address']}
        Postnummer: {data['postnr']}
        Diameter: {data['diameter']} cm
        Antall stubber: {data['num_stumps']}
        Tilkomst: {data['difficulty']}
        Stubbefresing kost totalt: {result_1} Kr
        Transportkostnad: {dist_cost} Kr
        Kjørelengde: {distance}
        Estimert totalpris: {result} Kr

        Takk for at du bruker vår priskalkulator!

        Med vennlig hilsen,
        Norsk Trefelling
        """


    




        
