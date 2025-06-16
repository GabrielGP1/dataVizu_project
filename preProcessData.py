import pandas as pd
import numpy as np
import requests
from io import BytesIO

DROPBOX_URL = "https://www.dropbox.com/scl/fi/j9fwky905by6i5qb5mi2w/chicago_crimes_2018_2024.parquet?rlkey=0c06zaptg1e6w7p62nthb0eq8&st=bhwzfw1e&dl=1"

def load_main_dataset():
    print("Téléchargement du fichier Parquet depuis Dropbox...")
    response = requests.get(DROPBOX_URL)
    response.raise_for_status()
    
    print("Lecture du fichier en mémoire avec optimisation...")
    columns_needed = ['date', 'primary_type', 'arrest', 'latitude', 'longitude', 'year']
    
    # Définition des types optimisés pour chaque colonne
    dtype_mapping = {
        'primary_type': 'category',  # Bon pour les variables avec peu de valeurs uniques
        'arrest': 'bool',
        'latitude': 'float32',
        'longitude': 'float32',
        'year': 'int16'
    }
    
    # Lecture avec filtrage précoce et conversion de types
    df = pd.read_parquet(
        BytesIO(response.content),
        columns=columns_needed
    )
    
    # Conversion des types selon le mapping
    for col, dtype in dtype_mapping.items():
        if col in df.columns:
            df[col] = df[col].astype(dtype)
    
    # Conversion des dates et nettoyage
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date', 'latitude', 'longitude'])
    
    print("Lecture terminée avec optimisations.")
    print_memory_usage(df)
    
    return df

def prepare_bar_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    # Création d'une copie pour éviter les modifications sur le DataFrame original
    df = df.copy()
    
    # Conversion des types pour économiser la mémoire
    df['day_of_week'] = df['date'].dt.dayofweek.astype('int8')
    df['Period'] = (df['day_of_week'] >= 5).map({True: 'Weekend', False: 'Weekday'}).astype('category')
    
    # Sélection des top crimes et conversion en category
    top_crimes = df['primary_type'].value_counts().head(10).index
    df = df[df['primary_type'].isin(top_crimes)]
    df['Crime_Type'] = df['primary_type'].str.title().astype('category')
    
    # Groupby avec reset_index() au lieu de as_index=False
    result = df.groupby(['Period', 'Crime_Type']).size().reset_index(name='Count')
    
    return result

def prepare_map_data(df: pd.DataFrame) -> pd.DataFrame:
    # Sélection des colonnes nécessaires avant le sampling
    df = df[["latitude", "longitude", "primary_type", "year"]].copy()
    df = df.dropna()
    return df.sample(n=min(len(df), 30000), random_state=42)

def prepare_sankey_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Utilisation de catégories pour les colonnes textuelles
    df['Crime_Type'] = df['primary_type'].str.title().astype('category')
    
    # Optimisation de la colonne Resolution
    if df['arrest'].dtype == 'bool':
        df['Resolution'] = df['arrest'].map({True: 'Arrested', False: 'Not Arrested'})
    else:
        # Conversion plus robuste pour différents formats
        df['Resolution'] = pd.to_numeric(df['arrest'], errors='coerce').fillna(0).astype(bool)
        df['Resolution'] = df['Resolution'].map({True: 'Arrested', False: 'Not Arrested'})
    
    df['Resolution'] = df['Resolution'].astype('category')
    
    # Filtrage des crimes les plus fréquents
    top_crimes = df['Crime_Type'].value_counts().head(15).index
    return df[df['Crime_Type'].isin(top_crimes)].copy()

def prepare_line_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    # Création d'une copie pour éviter les modifications sur le DataFrame original
    df = df.copy()
    
    # Conversion des colonnes temporelles en types optimisés
    df['hour'] = df['date'].dt.hour.astype('int8')
    df['month'] = df['date'].dt.month.astype('int8')
    
    # Identification des 10 crimes les plus fréquents
    top_10 = df['primary_type'].value_counts().nlargest(10).index
    
    # Création de la colonne grouped en deux étapes
    # 1. Création avec toutes les valeurs
    df['crime_grouped'] = np.where(
        df['primary_type'].isin(top_10),
        df['primary_type'],
        'Other'
    )
    
    # 2. Conversion en category seulement après avoir toutes les valeurs
    df['crime_grouped'] = df['crime_grouped'].astype('category')
    
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