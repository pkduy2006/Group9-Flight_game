'use strict';

//set up the time
function updateTime() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const seconds = now.getSeconds().toString().padStart(2, '0');
  document.getElementById('time').innerHTML = `${hours}:${minutes}:${seconds}`;
}
updateTime();
setInterval(updateTime, 1000);

const now = new Date();
const day = now.getDate().toString().padStart(2, '0');
const month = (now.getMonth() + 1).toString().padStart(2, '0');
const year = now.getFullYear();
document.getElementById('date').innerHTML = `${day}/${month}/${year}`;

//open the map
const map = L.map('map', {tap: false});
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 20,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
map.setView([21.2187, 105.8042], 3);

//global variables
let base, target, cur, pre = undefined, playerBonus = 0, enemies_killed = 0, total_enemies_killed = 0;
let status = {'Fuel': 1000, 'Trip': 0, 'Name': '', 'missionCompleted': false};
let airportData = [];
const apiWeatherKey = '0170ed82183397732f6349d276636ac8';
const airportMarkers = L.featureGroup().addTo(map);
const directions = ["North (N)", "North-Northeast (NNE)", "Northeast (NE)", "East-Northeast (ENE)", "East (E)", "East-Southeast (ESE)", "Southeast (SE)", "South-Southeast (SSE)", "South (S)", "South-Southwest (SSW)", "Southwest (SW)", "West-Southwest (WSW)", "West (W)", "West-Northwest (WNW)", "Northwest (NW)", "North-Northwest (NNW)"];

//icons of the map
const redIcon = L.divIcon({className: 'red-icon'});
const blackIcon = L.divIcon({className: 'black-icon'});

//function to get the data
async function getData(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error('Invalid server input!');
  const data = await response.json();
  return data;
}

//function to convert degree to radian
function degreesToRadians(degrees)  {
  return degrees * Math.PI / 180;
}

