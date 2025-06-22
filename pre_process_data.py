# -*- coding: utf-8 -*-
"""
pre_processing_data.py

Ce module télécharge, nettoie et prépare un jeu de données sur les crimes à Chicago
(2018–2024) pour l’analyse visuelle via des graphiques en barres, cartes, diagrammes
de Sankey et lignes temporelles.

Auteur : Team 13
Date : 2025-06-22
"""

import os
import pandas as pd
import requests
from io import BytesIO
import numpy as np

DROPBOX_URL = "https://www.dropbox.com/scl/fi/j9fwky905by6i5qb5mi2w/chicago_crimes_2018_2024.parquet?rlkey=0c06zaptg1e6w7p62nthb0eq8&st=py05o5tx&dl=1"
LOCAL_FILE = "chicago.parquet"

def load_main_dataset() -> pd.DataFrame:
    """
    Télécharge ou charge localement le jeu de données sur les crimes à Chicago.
    Effectue un nettoyage, des conversions de types et filtre les 10 crimes les plus fréquents.

    Returns:
        pd.DataFrame: Le DataFrame nettoyé et préparé.
    """
    if os.path.exists(LOCAL_FILE):
        buffer = LOCAL_FILE
    else:
        try:
            response = requests.get(DROPBOX_URL, timeout=15)
            response.raise_for_status()
            with open(LOCAL_FILE, "wb") as f:
                f.write(response.content)
            buffer = LOCAL_FILE
        except requests.exceptions.RequestException as e:
            exit(1)

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
    top_crimes = df['primary_type'].value_counts().head(10).index
    df = df[df['primary_type'].isin(top_crimes)]
    df['Crime_Type'] = df['primary_type'].str.title().astype('category')
    return df


def prepare_bar_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les données pour un graphique en barres comparant les crimes en semaine vs fin de semaine.

    Args:
        df (pd.DataFrame): Le DataFrame de base.

    Returns:
        pd.DataFrame: Données groupées par période (Weekday/Weekend) et type de crime.
    """
    df = df.copy()
    df['day_of_week'] = df['date'].dt.dayofweek.astype('int8')
    df['Period'] = (df['day_of_week'] >= 5).map({True: 'Weekend', False: 'Weekday'}).astype('category')
    result = df.groupby(['Period', 'Crime_Type']).size().reset_index(name='Count')
    return result


def prepare_map_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare un sous-échantillon des données géographiques pour une carte.

    Args:
        df (pd.DataFrame): Le DataFrame de base.

    Returns:
        pd.DataFrame: Échantillon aléatoire de coordonnées avec type de crime et année.
    """
    df = df[["latitude", "longitude", "primary_type", "year"]].copy()
    df = df.dropna()
    return df.sample(n=min(len(df), 30000), random_state=42)


def prepare_sankey_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les données pour un diagramme de Sankey entre types de crime et résolution (arrestation ou non).

    Args:
        df (pd.DataFrame): Le DataFrame de base.

    Returns:
        pd.DataFrame: Données enrichies avec la colonne 'Resolution'.
    """
    df = df.copy()
    if df['arrest'].dtype == 'bool':
        df['Resolution'] = df['arrest'].map({True: 'Arrested', False: 'Not Arrested'})
    else:
        df['Resolution'] = pd.to_numeric(df['arrest'], errors='coerce').fillna(0).astype(bool)
        df['Resolution'] = df['Resolution'].map({True: 'Arrested', False: 'Not Arrested'})
    
    df['Resolution'] = df['Resolution'].astype('category')
    return df


def prepare_line_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les données pour un graphique linéaire par heure et mois.

    Args:
        df (pd.DataFrame): Le DataFrame de base.

    Returns:
        pd.DataFrame: Données avec colonnes supplémentaires pour heure, mois et type de crime.
    """
    df = df.copy()    
    df['hour'] = df['date'].dt.hour.astype('int8')
    df['month'] = df['date'].dt.month.astype('int8')
    df['crime_grouped'] = df['Crime_Type'].astype('category')
    return df


def preprocess_all() -> dict:
    """
    Charge et prépare l'ensemble des données pour les différents types de visualisations.

    Returns:
        dict: Dictionnaire contenant les DataFrames préparés pour bar, map, sankey et line.
    """
    df = load_main_dataset()
    data = {
        "bar": prepare_bar_chart_data(df),
        "line": prepare_line_chart_data(df),
        "map": prepare_map_data(df),
        "sankey": prepare_sankey_data(df)
    }
    return data
