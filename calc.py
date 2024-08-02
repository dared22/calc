import pickle
import googlemaps
from datetime import datetime

API_KEY = 'AIzaSyD52GY-dsG6mjbXSukZIsmuOxE2w3X80iQ'
ORIGIN = 'Tåsenveien 127, 0880'
gmaps = googlemaps.Client(key=API_KEY)


class Calculator:
    """
    En klasse for å beregne kostnader knyttet til stubbefresing og transport.

    Attributter:
    vanskelighet_dict (dict): En ordbok som lagrer vanskelighetsgrader og tilhørende kostnadsfaktorer.
    result_job (float): Resultatet av jobbkostnadsberegningen.
    result_vei (float): Resultatet av transportkostnadsberegningen.
    prisliste_dict (dict): En ordbok som lagrer prislister, lastet fra en pickle-fil.
    """
    def __init__(self):
        """
        Initialiserer Calculator-klassen og laster prisliste-data fra en pickle-fil.
        """
        self.vanskelighet_dict = {"Enkel": 0, "Vanskelig": 0.7, "Trapp": 0.7, "Bratt": 0.7}
        self.result_job = 0
        self.result_vei = 0
        self.postnr = [1433, 1444, 1445, 1446, 1447]
        with open('prisliste_data.pkl', 'rb') as f:
            self.prisliste_dict = pickle.load(f)


    def calc(self, diameter, num, vanske):
        """
        Beregner kostnaden for stubbefresing basert på diameter, antall stubber og vanskelighetsgrad.

        Parametere:
        diameter (str): Diameteren på stubben i cm.
        num (int): Antall stubber som skal fjernes.
        vanske (str): Vanskelighetsgraden på tilkomsten (Enkel, Vanskelig, Trapp, Bratt).

        Returnerer:
        Oppdaterer `result_job` attributten med beregnet kostnad.
        """
        diameterpris = self.prisliste_dict[diameter]
        if num == 1:
            x = diameterpris
        else:
            x = diameterpris + (num - 1) * diameterpris * 0.5
        y = diameterpris * self.vanskelighet_dict[vanske]
        self.result_job = x + y


    def distance_calc(self, destination, origin=ORIGIN):
        """
        Beregner avstanden og transportkostnaden fra en opprinnelsesadresse til en destinasjon.

        Parametere:
        destination (str): Destinasjonsadressen.
        origin (str, valgfritt): Opprinnelsesadressen. Standardverdi er ORIGIN (Tåsenveien 127).

        Returnerer:
        tuple: En tuple bestående av avstandstekst (str), avstandsverdi i meter (int), og varighetstekst (str).
        """
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
    

    @staticmethod
    def create_email_body(data, result, result_1, dist_cost, distance):
        """
        Lager innholdet til en e-post basert på beregningsdata og brukerinput.

        Parametere:
        data (dict): En ordbok som inneholder brukerens detaljer.
        result (float): Den totale estimerte kostnaden.
        result_1 (float): Kostnaden for stubbefresing.
        dist_cost (float): Transportkostnaden.
        distance (str): Den beregnede avstanden.

        Returnerer:
        str: En formattert e-posttekst som inkluderer all relevant informasjon.
        """
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


    




        
