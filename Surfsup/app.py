# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")



# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<center><strong>Welcome! Here are all the available routes</strong></center><br/>"
        f"<strong>Available Routes:</strong><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    latest_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    one_year_ago = latest_date - dt.timedelta(days=365)
    precipitation= session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago)
    session.close()
    precipitation_dict = {}
    for date, prcp in precipitation:
        precipitation_dict[date] = prcp
    return jsonify(precipitation_dict)
    
    
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()
    all_names = list(np.ravel(results))
    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    latest_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    one_year_ago = latest_date - dt.timedelta(days=365)
    station_counts = session.query(measurement.station, func.count(measurement.date) ).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active_station = station_counts[0][0]
    temperature = session.query(measurement.tobs).filter(measurement.date >= one_year_ago).filter(measurement.station == most_active_station).all()
    temp_list = list(np.ravel(temperature))
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    session = Session(engine)
    functions = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    if not end:
        results = session.query(*functions).filter(measurement.date >=start).all()
        session.close()
        return jsonify(list(np.ravel(results)))
    else:
        results = session.query(*functions).filter(measurement.date >=start).filter(measurement.date <= end).all()
        session.close()
        return jsonify(list(np.ravel(results)))

if __name__ == '__main__':
    app.run(debug=True)
