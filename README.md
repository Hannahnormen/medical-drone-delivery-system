# Medical Drone Delivery System
Course Project - Digitalization, System Design and User-Centered Development

# Overview
This project is a prototype of a medical drone delivery system. It is based on a course-provided codebase and the core structure included a basic drone simulation, map based interface and backend communication. On top of the initial structure, the project was collaboratively extended to explore system design and digital services.

---

# Implemented Features
- **Support for multiple drones:**
  Support for running and managing multiple drones simultaneously, with unique IDs and       dedicated ports.

- **Web UI:**
  An interactive user interface displaying the drones on a map, where users can see drone    positions and order status.

- **Route planning service:**
  A route planner that calculates and assigns delivery routes based on drones states,        positions and destinations.
  
- **Redis-based data handling:**
  Usage of redis to store drone states and delivery data, enabling real-time updates.
  
- **Weather sensitive delivery logic:**
  Deliverys are paused during unsafe weather conditions.

  ---

# Technology and Tools
- **Backend: ** Python, Flask, Redis
- **Frontend:** HTML, CSS, Java
- **Other tools:** Raspberry Pi, REST APIs, QR-code generation

---

# Team Collaboration
This project was developed in a team as a part of a course assignment. The initial structure was provided by the course and was expanded through teamwork.
Team members: Hannah Normén, Signe Davidsson, Elliot Sjövall and Mohamad Alexander Hiadan

___

# How to run the simulation
You can run the project in a simulated enviroment, using several Raspberry pies

# Requirments
Install the required Python packages:
```
sudo apt update
sudo apt install python3-socketio
sudo apt install python3-engineio
sudo apt install python3-flask-socketio
sudo apt install python3-flask-cors
sudo apt install python3-geopy
```


## On the Server Pi:
Go to `/webserver`, start your Redis server and run the three flask servers that make up the server side of the drone application:

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

5.  Open a web browser on your Raspberry Pi and enter the following URL.

    ```
    http://localhost:5000
    ```

Note: Don't use `python3 build.py`, `python3 route_planner.py`, `python3 database.py` or `python3 drone.py` to run the webservers, since this does not provide all the functionality required by the application.

