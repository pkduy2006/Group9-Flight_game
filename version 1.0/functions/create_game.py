import get_forty_airports_in_europe
from prettytable import PrettyTable
import mysql.connector

connection = mysql.connector.connect(
    host = '127.0.0.1',
    port = 3306,
    database = 'version1',
    user = 'root',
    password = '16102006',
    autocommit = True
)

def get_fuel_table():
    sql = """SELECT * FROM fuel;"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def get_enemy_table():
    sql = """SELECT * FROM enemy;"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def insert_details_to_random_airports_table(icao, fu, en, si):
    sql = """INSERT INTO random_airports (ident, amount_of_fuel, number_of_enemy, situation) VALUES (%s, %s, %s, %s);"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (icao, fu, en, si))

def create_game(c_airports, p_base, p_target):
    #add your base and the target to the random_airports table
    insert_details_to_random_airports_table(p_base, 0, 0, 'intact')
    insert_details_to_random_airports_table(p_target, 0, 0, 'intact')

    #insert airports with fuel to the random airports table
    fuel_data = get_fuel_table()
    fuel_type_list = []
    for i in fuel_data:
        for j in range(0, i['probability']):
            fuel_type_list.append(i['amount'])
    for i, j in enumerate(fuel_type_list):
        insert_details_to_random_airports_table(c_airports[i + 2]['ident'], j, 0, 'intact')

    #insert airports with enemy to the random airports table
    enemy_data = get_enemy_table()
    enemy_type_list = []
    for i in enemy_data:
        for j in range(0, i['probability']):
            enemy_type_list.append(i['number'])
    for i, j in enumerate(enemy_type_list):
        insert_details_to_random_airports_table(c_airports[i + 17]['ident'], 0, j, 'intact')

    #insert airports with nothing to the random airports table
    for i in range(32, 40, 1):
        insert_details_to_random_airports_table(c_airports[i]['ident'], 0, 0, 'intact')

def delete_data_in_random_airports_table():
    sql = """DELETE FROM random_airports;"""
    cursor = connection.cursor()
    cursor.execute(sql)

def get_data_from_random_airports_table():
    sql = """SELECT * FROM random_airports;"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


airports = get_forty_airports_in_europe.get_forty_airports_in_europe()
p_base = airports[0]['ident']
p_target = airports[1]['ident']
create_game(airports, p_base, p_target)

random_airports_data = get_data_from_random_airports_table()
random_airports_table = PrettyTable(["id", "ident", "amount_of_fuel", "number_of_enemy", "situation"])
for i, j in enumerate(random_airports_data):
    random_airports_table.add_row([i + 1, j['ident'], j['amount_of_fuel'], j['number_of_enemy'], j['situation']])
print(random_airports_table)
#delete_data_in_random_airports_table()