//function to calculate the distance between 2 airports
function calDis(lat1, lon1, lat2, lon2)  {
  const earthRadiusKm = 6371;

  const dLat = degreesToRadians(lat2 - lat1);
  const dLon = degreesToRadians(lon2 - lon1);

  lat1 = degreesToRadians(lat1);
  lat2 = degreesToRadians(lat2);

  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(lat1) * Math.cos(lat2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(earthRadiusKm * c);
}

//function to load the resource of an airport
function load_the_resource(type, airports) {
  let index = 0;
  for (let i = 0; i < type.length; i++) {
    //console.log(type[i].number);
    for (let j = 0; j < type[i].number; j++)  {
      airports[index].garrison = type[i].garrison;
      airports[index].storage = type[i].storage;
      index++;
    }
  }

  return airports;
}

// function to get the name of the player
async function getName()  {
  const name = await prompt('What is your name?');
  return String(name);
}

//function to update base
function updateBase (icao, name, municipality, country) {
  document.querySelector('#icao-base').innerHTML = `ICAO: ${icao}`;
  document.querySelector('#name-base').innerHTML = `Name: ${name}`;
  document.querySelector('#municipality-base').innerHTML = `Municipality: ${municipality}`;
  document.querySelector('#country-base').innerHTML = `Country: ${country}`;
}

//function to update the target
function updateTarget (icao, name, municipality, country) {
  document.querySelector('#icao-target').innerHTML = `ICAO: ${icao}`;
  document.querySelector('#name-target').innerHTML = `Name: ${name}`;
  document.querySelector('#municipality-target').innerHTML = `Municipality: ${municipality}`;
  document.querySelector('#country-target').innerHTML = `Country: ${country}`;
}

//function to get the id of the airport
function getID(icao)  {
  let id = undefined;
  for (let i = 0; i < airportData.length; i++)  {
    if (airportData[i].ident === icao)  {
      id = i;
      break;
    }
  }
  return id;
}

//function to update the weather data
async function updateWeather(icao)  {
  try {
    const id = getID(icao);
    const lat = airportData[id].latitude_deg;
    const lon = airportData[id].longitude_deg;
    const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiWeatherKey}&units=metric`);
    if (!response.ok) throw new Error('Fetch failed!');
    const json_response = await response.json();
    document.querySelector('#temperature').innerHTML = `Temperature: ${json_response.main.temp} °C`;
    document.querySelector('#wind-speed').innerHTML = `Wind speed: ${json_response.wind.speed} km/h`;
    console.log(json_response.wind.deg);
    const windDegree = json_response.wind.deg;
    console.log(windDegree);
    const index = Math.round(windDegree / 22.5) % 16;
    console.log(index);
    console.log(directions[index]);
    document.querySelector('#wind-direction-by-degree').innerHTML = `Wind direction by degree: ${json_response.wind.deg}`;
    document.querySelector('#wind-dỉrection').innerHTML = `Wind direction: ${directions[index]}`;
    document.querySelector('#description').innerHTML = `Description: ${json_response.weather[0].description}`;
  } catch (error) {
    console.log(error.message);
  }
}

// function to check whether there are some fuels in the airport
function checkFuel(icao)  {
  const id = getID(icao);
  return airportData[id].storage;
}

//function to check whether there are some enemies in the airport
function checkEnemy(icao) {
  const id = getID(icao);
  return airportData[id].storage;
}

//function to check if the player is lose
function playerLose() {
  const cur_id = getID(cur);
  for (let i = 0; i < airportData.length; i++)  {
    if (cur_id === i || !airportData[i].active)
      continue;
    const dis = calDis(airportData[cur_id].latitude_deg, airportData[cur_id].longitude_deg, airportData[i].latitude_deg, airportData[i].longitude_deg);
    if (dis <= status.Fuel * 2)
      return true;
  }
  return false;
}

//function to update the settings after arriving at new airport
async function arriveSetup()  {
  //console.log(pre);
  //console.log(cur);
  const cur_id = getID(cur);
  const pre_id = getID(pre);
  const disPreCur = calDis(airportData[pre_id].latitude_deg, airportData[pre_id].longitude_deg, airportData[cur_id].latitude_deg, airportData[cur_id].longitude_deg);
  status.Fuel -= Math.round(disPreCur / 2);
  status.Trip += Math.round(disPreCur);
  document.querySelector('#fuel-status').innerHTML = `Fuel: ${status.Fuel} L`;
  document.querySelector('#trip-dis').innerHTML = `Trip: ${status.Trip} km`;
  document.querySelector('#icao-location').innerHTML = `ICAO: ${airportData[cur_id].ident}`;
  document.querySelector('#name-location').innerHTML = `Name: ${airportData[cur_id].name}`;
  document.querySelector('#municipality-location').innerHTML = `Municipality: ${airportData[cur_id].municipality}`;
  document.querySelector('#country-location').innerHTML = `Country: ${airportData[cur_id].country}`;
  await alert(`Welcome to ${airportData[cur_id].name}`);
  await updateWeather(cur);

  if (cur === target) {
    await alert('You arrived at the target. Destroy it');
    const target_id = getID(target);
    airportData[target_id].active = false;
    status.missionCompleted = true;
    playerBonus += 50;
    document.querySelector('#player-bonus').innerHTML = `Bonus: ${playerBonus} %`;
    document.querySelector('#player-mission').innerHTML = 'Mission completed: yes';
  } else if (cur === base)  {
    if (status.missionCompleted === true) {
      await alert('Welcome home our hero');
    } else  {
      await alert('Your mission is failed');
    }
  } else  {
    const land = await confirm('Do you want to land at this airport?');
    const haveFuel = checkFuel(cur);
    const haveEnemy = checkEnemy(cur);
    if (land)  {
      if (haveFuel > 0) {
        status.Fuel += Math.round(haveFuel * (playerBonus / 100 + 1));
        await alert(`Congratulation! You have found ${haveFuel} litre of gasoline here.`);
        document.querySelector('#fuel-status').innerHTML = `Fuel: ${status.Fuel} L`;
      } else
        await alert('Damn, there is no fuels at here.');
      if (haveEnemy > 0)  {
        status.Fuel /= 2;
        status.Fuel = Math.round(status.Fuel);
        await alert('Damn, enemies found your aircraft and your fuel was stolen.');
        document.querySelector('#fuel-status').innerHTML = `Fuel: ${status.Fuel} L`;
      }
    } else  {
      const destroy = confirm('Do you want to destroy this airport?');
      if (destroy)  {
        airportData[cur_id].active = false;
        if (haveEnemy > 0)  {
          enemies_killed += haveEnemy;
          total_enemies_killed += haveEnemy;
          document.querySelector('#player-enemies').innerHTML = `Enemies killed: ${total_enemies_killed}`;
          await alert(`Nice! You killed ${haveEnemy} enemy soldiers`);
          while (enemies_killed >= 1000) {
            enemies_killed -= 1000;
            playerBonus += 20;

            document.querySelector('#player-bonus').innerHTML = `Bonus: ${playerBonus} %`;
            await alert(`Now your bonus is ${playerBonus} %`);
          }
        } else  {
          await alert('Damn, there is no one at here!');
        }
      } else
        await alert(`Let's continue your journey`);
    }
  }
  const checkLose = playerLose();
  if (!checkLose) {
    await alert('You are not able to travel to any other airport and you lost.');
  } else  {
    airportMarkers.clearLayers();
    for (let i = 0; i < airportData.length; i++) {
      const marker = L.marker([airportData[i].latitude_deg, airportData[i].longitude_deg]).addTo(map);
      airportMarkers.addLayer(marker);
      if (airportData[i].ident === base)
        marker.setIcon(redIcon);
      if (airportData[i].ident === target)
        marker.setIcon(blackIcon);
      if (airportData[i].ident === cur) {
        marker.bindPopup(`You are here <b>${airportData[i].name}</b>`);
        marker.openPopup();
      } else  {
        const popupContent = document.createElement('div');
        const h4 = document.createElement('h4');
        h4.innerHTML = airportData[i].name;
        popupContent.append(h4);
        const p = document.createElement('p');
        const disData = calDis(airportData[cur_id].latitude_deg, airportData[cur_id].longitude_deg, airportData[i].latitude_deg, airportData[i].longitude_deg);
        console.log(airportData[i].active);
        if (!airportData[i].active)
          p.innerHTML = 'Unavailable';
        else
          p.innerHTML = `Distance: ${disData} km`;
        popupContent.append(p);
        if (airportData[i].active)  {
          const goButton = document.createElement('button');
          goButton.classList.add('button');
          goButton.innerHTML = 'Fly here';
          popupContent.append(goButton);
          goButton.addEventListener('click', async function() {
            if (disData <= status.Fuel * 2) {
              pre = cur;
              cur = airportData[i].ident;
              await arriveSetup();
            } else  {
              await alert('You do not have enough fuel to go to this airport. Please choose another airport');
            }
          });
        }
        marker.bindPopup(popupContent);
      }
    }
  }
}

