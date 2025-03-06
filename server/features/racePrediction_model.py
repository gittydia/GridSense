import fastf1
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import tempfile
import os
import atexit

# Create a temporary directory for caching
temp_cache_dir = tempfile.mkdtemp()
print(f"Using temporary cache directory: {temp_cache_dir}")

# Enable FastF1 cache
fastf1.Cache.enable_cache(temp_cache_dir)

# Ensure the temporary directory is cleaned up when the script exits
def cleanup_temp_dir():
    print(f"Cleaning up temporary cache directory: {temp_cache_dir}")
    for root, dirs, files in os.walk(temp_cache_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(temp_cache_dir)

atexit.register(cleanup_temp_dir)

def collect_historical_data(years=range(2021, 2024)):
    all_race_data = []
    
    for year in years:
        # Load all races for the year
        calendar = fastf1.get_event_schedule(year)
        for _, race in calendar.iterrows():
            try:
                session = fastf1.get_session(year, race['RoundNumber'], 'R')
                session.load()
                results = session.results
                
                for _, driver in results.iterrows():
                    all_race_data.append({
                        'season': year,
                        'round': race['RoundNumber'],
                        'driver': driver['Driver'],
                        'team': driver['Team'],
                        'grid': driver['GridPosition'],
                        'position': driver['Position'],
                        # Add winner flag (1 if position is 1, else 0)
                        'winner': 1 if driver['Position'] == 1 else 0
                    })
            except Exception as e:
                print(f"Error loading {year} round {race['RoundNumber']}: {e}")
                continue
    
    return pd.DataFrame(all_race_data)

def train_model():
    # Collect historical data
    print("Collecting historical data...")
    df = collect_historical_data()
    
    # Prepare features
    print("Preparing features...")
    X = pd.get_dummies(df.drop(['winner', 'position'], axis=1), columns=['driver', 'team'])
    y = df['winner']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    print("Training model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save the model
    print("Saving model...")
    with open("trained_model.pkl", "wb") as f:
        pickle.dump(model, f)
    
    # Print model accuracy
    print(f"Model accuracy: {model.score(X_test, y_test):.2f}")

if __name__ == "__main__":
    train_model()