Existing:
airport, country

New:
game data:
- screen name
- password
- location (FK to airport)
- fuel
- total enemy killed
- enemy killed
- bonus gained

fuel:
- type
- how many
- probability

enemy:
- type
- how many
- probability

random airports: 
- icao (FK to airport)
- how much gasoline (FK to fuel)
- how many enemy (FK to enemy)
- is it visited/destroyed/base/target (FK to game data)

NOTE: The difference between enemy killed and total enemy killed:
- Total enemy killed is the number of enemy's soldiers that you have killed since you started to play game.
- Enemy killed is used to count the bonus that you gained. If it is bigger than or equal to 1,000, bonus will be added 20% and enemy killed will be minus by 1,000.