//function to shuffle the airportData
function shuffle(array) {
  let currentIndex = array.length;

  while (currentIndex !== 0) {
    let randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;

    [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
  }
}

//function to check if the base and airport is far enough
function checkBaseAndTarget(airports) {
  let dis = calDis(airports[0].latitude_deg, airports[0].longitude_deg, airports[1].latitude_deg, airports[1].longitude_deg);
  let cnt = 0;
  while (dis <= 2000 && cnt <= 10) {
    shuffle(airports);
    cnt++;
    //console.log(airportData[0].latitude_deg, airportData[0].longitude_deg, airportData[1].latitude_deg, airportData[1].longitude_deg);
    dis = calDis(airports[0].latitude_deg, airports[0].longitude_deg, airports[1].latitude_deg, airports[1].longitude_deg);
  }
  //console.log(dis);
  return airports;
}

async function gameSetup()  {
  try {
    const playerName = await getName();
    status.Name = playerName;
    document.querySelector('#fuel-status').innerHTML = `Fuel: ${status.Fuel} L`;
    document.querySelector('#trip-dis').innerHTML = `Trip: ${status.Trip} km`;
    document.querySelector('#player-name').innerHTML = `Name: ${status.Name}`;
    document.querySelector('#player-mission').innerHTML = `Mission completed: No`;

    let airportBasicData = await getData('http://127.0.0.1:5000/airports');
    airportBasicData = checkBaseAndTarget(airportBasicData);
    //console.log(airportBasicData);
    const typeData = await getData('http://127.0.0.1:5000/type');
    //console.log(typeData);

    airportData = load_the_resource(typeData, airportBasicData);
    //console.log(airportData);
    base = airportData[0].ident;
    updateBase(base, airportData[0].name, airportData[0].municipality, airportData[0].country);
    target = airportData[1].ident;
    updateTarget(target, airportData[1].name, airportData[1].municipality, airportData[1].country);
    cur = base;
    const cur_id = getID(cur);
    document.querySelector('#icao-location').innerHTML = `ICAO: ${airportData[cur_id].ident}`;
    document.querySelector('#name-location').innerHTML = `Name: ${airportData[cur_id].name}`;
    document.querySelector('#municipality-location').innerHTML = `Municipality: ${airportData[cur_id].municipality}`;
    document.querySelector('#country-location').innerHTML = `Country: ${airportData[cur_id].country}`;

    await updateWeather(cur);

    for (let i = 0; i < airportData.length; i++)  {
      const marker = L.marker([airportData[i].latitude_deg, airportData[i].longitude_deg]).addTo(map);
      airportMarkers.addLayer(marker);
      airportData[i].active = true;
      if (airportData[i].ident === base) {
        marker.setIcon(redIcon);
      }
      if(airportData[i].ident === target)  {
        marker.setIcon(blackIcon);
      }
      if(airportData[i].ident === cur) {
        marker.bindPopup(`You are here <b>${airportData[i].name}</b>.`);
        marker.openPopup();
      } else  {
        const popupContent = document.createElement('div');
        const h4 = document.createElement('h4');
        h4.innerHTML = airportData[i].name;
        popupContent.append(h4);
        const p = document.createElement('p');
        const disData = await calDis(airportData[cur_id].latitude_deg, airportData[cur_id].longitude_deg, airportData[i].latitude_deg, airportData[i].longitude_deg);
        p.innerHTML = `Distance: ${disData} km`;
        popupContent.append(p);
        const goButton = document.createElement('button');
        goButton.classList.add('button');
        goButton.innerHTML = 'Fly Here';
        popupContent.append(goButton);
        marker.bindPopup(popupContent);
        goButton.addEventListener('click', async function() {
          if(disData <= status.Fuel * 2)  {
            pre = cur;
            cur = airportData[i].ident;
            await arriveSetup();
          } else  {
            await alert('You do not have enough fuel to travel to this airport. Please select again');
          }
        });
      }
    }
  } catch (error) {
    console.log(error);
  }
}

gameSetup();