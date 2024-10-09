--
-- Creating the table 'game_data'
--

CREATE TABLE game_data
(
	id int AUTO_INCREMENT,
	name varchar(40) NULL,
	ident varchar(10) NULL,
	fuel int NULL,
	total_enemy_killed int NULL,
	enemy_killed int NULL,
	bonus_gained int NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (ident) REFERENCES airport(ident)
)
	charset = latin1;

--
-- Creating the table 'fuel'
--

CREATE TABLE fuel
(
	id int NOT NULL,
	type varchar(40) NULL,
	amount int NULL,
	probability int NULL,
	PRIMARY KEY (id)
)
	charset = latin1;

--
-- Dumping data for table 'fuel'
--

INSERT INTO fuel (id, type, amount, probability)
VALUES (1, 'Poor', 300, 7),
       (2, 'Medium', 500, 5),
       (3, 'Rich', 800, 3);

--
-- Creating the table 'enemy'
--

CREATE TABLE enemy
(
	id int NOT NULL,
	type varchar(40) NULL,
	number int NULL,
	probability int NULL,
	PRIMARY KEY (id)
)
	charset = latin1;

--
-- Dumping data for table 'enemy'
--

INSERT INTO enemy (id, type, number, probability)
VALUES (1, 'Outpost', 500, 9),
       (2, 'Stronghold', 700, 4),
       (3, 'Big_port', 900, 2);
	
-- 
-- Creating table 'random_airports'
--
CREATE TABLE random_airports
(
	id int AUTO_INCREMENT PRIMARY KEY,
	ident varchar(10), 
	amount_of_fuel int NULL,
	number_of_enemy int NULL,
	situation varchar(40) NULL,
	FOREIGN KEY (ident) REFERENCES airport(ident)
)
	charset = latin1;
