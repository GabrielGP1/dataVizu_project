import pandas as pd
import os
import requests

DROPBOX_URL = "https://www.dropbox.com/scl/fi/9mutc67knfn6jpxbze6a3/chicago_crimes_2015_2025.parquet?rlkey=098nh2hbqk0er2ytuxac6ry9y&st=ptnmzd3y&dl=1"
LOCAL_PATH = "./data/chicago_crimes_2015_2025.parquet"

def download_parquet():
    if not os.path.exists(LOCAL_PATH):
        os.makedirs("data", exist_ok=True)
        print("Téléchargement du fichier Parquet...")
        response = requests.get(DROPBOX_URL)
        response.raise_for_status()
        with open(LOCAL_PATH, "wb") as f:
            f.write(response.content)
        print("Téléchargement terminé.")
    else:
        print("Fichier déjà présent localement.")

def load_main_dataset():
    download_parquet()
    df = pd.read_parquet(LOCAL_PATH)
    return df

def prepare_bar_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['day_of_week'] = df['date'].dt.dayofweek
    df['Period'] = df['day_of_week'].apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
    df['Crime_Type'] = df['primary_type'].str.title()
    top_crimes = df['Crime_Type'].value_counts().head(10).index
    df = df[df['Crime_Type'].isin(top_crimes)]
    return df.groupby(['Period', 'Crime_Type']).size().reset_index(name='Count')

def prepare_map_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df[["latitude", "longitude", "primary_type", "year"]]
    df = df.dropna()
    return df.sample(n=min(len(df), 30000), random_state=42)

def prepare_sankey_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['Crime_Type'] = df['primary_type'].str.title()
    if df['arrest'].dtype == 'bool':
        df['Resolution'] = df['arrest'].map({True: 'Arrested', False: 'Not Arrested'})
    else:
        df['Resolution'] = df['arrest'].map({
            True: 'Arrested', False: 'Not Arrested',
            'true': 'Arrested', 'false': 'Not Arrested',
            'True': 'Arrested', 'False': 'Not Arrested',
            1: 'Arrested', 0: 'Not Arrested'
        })
    df = df.dropna(subset=['Crime_Type', 'Resolution'])
    top_crimes = df['Crime_Type'].value_counts().head(15).index
    return df[df['Crime_Type'].isin(top_crimes)]

def prepare_line_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date', 'primary_type', 'year'])
    df['hour'] = df['date'].dt.hour
    df['month'] = df['date'].dt.month
    top_10 = df['primary_type'].value_counts().nlargest(10).index
    df['crime_grouped'] = df['primary_type'].where(df['primary_type'].isin(top_10), 'Other')
    return df

def preprocess_all():
    df = load_main_dataset()
    return {
        "bar": prepare_bar_chart_data(df),
        "line": prepare_line_chart_data(df),
        "map": prepare_map_data(df),
        "sankey": prepare_sankey_data(df)
    }
