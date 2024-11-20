# Import the dependencies.
import numpy as np
import sqalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create our session (link) from Python to the DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Create engine
base = automap_base()
base.prepare(autoload_with = engine)


# reflect an existing database into a new model
# reflect the tables


# Save references to each table
measurement = base.classes.measurement
Station = base.classes.station


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations List: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
    )

@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()

    temp_obs_all = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Minimum"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Maximum"] = max
        temp_obs_all.append(tobs_dict)

    return jsonify(temp_obs_all)

@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= stop).all()
    session.close()

    temp_obs_all = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        temp_obs_all.append(tobs_dict)

    return jsonify(temp_obs_all)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    lateststr = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [measurement.date,measurement.tobs]
    queryresult = session.query(*sel).filter(measurement.date >= querydate).all()
    session.close()

    temp_obs_all = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        temp_obs_all.append(tobs_dict)

    return jsonify(temp_obs_all)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [measurement.date,measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

if __name__ == '__main__':
    app.run(debug=True)