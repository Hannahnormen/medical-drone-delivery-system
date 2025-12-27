from os import fdopen
import os
from flask import Flask, render_template, request
from flask.json import jsonify
from flask_cors import CORS
import time
import redis
import json
from lager import Produkt
from lager import Order
from lager import Test
from flask import redirect, url_for
import requests

#Lagt  till dessa importer för att kunna ladda in listan med produkterna
import base64
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

from weather import get_current_weather

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'


redis_server = redis.Redis(host="localhost", decode_responses=True, charset="unicode_escape", port=6379)

def translate(coords_osm):
    x_osm_lim = (13.143390664, 13.257501336)
    y_osm_lim = (55.678138854000004, 55.734680845999996)

    x_svg_lim = (212.155699, 968.644301)
    y_svg_lim = (103.68, 768.96)

    x_osm = coords_osm[0]
    y_osm = coords_osm[1]

    x_ratio = (x_svg_lim[1] - x_svg_lim[0]) / (x_osm_lim[1] - x_osm_lim[0])
    y_ratio = (y_svg_lim[1] - y_svg_lim[0]) / (y_osm_lim[1] - y_osm_lim[0])
    x_svg = x_ratio * (x_osm - x_osm_lim[0]) + x_svg_lim[0]
    y_svg = y_ratio * (y_osm_lim[1] - y_osm) + y_svg_lim[0]

    return x_svg, y_svg

lista1 = [
    Produkt("Sårsalvor och antiseptiska medel", 50), 
    Produkt("Nässprej", 20), 
    Produkt("C-vitamin", 500),
]
lista2 = [
    Produkt("Paracetamol", 10),
    Produkt("Ibuprofen", 16),
    Produkt("Acetylsalicylsyra", 10),
]
lista3 = [
    Produkt("Acetylsalicylsyra", 10),
    Produkt("Antihistaminer", 2),
    Produkt("Laktosintoleransmedel", 4),
    Produkt("Antacida", 48),
]
lista4 = [
    Produkt("Aloe Vera-gel", 100),
]
order1 = Order(lista1, "Magistratsvägen 1", "1")
order2 = Order(lista2, "Nationsgatan 1", "2")
order3 = Order(lista3, "Tunavägen 5", "3")
order4 = Order(lista4, "Södra Esplanaden 10", "4")
order5 = Order(lista1, "Södra Esplanaden 1", "5")

order1.set_qr_code("qr_order_1.png")
order2.set_qr_code("qr_order_2.png")
order3.set_qr_code("qr_order_3.png")
order4.set_qr_code("qr_order_4.png")
order5.set_qr_code("qr_order_5.png")

olist = [
   order1,
    order2,
    order3,
    order4,
    order5
    
]

test_obj = Test(olist)

def check_available_drones():
    drone_keys = redis_server.keys("drone:*")
    
    for key in drone_keys:
        # Ignorera drone:queue
        if key == "drone:queue":
            continue

        # Kontrollera typ
        key_type = redis_server.type(key)
        if key_type != 'hash':
            continue

        drone_data = redis_server.hgetall(key)
        if drone_data:
            status = drone_data.get('status', 'unknown')
            if status == "idle":
                return True
    return False

def checkweather():
    weather_api_key = os.getenv('WEATHER_API_KEY')
    current_weather = get_current_weather("Lund", weather_api_key)
      
    is_raining = current_weather["is_raining"]
    wind_kph = current_weather["wind_kph"]
    temp_c = current_weather["temp_c"]

    print(f"raining: {is_raining},  wind: {wind_kph},  temp: {temp_c}")

    if is_raining or wind_kph > 10:
        return True
    return False

condition = True

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/map', methods=['GET'])
def map():
    return render_template('index.html')

@app.route('/qr')
def qr_scanner():
    return render_template('qrcode.html')  # HTML-filen som innehåller QR-kodskannaren

