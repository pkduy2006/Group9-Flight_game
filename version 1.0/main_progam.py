import mysql.connector
import user_story
import time
from prettytable import PrettyTable
from geopy import distance
import random

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

def get_coord_of_airport(icao):
    sql = "SELECT latitude_deg, longitude_deg FROM airport WHERE ident = %s;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (icao, ))
    result = cursor.fetchone()
    return result

def cal_dis(airport1, airport2):
    st_coord = get_coord_of_airport(airport1)
    nd_coord = get_coord_of_airport(airport2)

    return distance.distance((st_coord['latitude_deg'], st_coord['longitude_deg']), (nd_coord['latitude_deg'], nd_coord['longitude_deg'])).km

def get_available_airports(icao, p_fuel):
    sql = ("""SELECT airport.ident, random_airports.ident, random_airports.situation, airport.iso_country, country.iso_country, country.name 
    FROM random_airports, airport, country
     WHERE random_airports.ident NOT IN (SELECT random_airports.ident FROM random_airports WHERE random_airports.ident = %s)
     AND airport.ident = random_airports.ident
     AND airport.iso_country = country.iso_country
     ORDER BY country.name;""")
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (icao, ))
    available_airports = []
    opened_airports = cursor.fetchall()
    for x in opened_airports:
        dis = cal_dis(icao, x['ident'])
        if x['situation'] == 'intact' and dis <= p_fuel * 2:
            available_airports.append(x['ident'])

    return available_airports

def delete_random_airports_table():
    sql = """DELETE FROM random_airports;"""
    cursor = connection.cursor()
    cursor.execute(sql)

