import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# import Flask
from flask import Flask, jsonify

################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Create an app, being sure to pass __name__
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################


# Define what to do when a user hits the index route
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature Observations: /api/v1.0/temp<br/>"
        f"Min, Max. and Avg. temperatures for a given start date (please use 'yyyy-mm-dd' format): /api/v1.0/&lt;start_date&gt;<br/>"
        f"Min, Max. and Avg. temperatures for a given start and end date (please use 'yyyy-mm-dd' format): /api/v1.0/&lt;start_date&gt;/&lt;end_date&gt;"
    )


# Create Precipitation Route
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create the session link
    session = Session(engine)

    """Return the JSON representation of your dictionary."""
    
    # Query precipitation and date values 
    results = session.query(Measurement.date, Measurement.prcp).all()
        
    session.close()
    
    # Create a dictionary as date the key and prcp as the value
    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

# Create Stations Route
#################################################

@app.route("/api/v1.0/stations")
def stations():
    # Create the session link
    session = Session(engine)
    
    """Return a JSON list of stations from the dataset."""
    # Query data to get stations list
    results = session.query(Station.station, Station.name).all()
    session.close()

    # Convert list of tuples into list of dictionaries for each station and name
    stations = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        stations.append(station_dict)
    
    # jsonify the list
    return jsonify(stations)

# Create Temperatures Route
#################################################

@app.route("/api/v1.0/temp")
def temp():
    # create session link
    session = Session(engine)
    
    """Return a JSON list of temperature observations (TOBS) for the previous year from the most active station."""
    
    # query tempratures from a year from the last data point.
    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = (dt.datetime.strptime(latest[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    print("****" + year_ago)
    
    # most active station
    most_active = session.query(Measurement.station,\
                  func.count(Measurement.station)).\
                  group_by(Measurement.station).\
                  order_by(func.count(Measurement.station).desc()).first()
#     print("**** " + str(type(most_active))) debugging

    results = session.query(Measurement.date,\
                            Measurement.tobs).\
                            filter(Measurement.date >= year_ago).\
                            filter(Measurement.station == most_active[0]).all()
    session.close()

    # convert list of tuples to show date and tempratures
    tobs_list = []
    for date, tobs in results:
        tob_dict = {}
        tob_dict["date"] = date
        tob_dict["tobs"] = tobs
        tobs_list.append(tob_dict)

    # jsonify the list
    return jsonify(tobs_list)

# Create Start Route
#################################################

@app.route("/api/v1.0/<start_date>")
def start(start_date):

    # create session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
        
    """
    # query data for the start date value
    results = session.query(func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date == start_date).all()
    session.close()
    
    # convert list of tuples to show date and min, avg, max tempratures
    temps_start = []
    for min, avg, max in results:
        temp_dict = {}
        temp_dict["min"] = min
        temp_dict["avg"] = avg
        temp_dict["max"] = max
        temps_start.append(temp_dict)

    # jsonify the list
    return jsonify(temps_start)

# Create Start/End Route
#################################################
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    # create session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
        
    """
    # query data for the start date value
    results = session.query(func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).\
                            filter(Measurement.date <= end_date).all()
    session.close()
    
    # convert list of tuples to show date and min, avg, max tempratures
    temps_start_end = []
    for min, avg, max in results:
        temp_dict = {}
        temp_dict["min"] = min
        temp_dict["avg"] = avg
        temp_dict["max"] = max
        temps_start_end.append(temp_dict)

    # jsonify the list
    return jsonify(temps_start_end)

if __name__ == '__main__':
    app.run(debug=True)