@app.route('/verify_order', methods=['POST'])
def verify_order():
    order_number = request.form.get('order-number')
    order = test_obj.getOrder(order_number)

    if order:
        from_addr = "Sölvegatan 14" 
        #använder nu funktionen .getAdress() istället för enbart .adress
        to_addr = order.getAdress()
        #Lagt till så korrekt vikt hämtas
        total_weight = order.getTotWeight()

        #hämtar produkterna från list
        products = [p.namn for p in order.lists]
        product_json = base64.urlsafe_b64encode(json.dumps(products).encode()).decode()
        
        print("Kör checkweather...")
        weather_conditions = checkweather()

        # Om väderförhållanden är dåliga
        if weather_conditions:
            order_status = "väderproblem"
            redis_server.hset(order_number, 'status', 'väderproblem')
            return redirect(url_for('map',
                                    ordernumber=order_number,
                                    address=to_addr,
                                    weight=total_weight,
                                    products=product_json,
                                    status="väderproblem"))
        
       

       # Kolla om det finns lediga drönare
        available_drones = check_available_drones()

        if available_drones:
            order_status = "levereras"  # Sätt orderstatusen till "levereras" om en ledig drönare finns
        else:
            order_status = "i kö"  # Sätt orderstatusen till "i kö" om inga lediga drönare finns


       
        planner_url = "http://localhost:5002/planner"
        payload = {
            "faddr": from_addr,
            "taddr": to_addr,
            "order_number": order_number
            
        }

        #Detta skickar en korrekt url som är nåbar i index.html.
        try:
            resp = requests.post(planner_url, json=payload)
            print("Planner response:", resp.text)
        except Exception as e:
            print("Planner error:", e)
        
        #Skickar url med alla komponenter som behövs för info-panel
        return redirect(url_for('map', 
                            ordernumber=order_number,
                            address=to_addr,
                            weight=total_weight,
                            products=product_json, 
                            status=order_status))  # Lägg till status i URL:en
    else:
        return jsonify({'error': 'Ordernummer finns inte.'}), 40


@app.route('/get_drones', methods=['GET'])
def get_drones():
    drone_dict = {}
    drone_keys = redis_server.keys("drone:*")
    print(f"Found drone keys: {drone_keys}")  # Lägg till loggning för att se vilka nycklar som finns

    for key in drone_keys:
        # Kontrollera typ
        key_type = redis_server.type(key)
        if key_type != 'hash':
            continue
        drone_id = key.split(":")[1]
        drone_data = redis_server.hgetall(key)

        if drone_data:
            try:
                longitude = float(drone_data.get('longitude', 0))
                latitude = float(drone_data.get('latitude', 0))
                status = str(drone_data.get('status'))

                x_svg, y_svg = translate((longitude, latitude))
                drone_dict[drone_id] = {
                    'longitude': x_svg,
                    'latitude': y_svg,
                    'status': status
                }
            except Exception as e:
                print(f"Error with {key}: {e}")

    return jsonify(drone_dict)


@app.route('/order_status/<order_number>', methods=['GET'])
def get_order_status(order_number):
    """Returnerar aktuell status för en order."""
    status = redis_server.hget(order_number, 'status') or 'okänd'
    return jsonify({'status': status})

@app.route('/set_order_delivered', methods=['POST'])
def set_order_delivered():
    data = request.get_json()
    order_number = data.get('order_number')

    if order_number:
        redis_server.hset(order_number, 'status', 'levererad')
        return jsonify({'status': 'ok'}), 200
    return jsonify({'error': 'Ordernummer saknas'}), 400

@app.route('/verify_qr', methods=['POST'])
def verify_qr():
    try:
        data = request.get_json()
        qr_code_data = data.get('decoded_text')
        order_id = data.get('order_id')

        if not qr_code_data or not order_id:
            return jsonify({'success': False, 'message': 'QR-kod eller order-ID saknas'}), 400

        # Verifiera QR-koddata här 
        order = test_obj.getOrder(order_id)

        if order is None:
            return jsonify({'success': False, 'message': 'Order finns inte'}), 404

       # Jämför QR-kodens data med orderns id
        if qr_code_data == order.getOrderNmbr():
            redis_server.hset(order_id, 'status', 'levererad')  # markera levererad
            return jsonify({'success': True}), 200
        else:
            try:
                with open('problem_reports.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  - Ordernummer: {order_id} - Fel QR-kod\n")
            except Exception as e:
                print(f"Kunde inte logga problemet: {e}")
            return jsonify({'success': False}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report-problem', methods=['POST'])
def report_problem():
    data = request.get_json()
    message = data.get('message')
    order_number = data.get('order_number')

    if not message:
        return jsonify({'error': 'Inget meddelande mottaget'}), 400

    try:
        with open('problem_reports.txt', 'a', encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  - Ordernummer: {order_number} - {message}\n")
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')