def update_airport_situation(p_location, a_situation):
    sql = """UPDATE random_airports SET situation = %s WHERE ident = %s;"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (p_location, a_situation))

def get_airport_amount_of_fuel(icao):
    sql = "SELECT amount_of_fuel FROM random_airports WHERE ident = %s;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (icao, ))
    result = cursor.fetchone()
    return result['amount_of_fuel']

def get_airport_number_of_enemy(icao):
    sql = "SELECT number_of_enemy FROM random_airports WHERE ident = %s;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (icao, ))
    result = cursor.fetchone()
    return result['number_of_enemy']

def create_available_airport_table(re_a_data, p_location):
    recommended_airport_table = PrettyTable(['id', 'name', 'location', 'ident', 'Distance'])
    for i, j in enumerate(re_a_data):
        airport_info = get_name_and_city_country_of_airport(j)
        recommended_airport_table.add_row(
            [i + 1, airport_info['name'], str(airport_info['city'] + ', ' + airport_info['country']), j, round(cal_dis(p_location, j), 1)])
    return recommended_airport_table

def insert_details_of_loser(p_name, p_location, p_total_enemy_killed):
    sql = """INSERT INTO monument(name, location, total_enemy_killed) VALUES (%s, %s, %s);"""
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (p_name, p_location, p_total_enemy_killed))

#Greet player
print("Hello. Welcome to Group 9's flight game! Let's begin!")

#show the monument table and the hall of fame table so the player can see the danger of this mission
print("Before I introduce you about you mission, let's visit the Monument to War Heroes and Martyrs.")
time.sleep(1)
monument_data = get_monument()
monument_table = PrettyTable(['id', 'name', 'place of loss', 'total enemy killed'])
for i in monument_data:
    airport_of_loss = get_name_and_city_country_of_airport(i['location'])
    monument_table.add_row([i['id'], i['name'], airport_of_loss['name'] + ', ' + airport_of_loss['city'] + ', ' + airport_of_loss['country'], i['total_enemy_killed']])
print(monument_table)
print("As you can see, it's a quite dangerous mission and no one has completed its before.")
time.sleep(1)

#ask if player want to read the background story
print("Next, there are some important details that our spies have collected in the background story.")
time.sleep(1)
story_choice = input("Do you want to read it? (yes/no) ")
if story_choice == "yes":
    for each_line in user_story.get_story():
        print(each_line)
        time.sleep(1.5)
else:
    print("You will be regretted later.")

#player settings
player_name = input("What is your name? ")
player_fuel = 500
player_total_enemy_killed = 0
player_bonus_gained = 0
player_enemy_killed = 0
player_mission_completed = False
game_over = False
player_victory = False

#player base and target settings
chosen_airports = get_forty_airports_in_europe()
player_base = chosen_airports[0]['ident']
player_target = chosen_airports[1]['ident']
while cal_dis(player_base, player_target) <= player_fuel:
    random.shuffle(chosen_airports)
    player_base = chosen_airports[0]['ident']
    player_target = chosen_airports[1]['ident']
player_location = player_base

#create a new game
create_game(chosen_airports, player_base, player_target)

#start game
print("Your mission starts.")
time.sleep(1)

#inform player about his/her base
player_base_info = get_name_and_city_country_of_airport(player_base)
print(f"You are at {player_base_info['name']} in {player_base_info['city']}, {player_base_info['country']}.")
time.sleep(1)

#inform player about his/her target
player_target_info = get_name_and_city_country_of_airport(player_target)
print(f"Your target is {player_target_info['name']} in {player_target_info['city']}, {player_target_info['country']}.")
time.sleep(1)

#inform player about his/her fuel left
print(f"The military headquarter provided you with {player_fuel} liters of aviation gasoline. As a result, you can travel up to {player_fuel * 2} km.")
time.sleep(1)

#show the available airports list
recommended_airport_data = get_available_airports(player_location, player_fuel)
print("Here is the recommended airport list:")
print(create_available_airport_table(recommended_airport_data, player_location))
time.sleep(1)

#ask for the first destination
destination = input("Enter the ICAO code of your destination: ")
player_fuel -= cal_dis(player_base, destination) / 2
player_location = destination

#game_loop
while not game_over:
    #get the info about the current airport fuel and enemy
    airport_fuel = get_airport_amount_of_fuel(player_location)
    airport_enemy = get_airport_number_of_enemy(player_location)

    #inform player about their location and their fuel left
    player_location_info = get_name_and_city_country_of_airport(player_location)
    print(f"You arrived at {player_location_info['name']} airspace in {player_location_info['city']}, {player_location_info['country']}")
    time.sleep(1)

    #check if player come home safely
    if player_location == player_base and player_mission_completed == True:
        player_victory = True
        game_over = True
        print("Welcome back home, the greatest hero that we have ever seen!")
        time.sleep(1)
        continue
    #check if it is the enemy's base
    elif player_location == player_target:
        print("Wow, it is your target. Destroy it!")
        time.sleep(1)
        player_bonus_gained += 50
        update_airport_situation(player_location, 'destroyed')
        print("You destroyed your target and your mission is completed. Let's go home!")
        time.sleep(1)
        print(f"At the moment, your bonus is {player_bonus_gained}%.")
        time.sleep(1)
        player_mission_completed = True
        update_airport_situation(player_location, 'destroyed')
    else:
        #inform player about his/her fuel left
        print(f"You now have {player_fuel:.1f} liters of aviation gasoline and can fly up to {player_fuel * 2:.1f} km.")
        time.sleep(1)

        #ask if player want to land
        player_choice_to_land = input("Do you want to land at this airport? (yes/no) ")
        if player_choice_to_land == "yes":
            print(f"Welcome to {player_location_info['name']}! Let's see what is waiting for you.")
            time.sleep(1)
            if airport_fuel > 0:
                player_fuel += airport_fuel * (player_bonus_gained / 100 + 1);
                print(f"Congratulations! You have founded {airport_fuel} liters of aviation gasoline.")
            elif airport_enemy > 0:
                print(f"Oh my gosh, there are {airport_enemy} soldiers at this airport. Your fuel has been stolen!")
                player_fuel /= 2
            else:
                print("Sorry, there is nothing at here.")
            time.sleep(1)
        else:
            player_choice_to_destroy = input("Do you want to destroy this airport? (yes/no) ")
            if player_choice_to_destroy == "yes":
                if airport_enemy > 0:
                    player_total_enemy_killed += airport_enemy
                    player_enemy_killed += airport_enemy
                    if player_enemy_killed >= 1000:
                        player_enemy_killed -= 1000
                        player_bonus_gained += 20
                    print(f"Nice! You killed {airport_enemy} enemy's soldiers in this airport!")
                    time.sleep(1)
                    print(f"Your bonus is {player_bonus_gained}% at the moment.")
                else:
                    print("Damn, there is nothing at here!")
                    time.sleep(1)
                    print(f"Your bonus is still {player_bonus_gained}% at the moment.")
                update_airport_situation(player_location, 'destroyed')

    #continue the journey
    print("Ok, let's continue your journey.")
    time.sleep(1)

    #warn player about the low fuel
    if player_fuel <= 250:
        print(f"Be careful, your fuel is low now!")
        time.sleep(1)

    #announce the player about their fuel
    print(f"At the moment, you have {player_fuel:.1f} liters of aviation gasoline and can fly up to {player_fuel * 2:.1f} km.")
    recommended_airport_data = get_available_airports(player_location, player_fuel)

    #check if player can continue mission
    if len(recommended_airport_data) == 0:
        print("You are out of range.")
        time.sleep(1)
        game_over = True
        continue
    else:
        print("Here is the recommended airports list:")
        print(create_available_airport_table(recommended_airport_data, player_location))
        destination = input("Enter the ICAO code of the destination airport: ")
        player_fuel -= cal_dis(player_location, destination) / 2
        player_location = destination

if player_victory:
    print("Congratulations! You've won!")
else:
    print("Sorry, your enemy caught you and you were killed. However, your country still remember your noble sacrifice and your name has been written in Monument to War Heroes and Martyrs.")
    insert_details_of_loser(player_name, player_location, player_total_enemy_killed)

delete_random_airports_table()