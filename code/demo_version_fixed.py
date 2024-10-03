import mysql.connector
import story
from geopy import distance
import time

connection = mysql.connector.connect(
    host = '127.0.0.1',
    port = 3306,
    database = 'demo_version',
    user = 'root',
    password = '16102006',
    autocommit = True
)

#Game Functions:

#get_40_airports_in_Europe
def get_forty_airports_in_europe():
    sql = f"SELECT iso_country, ident, name, latitude_deg, longitude_deg, municipality FROM airport WHERE continent = 'EU' AND type = 'large_airport' AND ident NOT IN (SELECT ident FROM airport WHERE (iso_country = 'RU' OR iso_country = 'IS')) ORDER BY RAND() LIMIT 40;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

#get_fuel_info
def get_fuel():
    sql = "SELECT * FROM fuel;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

#get enemy info
def get_enemy():
    sql = "SELECT * FROM enemy;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def create_game(p_name, p_location, p_fuel, p_total_enemy_killed, p_enemy_killed, p_bonus_gained, c_airports, p_base, p_target):
    sql = "INSERT INTO game_data (name, ident, fuel, total_enemy_killed, enemy_killed, bonus_gained) VALUES (%s, %s, %s, %s, %s, %s);"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (p_name, p_location, p_fuel, p_total_enemy_killed, p_enemy_killed, p_bonus_gained))

    #add your base to the random_airports table
    sql = "INSERT INTO random_airports (ident, amount_of_fuel, number_of_enemy, situation) VALUES (%s, %s, %s, %s);"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (p_base, 0, 0, 'intact'))

    #add your target to the random_airports table
    sql = "INSERT INTO random_airports (ident, amount_of_fuel, number_of_enemy, situation) VALUES (%s, %s, %s, %s);"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (p_target, 0, 0, 'intact'))

    #get_fuel
    fuel_types = get_fuel()
    fuel_type_list = []
    for fuel_type in fuel_types:
        for i in range(0, fuel_type['probability']):
            fuel_type_list.append(fuel_type['amount'])

    #get enemy
    enemy_types = get_enemy()
    enemy_type_list = []
    for enemy_type in enemy_types:
        for i in range(0, enemy_type['probability']):
            enemy_type_list.append(enemy_type['number'])

    #print(chosen_airport)
    #add the airports with fuel to the random_airports table
    for i, j in enumerate(fuel_type_list):
        sql = "INSERT INTO random_airports (ident, amount_of_fuel, number_of_enemy, situation) VALUES (%s, %s, %s, %s);"
        cursor = connection.cursor(dictionary = True)
        cursor.execute(sql, (c_airports[i + 2]['ident'], j, 0, 'intact'))

    #add the airports with enemy to the random_airports table
    for i, j in enumerate(fuel_type_list):
        sql = "INSERT INTO random_airports (ident, amount_of_fuel, number_of_enemy, situation) VALUES (%s, %s, %s, %s);"
        cursor = connection.cursor(dictionary = True)
        cursor.execute(sql, (c_airports[i + 17]['ident'], 0, j, 'intact'))

    #add other airports to the random_airports table
    for i in range(32, 40, 1):
        sql = "INSERT INTO random_airports (ident, amount_of_fuel, number_of_enemy, situation) VALUES (%s, %s, %s, %s);"
        cursor = connection.cursor(dictionary = True)
        cursor.execute(sql, (c_airports[i]['ident'], 0, 0, 'intact'))

#calulate_the_distance_between_2_airports
def cal_dis(airport1, airport2):
    #get the coordinate of the first airport
    sql = "SELECT latitude_deg, longitude_deg FROM airport WHERE ident = %s;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (airport1,))
    coord1 = cursor.fetchone()

    #get the coordinate of the second airport
    sql = "SELECT latitude_deg, longitude_deg FROM airport WHERE ident = %s;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (airport2,))
    coord2 = cursor.fetchone()

    return distance.distance((coord1['latitude_deg'], coord1['longitude_deg']), (coord2['latitude_deg'], coord2['longitude_deg'])).km

def get_available_airports(icao, player_range):
    sql = "SELECT ident, situation FROM random_airports;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql)
    available_airports = []
    opened_airports = cursor.fetchall()
    for x in opened_airports:
        dis = cal_dis(icao, x['ident'])
        if x['situation'] == 'intact' and dis <= player_range and dis > 0:
            available_airports.append(x['ident'])

    return available_airports

#get the name of the airport
def get_name_of_airport(icao):
    sql = "SELECT name FROM airport WHERE ident = %s;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (icao, ))
    result = cursor.fetchone()
    return result['name']

#get the amount of fuel of one airport
def get_airport_amount_of_fuel(icao):
    sql = "SELECT amount_of_fuel FROM random_airports WHERE ident = %s;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (icao, ))
    result = cursor.fetchone()
    return result['amount_of_fuel']

#get the number of enemy of one airport
def get_airport_number_of_enemy(icao):
    sql = "SELECT number_of_enemy FROM random_airports WHERE ident = %s;"
    cursor = connection.cursor(dictionary = True)
    cursor.execute(sql, (icao, ))
    result = cursor.fetchone()
    return result['number_of_enemy']

#Greet:
print("Hello! Welcome to group 9's flight game! Let's start!")

#Ask if player wants to read the story
story_choice = input("Do you want to read the background story? (yes/no) ")
if story_choice == "yes":
    for each_line in story.get_story():
        print(each_line)
        time.sleep(2.5)
