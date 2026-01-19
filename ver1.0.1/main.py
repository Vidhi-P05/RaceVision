from data_fetcher import (
    fetch_races,
    fetch_qualifying,
    fetch_results,
    fetch_season_standings,
    fetch_constructor_standings,
    fetch_pit_stops
)
from analysis import (
    analyze_qualifying_impact,
    calculate_driver_consistency,
    analyze_team_performance,
    analyze_teammate_performance,
    analyze_pit_stop_performance,
    analyze_track_suitability,
    analyze_constructor_dominance_trend,
    calculate_driver_career_trajectory
)
from ml_models import RaceOutcomePredictor, QualifyingToRacePredictor

# Example analysis functions
def calculate_driver_consistency(year: int):
    """Dummy function for demonstration."""
    # In real code, you would calculate avgPosition, stdPosition
    return fetch_season_standings(year)

def analyze_team_performance(year: int):
    """Dummy function for demonstration."""
    return fetch_constructor_standings(year)

# --------------------------
# Main Program
# --------------------------
if __name__ == "__main__":
    print("RaceVision - Formula 1 Analytics Platform (2015-2025)")
    print("=" * 60)

    year = 2023
    print(f"\n📊 SEASON ANALYSIS FOR {year}")
    print("-" * 60)

    try:
        # Driver standings
        standings = fetch_season_standings(year)
        if not standings.empty:
            print(f"\n✓ Driver Standings ({len(standings)} drivers):")
            print(standings[['driverName', 'position', 'points', 'wins']].head(5))
        else:
            print(f"No driver standings available for {year}.")

        # Races
        races = fetch_races(year)
        if not races.empty:
            print(f"\n✓ Season Races ({len(races)} rounds):")
            print(races[['round', 'raceName', 'circuit']].head(5))
        else:
            print(f"No races available for {year}.")

        # Constructor standings
        con_standings = fetch_constructor_standings(year)
        if not con_standings.empty:
            print(f"\n✓ Constructor Standings ({len(con_standings)} teams):")
            print(con_standings[['constructor', 'position', 'points', 'wins']].head(5))

        # Consistency analysis
        print(f"\n✓ Driver Consistency Metrics:")
        try:
            from analysis import calculate_driver_consistency as calc_consistency
            consistency = calc_consistency(year)
            if not consistency.empty:
                print(consistency[['driver', 'avgPosition', 'stdPosition', 'totalPoints']].head(5))
        except Exception as e:
            print(f"  (Skipped: {e})")

        # Team performance
        print(f"\n✓ Constructor Performance:")
        try:
            from analysis import analyze_team_performance as analyze_team_perf
            team_perf = analyze_team_perf(year)
            if not team_perf.empty:
                print(team_perf[['constructor', 'totalPoints', 'totalWins', 'avgPosition']].head(5))
        except Exception as e:
            print(f"  (Skipped: {e})")

        # Teammate analysis
        print(f"\n✓ Teammate Head-to-Head Performance:")
        try:
            teammates = analyze_teammate_performance(year)
            if not teammates.empty:
                print(teammates[['constructor', 'driver1', 'driver2', 'driver1_points', 'driver2_points']].head(5))
        except Exception as e:
            print(f"  (Skipped: {e})")

        # Qualifying impact
        print(f"\n✓ Qualifying Position Impact on Race Results:")
        try:
            qual_impact = analyze_qualifying_impact(year)
            if not qual_impact.empty:
                print(qual_impact[['race', 'correlation']].head(5))
                avg_corr = qual_impact['correlation'].mean()
                print(f"  Average correlation: {avg_corr:.3f}")
        except Exception as e:
            print(f"  (Skipped: {e})")

        # ML Model training
        print(f"\n🤖 MACHINE LEARNING MODELS")
        print("-" * 60)
        
        try:
            print("\n✓ Training Race Outcome Predictor...")
            predictor = RaceOutcomePredictor(model_type='rf')
            X, y = predictor.prepare_training_data([year-1, year])
            if len(X) > 10:
                predictor.train(X, y)
                metrics = predictor.get_metrics()
                print(f"  Model trained on {len(X)} data points")
                print(f"  MAE: {metrics.get('mae', 'N/A')}")
                print(f"  R² Score: {metrics.get('r2', 'N/A')}")
            else:
                print("  Insufficient data for training")
        except Exception as e:
            print(f"  ✗ Error: {e}")

        print(f"\n✓ Training Qualifying-to-Race Predictor...")
        try:
            qu_pred = QualifyingToRacePredictor()
            X, y = qu_pred.prepare_data([year-1, year])
            if len(X) > 10:
                qu_pred.train(X, y)
                print(f"  Model trained on {len(X)} data points")
            else:
                print("  Insufficient data for training")
        except Exception as e:
            print(f"  ✗ Error: {e}")

        print(f"\n✓ Data successfully loaded for {year}")
        print("\n📈 NEXT STEPS:")
        print("  • Launch interactive dashboard: streamlit run dashboard.py")
        print("  • Explore detailed analysis and visualizations")
        print("  • View ML model predictions and insights")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

