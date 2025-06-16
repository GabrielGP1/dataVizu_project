import pandas as pd
import os
import requests

#TODO remplacer les df.copy par le filtrage plus tard.

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
    main_df = pd.read_parquet("./data/chicago_crimes_2015_2025.parquet")
    #main_df = pd.read_csv("../data/Chicago_Crimes_small.csv", parse_dates=["Date"])
    return main_df


def prepare_bar_chart_data(df:pd.DataFrame) -> pd.DataFrame:
    bar_df = df.copy()

    # 1. Convertir la colonne 'date' si ce n'est pas déjà fait
    bar_df['date'] = pd.to_datetime(bar_df['date'], errors='coerce')
    bar_df = bar_df.dropna(subset=['date'])

    # 2. Ajouter la colonne 'DayOfWeek' (0=Monday, 6=Sunday)
    bar_df['day_of_week'] = bar_df['date'].dt.dayofweek

    # 3. Créer la colonne 'Period' : 'Weekday' (0–4) vs 'Weekend' (5–6)
    bar_df['Period'] = bar_df['day_of_week'].apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')

    # 4. Nettoyer/normaliser le nom des crimes
    bar_df['Crime_Type'] = bar_df['primary_type'].str.title()

    # 5. Filtrer les top 10 crimes les plus fréquents pour éviter surcharge visuelle
    top_crimes = bar_df['Crime_Type'].value_counts().head(10).index
    df_filtered = bar_df[bar_df['Crime_Type'].isin(top_crimes)]

    # 6. Grouper pour obtenir le total par type et par période
    bar_df = df_filtered.groupby(['Period', 'Crime_Type']).size().reset_index(name='Count')

    return bar_df



def prepare_map_data(df:pd.DataFrame)-> pd.DataFrame:
    
    #Prépare les données pour la carte interactive. 

    map_df = df.copy()

    # Ne garder que les colonnes nécessaires pour l'affichage de la carte
    columns_to_keep = ["latitude", "longitude", "primary_type", "year"]
    map_df = map_df[columns_to_keep]
    
    #limiter le df
    map_df = map_df.sample(n=min(len(map_df), 30000), random_state=42)

    # Nettoyage de base : suppression des lignes incomplètes
    map_df = map_df.dropna(subset=["latitude", "longitude", "primary_type", "year"])

    return map_df


def prepare_sankey_data(df: pd.DataFrame) -> pd.DataFrame:
    sankey_df = df.copy()

    # Nettoyage des dates (toujours utile pour d'autres visus, mais pas obligatoire ici)
    sankey_df['date'] = pd.to_datetime(sankey_df['date'], errors='coerce')
    sankey_df = sankey_df.dropna(subset=['date'])

    # Standardiser les colonnes
    sankey_df['Crime_Type'] = sankey_df['primary_type'].str.title()

    # Gestion des arrestations
    if sankey_df['arrest'].dtype == 'bool':
        sankey_df['Resolution'] = sankey_df['arrest'].map({True: 'Arrested', False: 'Not Arrested'})
    else:
        sankey_df['Resolution'] = sankey_df['arrest'].map({
            True: 'Arrested', False: 'Not Arrested',
            'true': 'Arrested', 'false': 'Not Arrested',
            'True': 'Arrested', 'False': 'Not Arrested',
            1: 'Arrested', 0: 'Not Arrested'
        })

    sankey_df = sankey_df.dropna(subset=['Crime_Type', 'Resolution'])

    # Filtrer les top 15 crimes pour lisibilité
    top_crimes = sankey_df['Crime_Type'].value_counts().head(15).index
    sankey_df = sankey_df[sankey_df['Crime_Type'].isin(top_crimes)]

    return sankey_df



def prepare_line_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date', 'primary_type', 'year'])

    df['hour'] = df['date'].dt.hour
    df['month'] = df['date'].dt.month

    # Top 10 crimes, reste en "Other"
    top_10 = df['primary_type'].value_counts().nlargest(10).index
    df['crime_grouped'] = df['primary_type'].where(df['primary_type'].isin(top_10), 'Other')

    return df


def preprocess_all():
    
    df = load_main_dataset()
    
    df_dic = {
        "bar":prepare_bar_chart_data (df),
        "line":prepare_line_chart_data(df),
        "map":prepare_map_data(df),
        "sankey":prepare_sankey_data(df)
    }
    return df_dic