else:
    print("You will be regretful later.")

#Player settings:
player_name = input("What is your name? ")
player_fuel = 500
player_total_enemy_killed = 0
player_enemy_killed = 0
player_bonus_gained = 0
player_mission_completed = False

#get_40_airports_in_Europe
chosen_airport = get_forty_airports_in_europe()
player_base = chosen_airport[0]['ident']
player_target = chosen_airport[1]['ident']
player_location = player_base
game_over = False
player_victory = False

#create new game
create_game(player_name, player_location, player_fuel, player_total_enemy_killed, player_enemy_killed, player_bonus_gained, chosen_airport, player_base, player_target)

#game starts:
print("Your mission starts.")
print(f"You are at {chosen_airport[0]['name']} in {chosen_airport[0]['municipality']}. Your target is {chosen_airport[1]['name']} in {chosen_airport[1]['municipality']}.")
print(f"The military headquarter provided you with {player_fuel} liters of aviation gasoline. As a result, you can travel up to {player_fuel * 2} km.")
print("Here is the recommended airport list:")
player_available_airports = get_available_airports(player_location, player_fuel * 2)
for i in player_available_airports:
    #print(i)
    dist = cal_dis(player_location, i)
    print(f"Name: {get_name_of_airport(i)}, icao_code: {i}, distance: {dist:<.1f} km")
#ask for the first destination:
destination = input("Enter the icao code of the destination airport: ")
travelled_distance = cal_dis(player_location, destination)
player_fuel -= travelled_distance / 2
player_location = destination

while not game_over:
    #greet player when he/she arrive at one airport
    a_name = get_name_of_airport(player_location)
    airport_fuel = get_airport_amount_of_fuel(player_location)
    airport_enemy = get_airport_number_of_enemy(player_location)
    if player_location == player_base and player_mission_completed == True:
        player_victory = True
        game_over = True
        continue
    #check if it is the enemy's base
    elif player_location == player_target:
        print(f"You arrived at {a_name} airspace.")
        print("Wow, it is your target. Let's destroy it!")
        player_bonus_gained += 50
        sql = """UPDATE random_airports
SET number_of_enemy = %s, situation = %s
WHERE ident = %s;"""
        cursor = connection.cursor(dictionary = True)
        cursor.execute(sql, (0, 'destroyed', player_location))
        print("You destroyed it and your mission is completed. Let's go home!")
        player_mission_completed = True
    else:
        # ask if player want to land
        print(f"You arrived at {a_name} airspace.")
        print(f"You now have {player_fuel:.1f} liters of aviation gasoline and can fly up to {player_fuel * 2:.1f} km.")
        player_choice_to_land = input("Do you want to land at this airport? (yes/no) ")
        if player_choice_to_land == "yes":
            print(f"Welcome to {a_name}! Let's see what is waiting for you.")
            if airport_fuel > 0:
                print(f"Congratulations! You have founded {airport_fuel} liters of aviation gasoline.")
                player_fuel += airport_fuel * (player_bonus_gained / 100 + 1);
            elif airport_enemy > 0:
                print(f"Oh my gosh, there are {airport_enemy} soldiers at this airport. Your fuel has been stolen!")
                player_fuel /= 2
            else:
                print("Sorry, there is nothing at here. ")
        else:
            # ask if player want to destroy the airport
            player_choice_to_destroy = input("Do you want to destroy this airport? (yes/no) ")
            if player_choice_to_destroy == "yes":
                if airport_enemy > 0:
                    player_total_enemy_killed += airport_enemy
                    player_enemy_killed += airport_enemy
                    if player_enemy_killed >= 1000:
                        player_enemy_killed -= 1000
                        player_bonus_gained += 20
                    print(f"Nice! You killed {airport_enemy} enemy's soldiers in this airport!")
                    print(f"Your bonus is {player_bonus_gained}% at the moment.")
                else:
                    print("Damn, there is nothing at here!")
                    print(f"Your bonus is still {player_bonus_gained}% at the moment.")
                sql = """UPDATE random_airports
                        SET amount_of_fuel = %s, number_of_enemy = %s, situation = %s
                        WHERE ident = %s;"""
                cursor = connection.cursor(dictionary = True)
                cursor.execute(sql, (0, 0, 'destroyed', player_location))

    print("Ok, let's continue your journey.")
    print(f"You now have {player_fuel:.1f} liters of aviation gasoline and can fly up to {player_fuel * 2:.1f} km.")
    player_available_airports = get_available_airports(player_location, player_fuel * 2)
    if len(player_available_airports) == 0:
        print("You are out of range.")
        game_over = True
    else:
        print("Here is the recommended airport list:")
        for i in player_available_airports:
            dist = cal_dis(player_location, i)
            print(f"Name: {get_name_of_airport(i)}, icao_code: {i}, distance: {dist:.1f} km")
        destination = input("Enter the icao code of the destination airport: ")
        travelled_distance = cal_dis(player_location, destination)
        player_fuel -= travelled_distance / 2
        player_location = destination

if player_victory:
    print("Congratulations! You've won!")
else:
    print("Sorry, your enemy catched you and you were killed. However, your country still remember your noble sacrifice and your name has been written in Monument to War Heroes and Martyrs.")

sql = "DELETE FROM random_airports;"
cursor = connection.cursor()
cursor.execute(sql)
