import pandas as pd
import os
import requests
from io import BytesIO

DROPBOX_URL = "https://www.dropbox.com/scl/fi/j9fwky905by6i5qb5mi2w/chicago_crimes_2018_2024.parquet?rlkey=0c06zaptg1e6w7p62nthb0eq8&st=bhwzfw1e&dl=1"
LOCAL_PATH = "./data/chicago_crimes_2015_2025.parquet"




def load_main_dataset():
    print("Téléchargement du fichier Parquet depuis Dropbox...")
    response = requests.get(DROPBOX_URL)
    response.raise_for_status()
    
    print("Lecture du fichier en mémoire avec optimisation...")
    columns_needed = ['date', 'primary_type', 'arrest', 'latitude', 'longitude', 'year']
    
    # Lecture initiale sans dtype (car non supporté par read_parquet)
    df = pd.read_parquet(
        BytesIO(response.content),
        columns=columns_needed
    )
    
    # Optimisations manuelles après chargement
    # 1. Conversion des types pour économiser la mémoire
    if 'primary_type' in df.columns:
        df['primary_type'] = df['primary_type'].astype('str')
    
    if 'arrest' in df.columns:
        # Gestion des différents formats possibles de 'arrest'
        if pd.api.types.is_bool_dtype(df['arrest']):
            pass  # Déjà optimal
        else:
            df['arrest'] = df['arrest'].astype(bool)
    
    if 'latitude' in df.columns:
        df['latitude'] = df['latitude'].astype('float32')
    
    if 'longitude' in df.columns:
        df['longitude'] = df['longitude'].astype('float32')
    
    if 'year' in df.columns:
        df['year'] = df['year'].astype('int16')
    
    # 2. Conversion des dates
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # 3. Nettoyage des données
    df = df.dropna(subset=['date', 'latitude', 'longitude'])
    
    print("Lecture terminée avec optimisations.")
    
    # Calcul de la mémoire utilisée
    mem_bytes = df.memory_usage(deep=True).sum()
    mem_mb = mem_bytes / (1024 ** 2)
    print(f"💾 Taille mémoire du DataFrame : {mem_mb:.2f} MB")
    
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
    df_sampled = df.groupby('year').apply(lambda x: x.sample(n=min(100000, len(x)), random_state=42)).reset_index(drop=True)
    return {
        "bar": prepare_bar_chart_data(df_sampled),
        "line": prepare_line_chart_data(df),
        "map": prepare_map_data(df),
        "sankey": prepare_sankey_data(df_sampled)
    }

def show_total_memory_usage(dataframes: dict):
    total_bytes = sum(
        df.memory_usage(deep=True).sum()
        for df in dataframes.values()
        if isinstance(df, pd.DataFrame)
    )
    total_mb = total_bytes / (1024 ** 2)
    print(f"💾 Mémoire totale utilisée par les DataFrames : {total_mb:.2f} MB")
