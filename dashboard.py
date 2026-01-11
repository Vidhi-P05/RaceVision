import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data_fetcher import (
    fetch_races, fetch_season_standings, fetch_constructor_standings, 
    fetch_results, fetch_qualifying, fetch_pit_stops
)
from analysis import (
    analyze_qualifying_impact, calculate_driver_consistency, analyze_team_performance,
    analyze_teammate_performance, analyze_pit_stop_performance, analyze_track_suitability,
    calculate_driver_career_trajectory, analyze_constructor_dominance_trend
)
from ml_models import RaceOutcomePredictor, QualifyingToRacePredictor

st.set_page_config(page_title="RaceVision", layout="wide", initial_sidebar_state="expanded")
st.title("🏎️ RaceVision: Formula 1 Analytics & Prediction Platform (2015-2025)")

menu = st.sidebar.radio(
    "Select Section",
    ["Home", "Season Analysis", "Driver Insights", "Constructor Analysis", "Predictions", "Visualizations", "Career Tracker"]
)

if menu == "Home":
    st.markdown("""
    # Welcome to RaceVision
    
    An end-to-end Formula 1 analytics platform combining **Data Analysis**, **Data Science**, and **Machine Learning**.
    
    ## Platform Capabilities
    
    ### 📊 **Data Analysis (DA)**
    - Season-level championship analysis (2015-2025)
    - Driver career trajectory tracking
    - Interactive dashboards for race storytelling
    
    ### 🔬 **Data Science (DS)**
    - Qualifying position vs. race finish analysis
    - Driver consistency and reliability metrics
    - Constructor dominance trends
    - Teammate head-to-head comparisons
    - Pit stop performance evaluation
    - Circuit suitability analysis
    
    ### 🤖 **Machine Learning (AI/ML)**
    - Race outcome prediction models
    - Qualifying-to-race performance prediction
    - Feature importance and interpretability
    - Multi-model support (RandomForest, XGBoost, CatBoost)
    
    ## How to Use
    
    Select a section from the sidebar to explore different analyses and predictions.
    """)

