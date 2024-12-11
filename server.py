import mysql.connector
from flask import Flask, Response
from flask_cors import CORS
from geopy import distance
import json

app = Flask(__name__)
CORS(app)

connection = mysql.connector.connect(
    host = '127.0.0.1',
    port = 3306,
    database = 'final_game',
    user = 'root',
    password = '16102006',
    autocommit = True
)

airports = []

@app.route('/airports')
def get_airports():
    sql = """SELECT airport.name as 'name', airport.iso_country as 'iso_country', airport.municipality as 'municipality', country.name as
'country', airport.ident as 'ident', airport.latitude_deg as 'latitude_deg', airport.longitude_deg as 'longitude_deg'
    FROM airport, country
    WHERE airport.iso_country = country.iso_country
    AND airport.continent = 'EU'
    AND airport.type = 'large_airport'
    AND airport.iso_country NOT IN (SELECT airport.iso_country FROM airport WHERE iso_country = 'RU')
    ORDER BY RAND()
    LIMIT 40;"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

@app.route('/type')
def get_airport_type():
    sql = """SELECT * FROM airport_type;"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

@app.route('/distance/start=<start>&end=<end>')
def get_distance(start, end):
    sql = """SELECT latitude_deg, longitude_deg FROM airport WHERE ident = %s;"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (start,))
    result_start = cursor.fetchone()
    start_x = result_start['latitude_deg']
    start_y = result_start['longitude_deg']

    cursor.execute(sql, (end,))
    result_end = cursor.fetchone()
    end_x = result_end['latitude_deg']
    end_y = result_end['longitude_deg']

    dist = distance.distance((start_x, start_y), (end_x, end_y)).km
    rounded_dist = round(dist, 1)
    response = {"distance": rounded_dist}
    return response

@app.route('/specific/icao=<code>')
def get_details_of_specific_airport(code):
    sql = """SELECT airport.name as 'name', airport.iso_country as 'iso_country', airport.municipality as 'municipality', country.name as
'country', airport.ident as 'ident', airport.latitude_deg as 'latitude_deg', airport.longitude_deg as 'longitude_deg'
    FROM airport, country
    WHERE airport.iso_country = country.iso_country
    AND airport.ident = %s;"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (code,))
    result = cursor.fetchone()
    return result

@app.route('/coordinates/icao=<code>')
def get_coordinates_of_airport(code):
    sql = """SELECT latitude_deg, longitude_deg FROM airport WHERE ident = %s;"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (code,))
    result = cursor.fetchone()
    return result

@app.errorhandler(404)
def page_not_found(e):
    response = {"message": "Invalid endpoint.",
                "status": 404}
    json_response = json.dumps(response)
    http_response = Response(response = json_response, status = 404, mimetype = 'application/json')
    return http_response

if __name__ == '__main__':
    app.run(use_reloader = True, host = '127.0.0.1', port = 5000)