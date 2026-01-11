import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
from data_fetcher import fetch_results, fetch_qualifying, fetch_races

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

class RaceOutcomePredictor:
    """Predict finishing positions using grid position and driver/constructor characteristics."""
    
    def __init__(self, model_type='rf'):
        """
        Initialize predictor with specified model type.
        
        Args:
            model_type: 'rf' (RandomForest), 'xgb' (XGBoost), 'cb' (CatBoost)
        """
        self.model_type = model_type
        self.le_driver = LabelEncoder()
        self.le_constructor = LabelEncoder()
        self.is_trained = False
        
        if model_type == 'xgb' and XGBOOST_AVAILABLE:
            self.model = xgb.XGBRegressor(n_estimators=100, max_depth=6, random_state=42)
        elif model_type == 'cb' and CATBOOST_AVAILABLE:
            self.model = cb.CatBoostRegressor(iterations=100, verbose=False, random_state=42)
        else:
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    def prepare_training_data(self, years: list) -> tuple:
        """Prepare training data from multiple seasons."""
        X_data = []
        y_data = []
        
        for year in years:
            try:
                races = fetch_races(year)
                for _, race in races.iterrows():
                    try:
                        qual = fetch_qualifying(year, int(race['round']))
                        results = fetch_results(year, int(race['round']))
                        
                        if qual.empty or results.empty:
                            continue
                        
                        merged = qual.merge(
                            results[['driverId', 'position', 'constructor']], 
                            on='driverId', 
                            suffixes=('_qual', '_race')
                        )
                        merged = merged[merged['position_race'].notna()]
                        
                        for _, row in merged.iterrows():
                            if pd.notna(row['position_race']) and pd.notna(row['position']):
                                X_data.append({
                                    'grid_position': row['position'],
                                    'driver': row['driverId'],
                                    'constructor': row['constructor']
                                })
                                y_data.append(row['position_race'])
                    except:
                        continue
            except:
                continue
        
        return pd.DataFrame(X_data), np.array(y_data)
    
    def train(self, X, y):
        """Train the prediction model."""
        X_encoded = X.copy()
        X_encoded['driver'] = self.le_driver.fit_transform(X['driver'])
        X_encoded['constructor'] = self.le_constructor.fit_transform(X['constructor'])
        
        self.model.fit(X_encoded, y)
        self.is_trained = True
        
        # Calculate and store evaluation metrics
        y_pred = self.model.predict(X_encoded)
        self.mae = mean_absolute_error(y, y_pred)
        self.r2 = r2_score(y, y_pred)
    
    def predict(self, grid_position: int, driver: str, constructor: str) -> float:
        """Predict race finish position."""
        if not self.is_trained:
            return None
        
        try:
            X_new = pd.DataFrame({
                'grid_position': [grid_position],
                'driver': [self.le_driver.transform([driver])[0]],
                'constructor': [self.le_constructor.transform([constructor])[0]]
            })
            prediction = self.model.predict(X_new)[0]
            return max(1.0, min(prediction, 20.0))
        except:
            return None
    
    def get_feature_importance(self) -> dict:
        """Get feature importance scores (XGBoost/CatBoost only)."""
        if not self.is_trained or self.model_type == 'rf':
            return {}
        
        try:
            features = ['grid_position', 'driver', 'constructor']
            importances = self.model.feature_importances_
            return {feat: imp for feat, imp in zip(features, importances)}
        except:
            return {}
    
    def get_metrics(self) -> dict:
        """Get model evaluation metrics."""
        if not self.is_trained:
            return {}
        
        return {
            'mae': getattr(self, 'mae', None),
            'r2': getattr(self, 'r2', None),
            'model_type': self.model_type
        }

class QualifyingToRacePredictor:
    """Predict position change from qualifying to race finish."""
    
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False
    
    def prepare_data(self, years: list) -> tuple:
        """Prepare data showing qualifying to race performance change."""
        X_data = []
        y_data = []
        
        for year in years:
            try:
                races = fetch_races(year)
                for _, race in races.iterrows():
                    try:
                        qual = fetch_qualifying(year, int(race['round']))
                        results = fetch_results(year, int(race['round']))
                        
                        if qual.empty or results.empty:
                            continue
                        
                        merged = qual.merge(
                            results[['driverId', 'position']], 
                            on='driverId',
                            suffixes=('_qual', '_race')
                        )
                        
                        for _, row in merged.iterrows():
                            if pd.notna(row['position_race']):
                                X_data.append([row['position']])
                                y_data.append(row['position_race'] - row['position'])
                    except:
                        continue
            except:
                continue
        
        return np.array(X_data), np.array(y_data)
    
    def train(self, X, y):
        """Train the predictor."""
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict(self, qualifying_position: int) -> float:
        """Predict position change from qualifying."""
        if not self.is_trained:
            return 0
        
        return float(self.model.predict([[qualifying_position]])[0])
