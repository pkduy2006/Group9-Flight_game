import mysql.connector
from prettytable import PrettyTable

connection = mysql.connector.connect(
    host = '127.0.0.1',
    port = 3306,
    database = 'version1',
    user = 'root',
    password = '16102006',
)

def get_monument():
    sql = """SELECT * FROM monument;"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def get_name_and_city_country_of_airport(icao):
    sql = """SELECT airport.name as 'name', airport.municipality as 'city', country.name as 'country'
    FROM airport, country
    WHERE airport.ident = %s
    AND airport.iso_country = country.iso_country;"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (icao, ))
    result = cursor.fetchone()
    return result

monument_data = get_monument()
monument_table = PrettyTable(['id', 'name', 'place of loss', 'total enemy killed'])
for i in monument_data:
    airport_of_loss = get_name_and_city_country_of_airport(i['location'])
    monument_table.add_row([i['id'], i['name'], airport_of_loss['name'] + ', ' + airport_of_loss['city'] + ', ' + airport_of_loss['country'], i['total_enemy_killed']])
print(monument_table)
