"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq

APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)

api = openaq.OpenAQ()

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return '< Time {}, Value {} >'.format(self.datetime, self.value)

@APP.route('/')
def root():
    """Base view."""
    return str(Record.query.filter(Record.value >= 10).all())

def los_angeles_pm25():
    """
    (List of tuples) Retrieves and returns last 100 observations of
    measurements of fine particulate matter in the Los Angeles area from 
    OpenAQ API.
    """
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    utc_values = []
    # Returns 'utc' from 'date' section and 'value' for each returned
    # observation and appends them as a tuple to a list
    for result in body['results']:
        tup = tuple([result['date']['utc'], result['value']])
        print(tup)
        utc_values.append(tup)
    print(utc_values)
    return utc_values

@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    utc_values = los_angeles_pm25()
    db_values = Record()
    # Add each time/value pair to the database
    for value in utc_values:
        db_value = Record(datetime=value[0], value=value[1])
        DB.session.add(db_value)
        print('VALUE ADDED - ', value)
    # Commit changes to database
    DB.session.commit()
    return 'Data refreshed!'