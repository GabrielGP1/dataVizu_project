# map.py

import plotly.express as px
import pandas as pd

def create_map(df: pd.DataFrame, selected_year: int = None, selected_crimes: list = None):
    """
    Crée une carte interactive Mapbox basée sur les crimes à Chicago.
    :param df: DataFrame prétraité avec uniquement les colonnes latitude, longitude, primary_type, year
    :param selected_year: année sélectionnée
    :param selected_crimes: liste des types de crime sélectionnés
    """

    #df = df.copy()

    # Standardisation du nom des crimes
    df['primary_type'] = df['primary_type'].astype(str).str.title()

    # Défaut : année 2022
    if selected_year is None:
        selected_year = df['year'].max()

    # Défaut : top 5 des crimes
    # Si aucun type de crime n'est sélectionné, afficher un message vide
    if selected_crimes is None or len(selected_crimes) == 0:
        return px.scatter_mapbox(
            pd.DataFrame(columns=["latitude", "longitude", "primary_type"]),
            lat="latitude",
            lon="longitude",
            mapbox_style="carto-positron",
            zoom=9,
            center={"lat": 41.8781, "lon": -87.6298}
        ).update_layout(
            title="No data available for the selected filters.",
            margin={"r": 0, "t": 30, "l": 0, "b": 0}
    )


    # Filtrage selon année et types de crimes
    filtered = df[
        (df['year'] == selected_year) &
        (df['primary_type'].isin(selected_crimes))
    ]

    # Si aucune donnée
    if filtered.empty:
        return px.scatter_mapbox(
            pd.DataFrame(columns=["latitude", "longitude"]),
            lat="latitude",
            lon="longitude",
            mapbox_style="carto-positron",
            zoom=9,
            center={"lat": 41.8781, "lon": -87.6298}
        ).update_layout(title="No data available for the selected filters.")

    # Échantillonnage intelligent pour performance (jusqu'à 3000 points)
    sample_size = min(len(filtered), 3000)
    sampled = filtered.sample(n=sample_size, random_state=42)

    # Création de la carte
    fig = px.scatter_mapbox(
        sampled,
        lat="latitude",
        lon="longitude",
        color="primary_type",
        mapbox_style="carto-positron",
        zoom=9,
        center={"lat": 41.8781, "lon": -87.6298},
        height=700,
        hover_data={
        "primary_type": True,         # Keep the data
        "latitude": False,            # We'll add it manually
        "longitude": False            # We'll add it manually
    }
)

    # Set the label manually in hovertemplate
    fig.update_traces(
        hovertemplate=(
            "<b>Crime Type:</b> %{customdata[0]}<br>" +
            "<b>Latitude:</b> %{lat:.5f}<br>" +
            "<b>Longitude:</b> %{lon:.5f}<extra></extra>"
        ),
        customdata=sampled[["primary_type"]]
    )

        # Layout update (cleaned)
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center={"lat": 41.8781, "lon": -87.6298},
            zoom=9,
        ),
        uirevision=False,  # Force reset on update
        legend_title_text="Crime Type",
        showlegend=True,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )


    return fig
