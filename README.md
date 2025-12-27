# InfoCom Drone Project - Part 5 - Multi-drone System
Install the required Python packages if not done already (you probably did this in the previous assignments):
```
sudo apt update
sudo apt install python3-socketio
sudo apt install python3-engineio
sudo apt install python3-flask-socketio
sudo apt install python3-flask-cors
sudo apt install python3-geopy
```


## On the Server Pi:
Go to `/webserver`, start your Redis server (if it is not already running, which it probably is – test using `redis-cli`) and run the three flask servers that make up the server side of the drone application:

1. Run the server for writing data to the redis server
    ```
    export FLASK_APP=database.py
    export FLASK_DEBUG=1
    python3 -m flask run --port=5001 --host=0.0.0.0
    ```

2. Start up the drones

Open up 4 terminals and go to `/pi`, run the following commands for each terminal window
```
    python3 drone.py --id DRONE1 --port 5004 for the first drone 
    python3 drone.py --id DRONE2 --port 5005 for the second drone
    python3 drone.py --id DRONE3 --port 5006 for the third drone 
    python3 drone.py --id DRONE4 --port 5007 for the fourth drone 
```
3. Open a new terminal, go to `/webserver`, and run the route planner
    ```
    export FLASK_APP=route_planner.py
    export FLASK_DEBUG=1
    python3 -m flask run --port=5002 --host=0.0.0.0
    ```

4. Open a new terminal, go to `/webserver`,  and run the website server
    ```
    export FLASK_APP=build.py
    export FLASK_DEBUG=1
    python3 -m flask run --port=5000 --host=0.0.0.0    
    ```

5.  Open a web browser (e.g. Chromium) on your Raspberry Pi and enter the following URL. You should see a map of Lund as in the previous assignment. Make sure you see two red dots on top of each other representing the drone at the LTH location.

    ```
    http://localhost:5000
    ```

Note: Don't use `python3 build.py`, `python3 route_planner.py`, `python3 database.py` or `python3 drone.py` to run the webservers, since this does not provide all the functionality required by the application.

