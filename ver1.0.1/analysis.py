import pandas as pd
import numpy as np
from scipy import stats
from data_fetcher import (
    fetch_results, fetch_qualifying, fetch_races, 
    fetch_season_standings, fetch_pit_stops, fetch_constructor_standings
)

# --------------------------
# QUALIFYING vs RACE ANALYSIS
# --------------------------
def analyze_qualifying_impact(year: int) -> pd.DataFrame:
    """Analyze correlation between qualifying position and race finish."""
    races = fetch_races(year)
    
    analysis_results = []
    for _, race in races.iterrows():
        try:
            qual = fetch_qualifying(year, int(race['round']))
            results = fetch_results(year, int(race['round']))
            
            if qual.empty or results.empty:
                continue
            
            merged = qual.merge(results[['driverId', 'position']], on='driverId', suffixes=('_qual', '_race'))
            merged = merged[merged['position_race'].notna()]
            
            if len(merged) > 3:
                correlation, p_value = stats.spearmanr(merged['position'], merged['position_race'])
                analysis_results.append({
                    'race': race['raceName'],
                    'round': race['round'],
                    'correlation': correlation,
                    'p_value': p_value,
                    'samples': len(merged)
                })
        except:
            continue
    
    return pd.DataFrame(analysis_results)
# --------------------------
# DRIVER CONSISTENCY METRICS
# --------------------------
def calculate_driver_consistency(year: int) -> pd.DataFrame:
    """Calculate comprehensive consistency and reliability metrics for drivers."""
    races = fetch_races(year)
    driver_performances = {}
    
    for _, race in races.iterrows():
        try:
            results = fetch_results(year, int(race['round']))
            for _, driver in results.iterrows():
                driver_id = driver['driverId']
                if driver_id not in driver_performances:
                    driver_performances[driver_id] = {
                        'name': driver['driverName'],
                        'constructor': driver['constructor'],
                        'positions': [],
                        'points': 0,
                        'races_completed': 0,
                        'races_dnf': 0
                    }
                if pd.notna(driver['position']):
                    driver_performances[driver_id]['positions'].append(driver['position'])
                    driver_performances[driver_id]['races_completed'] += 1
                else:
                    driver_performances[driver_id]['races_dnf'] += 1
                driver_performances[driver_id]['points'] += driver['points']
        except:
            continue
    
    consistency = []
    for driver_id, data in driver_performances.items():
        if len(data['positions']) > 0:
            podium_count = sum(1 for p in data['positions'] if p <= 3)
            points_per_race = data['points'] / (data['races_completed'] + data['races_dnf']) if (data['races_completed'] + data['races_dnf']) > 0 else 0
            
            consistency.append({
                'driverId': driver_id,
                'driver': data['name'],
                'constructor': data['constructor'],
                'races_started': data['races_completed'] + data['races_dnf'],
                'races_completed': data['races_completed'],
                'races_dnf': data['races_dnf'],
                'completion_rate': data['races_completed'] / (data['races_completed'] + data['races_dnf']) if (data['races_completed'] + data['races_dnf']) > 0 else 0,
                'avgPosition': np.mean(data['positions']),
                'medianPosition': np.median(data['positions']),
                'stdPosition': np.std(data['positions']) if len(data['positions']) > 1 else 0,
                'podiums': podium_count,
                'totalPoints': data['points'],
                'pointsPerRace': points_per_race
            })
    
    return pd.DataFrame(consistency).sort_values('avgPosition')

