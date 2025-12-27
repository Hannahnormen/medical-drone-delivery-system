from flask import Flask, request
from flask_cors import CORS
import redis

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

redis_server = redis.Redis(host="localhost", decode_responses=True, charset="unicode_escape", port=6379)

redis_server.set('longitude', 13.21008)
redis_server.set('latitude', 55.71106)

@app.route('/drone', methods=['POST'])
def drone():
    drone = request.get_json()
    #Ensure the 'port' key exists in the request data
    droneIP = request.remote_addr
    droneID = drone['id']
    drone_longitude = drone['longitude']
    drone_latitude = drone['latitude']
    drone_status = drone['status']
    # Hämta befintlig port från Redis om den finns
    existing_port = redis_server.hget(f"drone:{droneID}", 'port')

    # Om port finns i begäran, använd den, annars behåll den befintliga porten i Redis
    drone_port = drone.get('port', existing_port)

    print(f"Port received: {drone_port}")  # Debugging the port field


    drone_data = {
        'id': droneID,
        'ip': droneIP,
        'longitude': drone_longitude,
        'latitude': drone_latitude,
        'status': drone_status,
        'port': drone_port  
    }


    redis_server.hset(f"drone:{droneID}", mapping=drone_data)
    redis_server.sadd("drones", f"drone:{droneID}")
   
    return {'message': 'Drone data updated successfully'}, 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5001')
