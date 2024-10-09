import textwrap

story = '''Your country are in a war with another country. 
You are a combat pilot, and you always want to destroy the enemy's infrastructure as much as you can. One day, you have an ultimate mission: destroy enemy's main airports.

You set off on your journey, from your base's airport. You will be provided an amount of aviation gasoline. Be careful with them, because you will absolutely be killed by your enemy if you run out of fuel while completing your mission.

Before start your journey, you should remember important details that our spies have collected.

First, there are 15 airports with enemy, and in each airport, it has three levels of enemy:
- Outpost: 500 enemies (9 airports)
- Stronghold: 700 enemies (4 airports)
- Big Port: 900 enemies (2 airports)

Second, there are 15 airports with fuel, and in each airport, it has three levels of amount of fuel left:
- Rich: 800 liters (3 airports)
- Medium: 500 liters (5 airports)
- Poor: 300 liters (7 airports)

When you arrive at the airspace of an airport, you were congratulated by a message on your control display board that said "Welcome to X Airport! You have X liters of aviation gasoline left.

After that, you will receive a notification that make you choose either one of two choices:
- The first choice is to destroy the airport. If the airport has any enemies, you may gain a bonus. If the airport has some gasoline, you cannot take it in the next time you arrive at the airport.
- The second choice is to land at the airport. It will be a big problem if the airport has enemies, but do not worry. You will not be killed because you were equipped with very strong weapon. However, the enemies are still able to steal half of your fuel left. On the other hand, if the airport has some fuel, all of them will be yours.

Both choice have the advantages and disadvantages. So, be careful when making any decisions!

When you arrive at the airspace of enemy's main airport, you have only one choice: Destroy it!. You will receive a great bonus after destroying this airport. 

Now, you have the last mission: Come home safely. Although the enemy's main airport was destroyed, they are still very strong. So, do not soon relax.

When you come back your base, you will win the game. Your country will soon win the war. You will become the hero of your country. You now can retire and enjoy your succeed.

If you die while arriving back at your base, you still cannot win the game. Your country still soon win the war. You still become the hero of your country, but you cannot enjoy your succeed because now you are a great martyrs.

If you cannot destroy the enemy's base and be killed, you will lose and become a martyr. However, only a little people remember you and you will soon be forgotten.
'''

wrapper = textwrap.TextWrapper(width = 80, break_long_words = False, replace_whitespace = False)

word_list = wrapper.wrap(text = story)

def get_story():
    return word_list