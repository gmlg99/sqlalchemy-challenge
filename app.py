# Import the dependencies.

import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect the tables

Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    session.close()
    station_list = list(np.ravel(results))
    return jsonify(station_list)

# TOBS (Temperature Observations) route
@app.route("/api/v1.0/tobs")
def tobs():
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps)

# Start date route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    selection = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*selection).filter(Measurement.date >= start).all()
    else:
        results = session.query(*selection).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps)