def calculate_driver_career_trajectory(start_year: int, end_year: int, driver_id: str) -> pd.DataFrame:
    """Track a driver's career performance across multiple seasons."""
    trajectory = []
    
    for year in range(start_year, end_year + 1):
        try:
            standings = fetch_season_standings(year)
            driver_data = standings[standings['driverId'] == driver_id]
            
            if not driver_data.empty:
                row = driver_data.iloc[0]
                
                # Calculate seasonal stats
                races = fetch_races(year)
                season_stats = {'positions': [], 'points_earned': 0, 'races_completed': 0}
                
                for _, race in races.iterrows():
                    try:
                        results = fetch_results(year, int(race['round']))
                        driver_race = results[results['driverId'] == driver_id]
                        if not driver_race.empty:
                            if pd.notna(driver_race.iloc[0]['position']):
                                season_stats['positions'].append(driver_race.iloc[0]['position'])
                                season_stats['races_completed'] += 1
                    except:
                        pass
                
                trajectory.append({
                    'year': year,
                    'position': row['position'],
                    'points': row['points'],
                    'wins': row['wins'],
                    'constructor': row['constructor'],
                    'avgPosition': np.mean(season_stats['positions']) if season_stats['positions'] else None,
                    'races_completed': season_stats['races_completed']
                })
        except:
            continue
    
    return pd.DataFrame(trajectory)

# --------------------------
# CONSTRUCTOR ANALYSIS
# --------------------------
def analyze_team_performance(year: int) -> pd.DataFrame:
    """Analyze constructor dominance and performance metrics across season."""
    standings = fetch_season_standings(year)
    races = fetch_races(year)
    
    constructor_stats = {}
    
    for _, race in races.iterrows():
        try:
            results = fetch_results(year, int(race['round']))
            for _, driver in results.iterrows():
                constructor = driver['constructor']
                if constructor not in constructor_stats:
                    constructor_stats[constructor] = {
                        'totalPoints': 0,
                        'totalWins': 0,
                        'podiums': 0,
                        'races': 0,
                        'positions': []
                    }
                constructor_stats[constructor]['totalPoints'] += driver['points']
                if pd.notna(driver['position']):
                    constructor_stats[constructor]['races'] += 1
                    constructor_stats[constructor]['positions'].append(driver['position'])
                    if driver['position'] == 1:
                        constructor_stats[constructor]['totalWins'] += 1
                    if driver['position'] <= 3:
                        constructor_stats[constructor]['podiums'] += 1
        except:
            continue
    
    team_data = []
    for constructor, stats_dict in constructor_stats.items():
        team_data.append({
            'constructor': constructor,
            'totalPoints': stats_dict['totalPoints'],
            'totalWins': stats_dict['totalWins'],
            'podiums': stats_dict['podiums'],
            'avgPosition': np.mean(stats_dict['positions']) if stats_dict['positions'] else None,
            'races_participated': stats_dict['races']
        })
    
    return pd.DataFrame(team_data).sort_values('totalPoints', ascending=False)

def analyze_constructor_dominance_trend(start_year: int, end_year: int) -> pd.DataFrame:
    """Track constructor dominance across multiple seasons."""
    dominance_data = []
    
    for year in range(start_year, end_year + 1):
        try:
            standings = fetch_constructor_standings(year)
            for _, team in standings.iterrows():
                dominance_data.append({
                    'year': year,
                    'constructor': team['constructor'],
                    'points': team['points'],
                    'wins': team['wins'],
                    'position': team['position']
                })
        except:
            continue
    
    return pd.DataFrame(dominance_data)

# --------------------------
# TEAMMATE ANALYSIS
# --------------------------
def analyze_teammate_performance(year: int) -> pd.DataFrame:
    """Compare teammate head-to-head performance."""
    races = fetch_races(year)
    constructor_drivers = {}
    
    for _, race in races.iterrows():
        try:
            results = fetch_results(year, int(race['round']))
            for _, driver in results.iterrows():
                constructor = driver['constructor']
                if constructor not in constructor_drivers:
                    constructor_drivers[constructor] = {}
                
                driver_id = driver['driverId']
                if driver_id not in constructor_drivers[constructor]:
                    constructor_drivers[constructor][driver_id] = {
                        'name': driver['driverName'],
                        'positions': [],
                        'points': 0,
                        'races': 0
                    }
                
                if pd.notna(driver['position']):
                    constructor_drivers[constructor][driver_id]['positions'].append(driver['position'])
                    constructor_drivers[constructor][driver_id]['races'] += 1
                constructor_drivers[constructor][driver_id]['points'] += driver['points']
        except:
            continue
    
    comparisons = []
    for constructor, drivers in constructor_drivers.items():
        if len(drivers) == 2:
            driver_list = list(drivers.values())
            driver_ids = list(drivers.keys())
            
            if (driver_list[0]['races'] > 0 and driver_list[1]['races'] > 0):
                comparisons.append({
                    'constructor': constructor,
                    'driver1': driver_list[0]['name'],
                    'driver2': driver_list[1]['name'],
                    'driver1_avgPos': np.mean(driver_list[0]['positions']),
                    'driver2_avgPos': np.mean(driver_list[1]['positions']),
                    'driver1_points': driver_list[0]['points'],
                    'driver2_points': driver_list[1]['points'],
                    'driver1_races': driver_list[0]['races'],
                    'driver2_races': driver_list[1]['races']
                })
    
    return pd.DataFrame(comparisons)

