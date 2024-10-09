import mysql.connector
from prettytable import PrettyTable

connection = mysql.connector.connect(
    host = '127.0.0.1',
    port = 3306,
    database = 'version1',
    user = 'root',
    password = '16102006',
    autocommit = True
)

def get_forty_airports_in_europe():
    sql = """SELECT airport.name as 'name', airport.iso_country as 'iso_country', airport.municipality as 'municipality', country.name as 'country', airport.ident as 'ident', airport.latitude_deg as 'latitude_deg', airport.longitude_deg as 'longitude_deg' 
    FROM airport, country
    WHERE airport.iso_country = country.iso_country
    AND airport.continent = 'EU'
    AND airport.type = 'large_airport'
    AND airport.iso_country NOT IN (SELECT airport.iso_country FROM airport WHERE (iso_country = 'RU' OR iso_country = 'IS'))
    ORDER BY RAND()
    LIMIT 40"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

'''
airports = get_forty_airports_in_europe()
airports_table = PrettyTable(["Name", "ISO - Country code", "Municipality", "Country", "ICAO code", "Latitude Degree", "Longitude Degree"])
for i in airports:
    airports_table.add_row([i['name'], i['iso_country'], i['municipality'], i['country'], i['ident'], i['latitude_deg'], i['longitude_deg']])
print(airports_table)
'''
