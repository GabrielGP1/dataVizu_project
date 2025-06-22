import os
import pandas as pd
import requests
from io import BytesIO
import numpy as np

DROPBOX_URL = "https://www.dropbox.com/scl/fi/j9fwky905by6i5qb5mi2w/chicago_crimes_2018_2024.parquet?rlkey=0c06zaptg1e6w7p62nthb0eq8&st=py05o5tx&dl=1"
LOCAL_FILE = "chicago.parquet"

def load_main_dataset():
    print(" Vérification du fichier local...")
    if os.path.exists(LOCAL_FILE):
        print(f" Chargement local : {LOCAL_FILE}")
        buffer = LOCAL_FILE
    else:
        print(" Téléchargement du fichier Parquet depuis Dropbox...")
        try:
            response = requests.get(DROPBOX_URL, timeout=15)
            response.raise_for_status()
            with open(LOCAL_FILE, "wb") as f:
                f.write(response.content)
            print(f" Fichier téléchargé et sauvegardé localement sous : {LOCAL_FILE}")
            buffer = LOCAL_FILE
        except requests.exceptions.RequestException as e:
            print("❌ Erreur de téléchargement :", e)
            exit(1)

    print("📊 Lecture du fichier en mémoire avec optimisation...")

    columns_needed = ['date', 'primary_type', 'arrest', 'latitude', 'longitude', 'year']
    dtype_mapping = {
        'primary_type': 'category',
        'arrest': 'bool',
        'latitude': 'float32',
        'longitude': 'float32',
        'year': 'int16'
    }

    df = pd.read_parquet(buffer, columns=columns_needed)
    for col, dtype in dtype_mapping.items():
        if col in df.columns:
            df[col] = df[col].astype(dtype)

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date', 'latitude', 'longitude'])

    print(" Lecture terminée avec optimisations.")
    print_memory_usage(df)

    top_crimes = df['primary_type'].value_counts().head(10).index
    df = df[df['primary_type'].isin(top_crimes)]
    df['Crime_Type'] = df['primary_type'].str.title().astype('category')
    return df


def prepare_bar_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['day_of_week'] = df['date'].dt.dayofweek.astype('int8')
    df['Period'] = (df['day_of_week'] >= 5).map({True: 'Weekend', False: 'Weekday'}).astype('category')
    result = df.groupby(['Period', 'Crime_Type']).size().reset_index(name='Count')
    return result

def prepare_map_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["latitude", "longitude", "primary_type", "year"]].copy()
    df = df.dropna()
    return df.sample(n=min(len(df), 30000), random_state=42)

def prepare_sankey_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if df['arrest'].dtype == 'bool':
        df['Resolution'] = df['arrest'].map({True: 'Arrested', False: 'Not Arrested'})
    else:
        df['Resolution'] = pd.to_numeric(df['arrest'], errors='coerce').fillna(0).astype(bool)
        df['Resolution'] = df['Resolution'].map({True: 'Arrested', False: 'Not Arrested'})
    
    df['Resolution'] = df['Resolution'].astype('category')
    return df

def prepare_line_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()    
    df['hour'] = df['date'].dt.hour.astype('int8')
    df['month'] = df['date'].dt.month.astype('int8')
    df['crime_grouped'] = df['Crime_Type'].astype('category')
    return df

def print_memory_usage(df: pd.DataFrame):
    mem_bytes = df.memory_usage(deep=True).sum()
    mem_mb = mem_bytes / (1024 ** 2)
    print(f"💾 Taille mémoire du DataFrame : {mem_mb:.2f} MB")

def preprocess_all():
    df = load_main_dataset()
    data = {
        "bar": prepare_bar_chart_data(df),
        "line": prepare_line_chart_data(df),
        "map": prepare_map_data(df),
        "sankey": prepare_sankey_data(df)
    }
    show_total_memory_usage(data)
    return data

def show_total_memory_usage(dataframes: dict):
    total_bytes = sum(
        df.memory_usage(deep=True).sum()
        for df in dataframes.values()
        if isinstance(df, pd.DataFrame)
    )
    total_mb = total_bytes / (1024 ** 2)
    print(f"💾 Mémoire totale utilisée par les DataFrames : {total_mb:.2f} MB")