from cmath import pi
from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
from flask_cors import CORS
import redis
import json
import requests
import time
import threading
import atexit  # Lägg till atexit för att stänga ner Redis vid servernedstängning

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

redis_server = redis.Redis(host='localhost', port=6379, decode_responses=True)

geolocator = Nominatim(user_agent="my_request")
region = ", Lund, Skåne, Sweden"

# Funktion för att rensa Redis vid servernedstängning
def cleanup_redis():
    print("Cleaning up order-related Redis keys...")
    # Radera kön
    redis_server.delete('drone:queue')

    # Hämta alla nycklar
    all_keys = redis_server.keys('*')
    for key in all_keys:
        # Om nyckeln är ett heltal → vi antar det är ett ordernummer
        if key.isdigit():
            redis_server.delete(key)

# Registrera funktionen för att rensa Redis när servern stängs
atexit.register(cleanup_redis)

@app.route('/planner', methods=['POST'])
def route_planner():
    data = json.loads(request.data.decode())
    FromAddress = "Sölvegatan 14"
    ToAddress = data['taddr']
    order_number = data.get('order_number')
    
    from_location = geolocator.geocode(FromAddress + region, timeout=None)
    to_location = geolocator.geocode(ToAddress + region, timeout=None)
    print(f"from location: {from_location}")
    print(f"to location: {to_location}")

    if from_location is None:
        return 'Departure address not found, please input a correct address'
    elif to_location is None:
        return 'Destination address not found, please input a correct address'
    else:
        coords = {
            'pickup': (from_location.longitude, from_location.latitude),
            'destination': (to_location.longitude, to_location.latitude),
            'order_number': order_number
        }
        print(f"FromAdress: {coords}")
       
         # Hämta alla drönare från Redis
        drones = redis_server.smembers("drones")
        droneAvailable = None

        for drone in drones:
            droneData = redis_server.hgetall(drone)

            # Kolla om drönaren är ledig
            if droneData.get('status') == 'idle':
                droneAvailable = drone
                coords['current'] = (
                    float(droneData['longitude']),
                    float(droneData['latitude'])
                )
                # Uppdatera drönarens status till 'busy' för att indikera att den är upptagen
                redis_server.hset(drone, 'status', 'busy')
                break

        if droneAvailable is None:
             # Lägg till order i kön om ingen drönare är tillgänglig
            order_data = {
                'status': 'i kö',  # Sätt status till 'queued'
                'drone': '',  # Ingen drone tilldelad än
                'order_number': order_number
            }

            redis_server.hset(order_number, mapping=order_data)  # Lägg till ordern i Redis
            redis_server.rpush('drone:queue', json.dumps(coords))
            return jsonify({'status': 'i kö', 'message': 'No available drone, your order has been queued'})
        else:
            # Det finns en tillgänglig drönare
            redis_server.hset(order_number, mapping={
            'status': 'levereras',
            'drone': droneAvailable
            })

            DRONE_IP = redis_server.hget(droneAvailable, 'ip')
            DRONE_PORT = redis_server.hget(droneAvailable, 'port')  # Fetch the 'port' key
            DRONE_URL = f'http://{DRONE_IP}:{DRONE_PORT}'


            try:
                with requests.session() as session:
                    resp = session.post(DRONE_URL, json=coords)
                    print(resp.text)
                return jsonify({'status': 'levereras', 'message': 'Got address and sent request to the drone'})
            except Exception as e:
                print(e)
                return jsonify({'status': 'error', 'message': "Could not connect to the drone, please try again"})
            
@app.route('/queue-length', methods=['GET'])
def queue_length():
    # Kolla om det finns ordrar i kön
    length = redis_server.llen('drone:queue')
    return jsonify({'queue_length': length})

@app.route('/delivery_complete', methods=['POST'])
def delivery_complete():
    data = request.get_json()
    order_number = data.get('order_number')

    if order_number:
        # Uppdatera Redis
        redis_server.hset(order_number, 'status', 'levererad')
        print(f"✔️ Order {order_number} levererad.")

        return jsonify({'message': 'Orderstatus uppdaterad till levererad'}), 200
    return jsonify({'error': 'Ordernummer saknas'}), 400

def drone_queue_worker():
    while True:
        # Kolla om det finns ordrar i kön
        order_data = redis_server.lindex('drone:queue', 0)
        if order_data:
            drones = redis_server.smembers("drones")
            for drone in drones:
                droneData = redis_server.hgetall(drone)
                if droneData.get('status') == 'idle':
                    # Om drönaren är ledig, hämta ordern från kön
                    coords = json.loads(order_data)
                    coords['current'] = (
                        float(droneData['longitude']),
                        float(droneData['latitude'])
                    )
                    redis_server.hset(drone, 'status', 'busy')

                    drone_ip = droneData['ip']
                    drone_port = droneData['port']
                    drone_url = f"http://{drone_ip}:{drone_port}"

                    try:
                        with requests.session() as session:
                            resp = session.post(drone_url, json=coords)
                            print(f"Sent queued job to {drone}: {resp.text}")
                        
                       
                        redis_server.lpop('drone:queue')  # Ta bort order från kön
                        redis_server.hset(coords['order_number'], 'status', 'levereras')  # Uppdatera status i Redis

                    except Exception as e:
                        print(f"Failed to send queued job to {drone}: {e}")
                        redis_server.hset(coords['order_number'], 'status', 'error')  # Om det misslyckas, sätt status till 'error'
                    break
        time.sleep(5)

threading.Thread(target=drone_queue_worker, daemon=True).start()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5002')
