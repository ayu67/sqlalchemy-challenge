import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"/api/v1.0/&lt;insert_start_date_here&gt;<br/>"
        f"/api/v1.0/&lt;insert_start_date_here&gt;/&lt;insert_end_date_here&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using `date` as the key and `prcp` as the value"""

    # Query the dates and precipitation 
    results = session.query(measurement.date,measurement.prcp).order_by(measurement.date).all()

    # create list of dictionaries
    prcp_list = [] 
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        prcp_list.append(prcp_dict)

    session.close()

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(station.station, station.name).all()

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of temperature observations (TOBS) for the previous year 8/23/2016"""

    # Get last date and prev year
    date = session.query(measurement.date).order_by(desc(measurement.date)).first()[0]
    prev_year = (dt.datetime.strptime(date , '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query temperatures
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= prev_year).order_by(measurement.date).all()

    session.close()

    # create list of dictionaries
    tobs_list = []
    for date,tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<insert_start_date_here>")
# lets try to do start and end together
def temp_start(insert_start_date_here):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """calculate `TMIN`, `TAVG`, and `TMAX`"""

    # try to ensure the right format just in case
    start_dt = dt.datetime.strptime(insert_start_date_here,'%Y-%m-%d')

    # Get tobs
    results = session.query(measurement.date,func.min(measurement.tobs),\
        func.avg(measurement.tobs),func.max(measurement.tobs)).\
        filter(measurement.date >= start_dt).all()

    session.close()

    # create list of dictionaries
    tobs_list_start = []
    for date,tmin,tavg,tmax in results:
        tobs_dict_start = {}
        tobs_dict_start['Date'] = date
        tobs_dict_start['TMIN'] = tmin
        tobs_dict_start['TAVG'] = tavg
        tobs_dict_start['TMAX'] = tmax
        tobs_list_start.append(tobs_dict_start)

    return jsonify(tobs_list_start)

@app.route("/api/v1.0/<insert_start_date_here>/<insert_end_date_here>")
# lets try to do start and end together
def temp_start_end(insert_start_date_here,insert_end_date_here):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """calculate `TMIN`, `TAVG`, and `TMAX`"""

    # try to ensure the right format just in case
    start_dt = dt.datetime.strptime(insert_start_date_here,'%Y-%m-%d')
    end_dt = dt.datetime.strptime(insert_end_date_here,'%Y-%m-%d')

    # Get tobs
    results = session.query(func.min(measurement.tobs),\
        func.avg(measurement.tobs),func.max(measurement.tobs)).\
        filter(measurement.date >= start_dt).\
        filter(measurement.date <= end_dt).all()

    session.close()

    # create list of dictionaries
    tobs_list_start_end = []
    for tmin,tavg,tmax in results:
        tobs_dict_start_end = {}
        tobs_dict_start_end['Start Date'] = start_dt.strftime('%Y-%m-%d')
        tobs_dict_start_end['End Date'] = end_dt.strftime('%Y-%m-%d')
        tobs_dict_start_end['TMIN'] = tmin
        tobs_dict_start_end['TAVG'] = tavg
        tobs_dict_start_end['TMAX'] = tmax
        tobs_list_start_end.append(tobs_dict_start_end)

    return jsonify(tobs_list_start_end)


if __name__ == '__main__':
    app.run(debug=True)