elif menu == "Season Analysis":
    st.header("📈 Season Analysis")
    col_year, col_info = st.columns([1, 3])
    
    with col_year:
        year = st.slider("Select Season", 2015, 2025, 2023, key="season_year")
    
    with col_info:
        st.info(f"Analyzing F1 Season {year}")
    
    try:
        standings = fetch_season_standings(year)
        con_standings = fetch_constructor_standings(year)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Drivers", len(standings))
        with col2:
            st.metric("Constructors", len(con_standings))
        with col3:
            races = fetch_races(year)
            st.metric("Races", len(races))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top 10 Drivers")
            st.dataframe(standings[['driverName', 'position', 'points', 'wins']].head(10), use_container_width=True)
        
        with col2:
            st.subheader("Constructor Standings")
            st.dataframe(con_standings[['constructor', 'position', 'points', 'wins']].head(10), use_container_width=True)
        
        # Points distribution chart
        st.subheader("Driver Points Distribution")
        fig = px.bar(standings.head(15), x='driverName', y='points', 
                     title=f"Top 15 Drivers - {year}",
                     labels={'driverName': 'Driver', 'points': 'Points'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Constructor points chart
        st.subheader("Constructor Points Distribution")
        fig = px.bar(con_standings, x='constructor', y='points',
                     title=f"Constructor Points - {year}",
                     labels={'constructor': 'Constructor', 'points': 'Points'})
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Could not load season data: {e}")

elif menu == "Driver Insights":
    st.header("👤 Driver Insights")
    col_year, col_metric = st.columns(2)
    
    with col_year:
        year = st.slider("Select Season", 2015, 2025, 2023, key="driver_year")
    
    with col_metric:
        metric_type = st.radio("Analysis Type", ["Consistency", "Performance"])
    
    try:
        consistency = calculate_driver_consistency(year)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Most Consistent Drivers")
            top_consistent = consistency[['driver', 'races_completed', 'avgPosition', 'stdPosition', 'totalPoints']].head(10)
            st.dataframe(top_consistent, use_container_width=True)
        
        with col2:
            st.subheader("Key Metrics")
            fig = px.scatter(consistency, x='avgPosition', y='stdPosition', 
                            size='totalPoints', hover_data=['driver'],
                            title="Driver Consistency vs Average Position",
                            labels={'avgPosition': 'Avg Finish Position', 'stdPosition': 'Position Std Dev'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Podium analysis
        st.subheader("Podium Performance")
        podium_data = consistency[consistency['podiums'] > 0].sort_values('podiums', ascending=False).head(10)
        if not podium_data.empty:
            fig = px.bar(podium_data, x='driver', y='podiums',
                        title="Top 10 Drivers by Podium Finishes")
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Could not generate driver analysis: {e}")

elif menu == "Constructor Analysis":
    st.header("🏭 Constructor Analysis")
    col_year, col_view = st.columns(2)
    
    with col_year:
        year = st.slider("Select Season", 2015, 2025, 2023, key="team_year")
    
    with col_view:
        view_type = st.radio("View Type", ["Single Season", "Multi-Season Trend"])
    
    try:
        if view_type == "Single Season":
            team_perf = analyze_team_performance(year)
            st.subheader(f"Constructor Performance - {year}")
            st.dataframe(team_perf, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(team_perf, x='constructor', y='totalPoints',
                            title="Constructor Points",
                            labels={'totalPoints': 'Points', 'constructor': 'Constructor'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(team_perf, x='constructor', y='totalWins',
                            title="Constructor Wins",
                            labels={'totalWins': 'Wins', 'constructor': 'Constructor'})
                st.plotly_chart(fig, use_container_width=True)
        
        else:  # Multi-season trend
            start_year = st.slider("Start Year", 2015, 2024, 2020, key="trend_start")
            end_year = st.slider("End Year", 2015, 2025, 2024, key="trend_end")
            
            if start_year < end_year:
                dominance = analyze_constructor_dominance_trend(start_year, end_year)
                
                if not dominance.empty:
                    # Top constructors
                    top_constructors = dominance.groupby('constructor')['points'].sum().nlargest(5).index.tolist()
                    
                    filtered_data = dominance[dominance['constructor'].isin(top_constructors)]
                    
                    fig = px.line(filtered_data, x='year', y='points', color='constructor',
                                 title=f"Constructor Points Trend ({start_year}-{end_year})")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Start year must be before end year")
    
    except Exception as e:
        st.error(f"Could not generate constructor analysis: {e}")

elif menu == "Predictions":
    st.header("🔮 Predictive Models")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Race Outcome Prediction")
        try:
            pred_year = st.slider("Training Data Year", 2015, 2024, 2023, key="pred_year")
            
            races = fetch_races(pred_year)
            if not races.empty:
                race_names = races['raceName'].tolist()
                selected_race = st.selectbox("Select a race", race_names, key="race_select")
                
                race_data = races[races['raceName'] == selected_race].iloc[0]
                qual = fetch_qualifying(pred_year, int(race_data['round']))
                
                if not qual.empty:
                    driver_options = qual['driverName'].tolist()
                    selected_driver = st.selectbox("Select driver", driver_options, key="driver_select")
                    driver_data = qual[qual['driverName'] == selected_driver].iloc[0]
                    
                    grid_pos = int(driver_data['position'])
                    constructor = driver_data['constructor']
                    driver_id = driver_data['driverId']
                    
                    col_model = st.columns(1)
                    with col_model[0]:
                        model_type = st.radio("Model Type", ["Random Forest", "XGBoost", "CatBoost"], key="model_select")
                        model_map = {"Random Forest": "rf", "XGBoost": "xgb", "CatBoost": "cb"}
                    
                    if st.button("Predict Finish Position", key="predict_btn"):
                        try:
                            predictor = RaceOutcomePredictor(model_type=model_map[model_type])
                            X, y = predictor.prepare_training_data([pred_year-2, pred_year-1, pred_year])
                            if len(X) > 10:
                                predictor.train(X, y)
                                prediction = predictor.predict(grid_pos, driver_id, constructor)
                                if prediction:
                                    st.success(f"**Predicted finish position: {prediction:.1f}**")
                                    metrics = predictor.get_metrics()
                                    st.info(f"Model MAE: {metrics.get('mae', 'N/A'):.2f} | R²: {metrics.get('r2', 'N/A'):.3f}")
                            else:
                                st.warning("Insufficient training data")
                        except Exception as e:
                            st.error(f"Prediction failed: {e}")
        except Exception as e:
            st.error(f"Could not load race data: {e}")
    
    with col2:
        st.subheader("Qualifying-to-Race Analysis")
        try:
            qu_pred_year = st.slider("Analysis Year", 2015, 2024, 2023, key="qu_pred_year")
            
            qu_pred = QualifyingToRacePredictor()
            X, y = qu_pred.prepare_data([qu_pred_year-1, qu_pred_year])
            if len(X) > 10:
                qu_pred.train(X, y)
                
                grid_input = st.number_input("Grid Position", 1, 20, 5, key="grid_input")
                position_change = qu_pred.predict(grid_input)
                
                if position_change is not None:
                    st.metric("Expected Position Change", f"{position_change:.2f}")
                    st.caption("Positive = dropped positions | Negative = gained positions")
            else:
                st.warning("Insufficient data for training")
        except Exception as e:
            st.error(f"Could not generate qualifying analysis: {e}")

elif menu == "Visualizations":
    st.header("📊 Interactive Visualizations")
    
    viz_year = st.slider("Select Season", 2015, 2025, 2023, key="viz_year")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Qualifying Impact on Race Results")
        try:
            impact = analyze_qualifying_impact(viz_year)
            if not impact.empty:
                fig = px.bar(impact, x='race', y='correlation',
                            title=f"Qualifying Position Correlation with Race Finish",
                            labels={'correlation': 'Correlation Coefficient'})
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                avg_corr = impact['correlation'].mean()
                st.info(f"Average correlation: {avg_corr:.3f}")
        except Exception as e:
            st.info(f"Qualifying analysis not available: {e}")
    
    with col2:
        st.subheader("Pit Stop Performance")
        try:
            pit_data = analyze_pit_stop_performance(viz_year)
            if not pit_data.empty:
                fig = px.bar(pit_data.head(10), x='driver', y='avg_stop_duration',
                            title="Average Pit Stop Duration (Top 10)",
                            labels={'avg_stop_duration': 'Avg Duration (s)', 'driver': 'Driver'})
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info(f"Pit stop data not available: {e}")
    
    # Teammate comparison
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Teammate Head-to-Head")
        try:
            teammates = analyze_teammate_performance(viz_year)
            if not teammates.empty:
                fig = go.Figure(data=[
                    go.Bar(name='Driver 1', x=teammates['constructor'], y=teammates['driver1_points']),
                    go.Bar(name='Driver 2', x=teammates['constructor'], y=teammates['driver2_points'])
                ])
                fig.update_layout(title="Teammate Points Comparison", barmode='group')
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info(f"Teammate data not available: {e}")
    
    with col4:
        st.subheader("Season Points Distribution")
        try:
            standings = fetch_season_standings(viz_year)
            if not standings.empty:
                fig = px.pie(standings.head(10), values='points', names='driverName',
                            title=f"Top 10 Drivers Points Distribution")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not generate points distribution: {e}")

elif menu == "Career Tracker":
    st.header("📈 Driver Career Trajectory")
    
    try:
        all_drivers = fetch_season_standings(2023)
        if not all_drivers.empty:
            driver_options = all_drivers['driverId'].unique().tolist()
            selected_driver_id = st.selectbox("Select Driver", driver_options, 
                                             format_func=lambda x: all_drivers[all_drivers['driverId']==x]['driverName'].values[0] if len(all_drivers[all_drivers['driverId']==x]) > 0 else x)
            
            col_years = st.columns(2)
            with col_years[0]:
                start_year = st.slider("Start Year", 2015, 2024, 2020, key="career_start")
            with col_years[1]:
                end_year = st.slider("End Year", 2015, 2025, 2023, key="career_end")
            
            if start_year < end_year:
                trajectory = calculate_driver_career_trajectory(start_year, end_year, selected_driver_id)
                
                if not trajectory.empty:
                    st.subheader(f"Career Statistics: {trajectory.iloc[0].get('constructor', 'Unknown')}")
                    
                    col_stats = st.columns(4)
                    with col_stats[0]:
                        st.metric("Seasons", len(trajectory))
                    with col_stats[1]:
                        st.metric("Best Position", int(trajectory['position'].min()))
                    with col_stats[2]:
                        st.metric("Total Wins", int(trajectory['wins'].sum()))
                    with col_stats[3]:
                        st.metric("Total Points", int(trajectory['points'].sum()))
                    
                    # Career trajectory chart
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=trajectory['year'], y=trajectory['position'],
                                            mode='lines+markers', name='Championship Position',
                                            line=dict(color='red')))
                    fig.update_layout(title="Championship Position Over Years",
                                     xaxis_title="Year", yaxis_title="Position",
                                     yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Points trend
                    fig = px.bar(trajectory, x='year', y='points',
                                title="Season Points Progression")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Career table
                    st.subheader("Detailed Career Statistics")
                    st.dataframe(trajectory, use_container_width=True)
                else:
                    st.info("No data available for this driver in the selected period")
    except Exception as e:
        st.error(f"Could not load career data: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Source")
st.sidebar.info("Data: [Ergast API](https://ergast.com/mrd/) - Formula 1 Historical Data (1950-2025)")
st.sidebar.markdown("### 📚 About RaceVision")
st.sidebar.write("RaceVision is a comprehensive F1 analytics platform combining DA, DS, and ML to provide insights into F1 performance.")
