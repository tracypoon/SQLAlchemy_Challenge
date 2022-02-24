import numpy as np
import datetime as dt
from soupsieve import select

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session=Session(engine)

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
   """Return the precipitation data for the last year"""
   # Calculate the date 1 year ago from last date in database
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

   # Query for the date and precipitation for the last year
   precipitation = session.query(Measurement.date, Measurement.prcp).\
       filter(Measurement.date >= prev_year).all()

   session.close()

   # Dict with date as the key and prcp as the value
   precip = {date: prcp for date, prcp in precipitation}

   return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():

    """Return a list stations"""
    # Get all stations
    results = session.query(Station.station).all()

    session.close()

    #Unravel results into an array and convert to a list
    stations=list(np.ravel(results))

    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def tobs():
   """Return the temperature data for the last year"""
   # Calculate the date 1 year ago from last date in database
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

   # Query the primary station for all tobs from last year
   temperature = session.query(Measurement.date, Measurement.tobs).\
       filter(Measurement.station == 'USC00519281').\
       filter(Measurement.date >=prev_year).all()

   session.close()

   # Dict with date as the key and tobs as the value
   tobs = {date: tobs for date, tobs in temperature}

   
   return jsonify(tobs=tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start=None, end=None):
    
    #Create a list to calculate min, avg, and max temperatures
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    #Create an if statement to get the start time 
    if not end:
        start=dt.datetime.strptime(start, "%m-%d-%Y")
        
        #Get the results by filtering through the dates
        results = session.query(*sel).\
            filter(Measurement.date>= start).all()
   

        session.close()

   #Unravel results into an array and convert to a list
        tobs=list(np.ravel(results))
   
        return jsonify(tobs)

    #Define where user can input start/end dates
    start=dt.datetime.strptime(start, "%m-%d-%Y")
    end=dt.datetime.strptime(end, "%m-%d-%Y")

    #Get the results by filtering through the dates
    results=session.query(*sel).\
        filter(Measurement.date>=start).\
        filter(Measurement.date<=end).all()

    session.close()

    #Unravel results into an array and convert to a list
    tobs=list(np.ravel(results))

    return jsonify(tobs=tobs)

if __name__ =='__main__':
    app.run()

