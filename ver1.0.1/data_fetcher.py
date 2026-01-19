import requests
import pandas as pd

BASE_URL = "https://api.jolpi.ca/ergast/f1"

# --------------------------
# Race Data
# --------------------------
def fetch_races(year: int) -> pd.DataFrame:
    """Fetch all races for a given year, with custom raceId."""
    url = f"{BASE_URL}/{year}/races.json"
    response = requests.get(url)
    data = response.json()

    races = []
    for race in data['MRData']['RaceTable']['Races']:
        round_num = int(race['round'])
        races.append({
            'raceId': f"{year}_{round_num}",
            'round': round_num,
            'raceName': race['raceName'],
            'year': int(race['season']),
            'date': race['date'],
            'circuit': race['Circuit']['circuitName'],
            'circuitId': race['Circuit']['circuitId']
        })
    return pd.DataFrame(races)

# --------------------------
# Qualifying
# --------------------------
def fetch_qualifying(year: int, round_num: int) -> pd.DataFrame:
    """Fetch qualifying results for a specific race."""
    url = f"{BASE_URL}/{year}/{round_num}/qualifying.json"
    response = requests.get(url)
    data = response.json()

    results = []
    qual_lists = data['MRData']['QualifyingTable'].get('Races', [])
    if not qual_lists:
        return pd.DataFrame(results)

    qualifying_results = qual_lists[0].get('QualifyingResults', [])
    for q in qualifying_results:
        results.append({
            'raceId': f"{year}_{round_num}",
            'driverId': q['Driver']['driverId'],
            'driverName': q['Driver']['givenName'] + ' ' + q['Driver']['familyName'],
            'position': int(q['position']),
            'constructorId': q['Constructor']['constructorId'],
            'constructor': q['Constructor']['name']
        })
    return pd.DataFrame(results)

# --------------------------
# Race Results
# --------------------------
def fetch_results(year: int, round_num: int) -> pd.DataFrame:
    """Fetch race results for a specific race."""
    url = f"{BASE_URL}/{year}/{round_num}/results.json"
    response = requests.get(url)
    data = response.json()

    results = []
    races = data['MRData']['RaceTable'].get('Races', [])
    if not races:
        return pd.DataFrame(results)

    for r in races[0].get('Results', []):
        results.append({
            'raceId': f"{year}_{round_num}",
            'driverId': r['Driver']['driverId'],
            'driverName': r['Driver']['givenName'] + ' ' + r['Driver']['familyName'],
            'position': int(r['position']) if r['position'].isdigit() else None,
            'points': float(r['points']),
            'constructorId': r['Constructor']['constructorId'],
            'constructor': r['Constructor']['name'],
            'grid': int(r['grid']) if r['grid'].isdigit() else None,
            'laps': int(r['laps']),
            'status': r.get('status', 'Unknown')
        })
    return pd.DataFrame(results)

# --------------------------
# Pit Stops
# --------------------------
def fetch_pit_stops(year: int, round_num: int) -> pd.DataFrame:
    """Fetch pit stop data for a specific race."""
    url = f"{BASE_URL}/{year}/{round_num}/pitstops.json"
    response = requests.get(url)
    data = response.json()

    pit_stops = []
    races = data['MRData']['RaceTable'].get('Races', [])
    if not races:
        return pd.DataFrame(pit_stops)

    for ps in races[0].get('PitStops', []):
        pit_stops.append({
            'raceId': f"{year}_{round_num}",
            'driverId': ps['driverId'],
            'stop': int(ps['stop']),
            'lap': int(ps['lap']),
            'duration': ps.get('duration', None)
        })
    return pd.DataFrame(pit_stops)

# --------------------------
# Driver Standings
# --------------------------
def fetch_season_standings(year: int) -> pd.DataFrame:
    """Fetch driver standings for a season."""
    url = f"{BASE_URL}/{year}/driverStandings.json"
    response = requests.get(url)
    data = response.json()

    standings = []
    standings_lists = data['MRData']['StandingsTable'].get('StandingsLists', [])
    if not standings_lists:
        return pd.DataFrame(standings)

    for driver in standings_lists[0]['DriverStandings']:
        standings.append({
            'driverId': driver['Driver']['driverId'],
            'driverName': driver['Driver']['givenName'] + ' ' + driver['Driver']['familyName'],
            'position': int(driver['position']),
            'points': float(driver['points']),
            'wins': int(driver['wins']),
            'constructor': driver['Constructors'][0]['name']
        })
    return pd.DataFrame(standings)

# --------------------------
# Constructor Standings
# --------------------------
def fetch_constructor_standings(year: int) -> pd.DataFrame:
    """Fetch constructor standings for a season."""
    url = f"{BASE_URL}/{year}/constructorStandings.json"
    response = requests.get(url)
    data = response.json()

    standings = []
    standings_lists = data['MRData']['StandingsTable'].get('StandingsLists', [])
    if not standings_lists:
        return pd.DataFrame(standings)

    for c in standings_lists[0]['ConstructorStandings']:
        standings.append({
            'constructorId': c['Constructor']['constructorId'],
            'constructor': c['Constructor']['name'],
            'position': int(c['position']),
            'points': float(c['points']),
            'wins': int(c['wins'])
        })
    return pd.DataFrame(standings)