# --------------------------
# PIT STOP ANALYSIS
# --------------------------
def analyze_pit_stop_performance(year: int) -> pd.DataFrame:
    """Measure pit stop efficiency and impact on race results."""
    races = fetch_races(year)
    pit_stop_data = {}
    
    for _, race in races.iterrows():
        try:
            pit_stops = fetch_pit_stops(year, int(race['round']))
            results = fetch_results(year, int(race['round']))
            
            if pit_stops.empty or results.empty:
                continue
            
            for _, ps in pit_stops.iterrows():
                driver_id = ps['driverId']
                if driver_id not in pit_stop_data:
                    pit_stop_data[driver_id] = {
                        'driver': results[results['driverId'] == driver_id]['driverName'].values[0] if len(results[results['driverId'] == driver_id]) > 0 else 'Unknown',
                        'total_stops': 0,
                        'stop_durations': []
                    }
                
                pit_stop_data[driver_id]['total_stops'] += 1
                if ps['duration']:
                    try:
                        pit_stop_data[driver_id]['stop_durations'].append(float(ps['duration']))
                    except:
                        pass
        except:
            continue
    
    pit_analysis = []
    for driver_id, data in pit_stop_data.items():
        if data['stop_durations']:
            pit_analysis.append({
                'driverId': driver_id,
                'driver': data['driver'],
                'total_stops': data['total_stops'],
                'avg_stop_duration': np.mean(data['stop_durations']),
                'min_stop_duration': np.min(data['stop_durations']),
                'max_stop_duration': np.max(data['stop_durations'])
            })
    
    return pd.DataFrame(pit_analysis).sort_values('avg_stop_duration') if pit_analysis else pd.DataFrame()

# --------------------------
# CIRCUIT SUITABILITY
# --------------------------
def analyze_track_suitability(start_year: int, end_year: int, driver_id: str) -> pd.DataFrame:
    """Evaluate driver performance across different circuits."""
    circuit_performance = {}
    
    for year in range(start_year, end_year + 1):
        try:
            races = fetch_races(year)
            for _, race in races.iterrows():
                try:
                    results = fetch_results(year, int(race['round']))
                    driver_results = results[results['driverId'] == driver_id]
                    
                    if not driver_results.empty:
                        circuit = race['circuit']
                        if circuit not in circuit_performance:
                            circuit_performance[circuit] = {
                                'positions': [],
                                'points': 0,
                                'races': 0
                            }
                        
                        driver_row = driver_results.iloc[0]
                        if pd.notna(driver_row['position']):
                            circuit_performance[circuit]['positions'].append(driver_row['position'])
                            circuit_performance[circuit]['races'] += 1
                        circuit_performance[circuit]['points'] += driver_row['points']
                except:
                    continue
        except:
            continue
    
    suitability = []
    for circuit, perf in circuit_performance.items():
        if perf['races'] > 0:
            suitability.append({
                'circuit': circuit,
                'races': perf['races'],
                'avgPosition': np.mean(perf['positions']),
                'totalPoints': perf['points'],
                'pointsPerRace': perf['points'] / perf['races']
            })
    
    return pd.DataFrame(suitability).sort_values('avgPosition')
