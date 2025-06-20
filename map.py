import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import DBSCAN
import numpy as np


def create_map(df: pd.DataFrame, selected_year: int = None, selected_crimes: list = None):
    # Normalize crime labels
    df['primary_type'] = df['primary_type'].astype(str).str.title()

    # Default year
    if selected_year is None:
        selected_year = df['year'].max()

    # Filter by year
    year_df = df[df['year'] == selected_year].copy()

    # Base map layout
    def base_map(title=""):
        fig = go.Figure()
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                center={"lat": 41.8781, "lon": -87.6298},
                zoom=10
            ),
            height=900,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            legend_title="Crime Type",
            title=title
        )
        return fig

    # No selection
    if not selected_crimes:
        return px.scatter_mapbox(
            pd.DataFrame(columns=["latitude", "longitude", "primary_type"]),
            lat="latitude",
            lon="longitude",
            mapbox_style="carto-positron",
            zoom=9,
            center={"lat": 41.8781, "lon": -87.6298}
        ).update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=900,
            legend_title="Crime Type"
        )

    
    # Filter by selected crimes
    filtered = year_df[year_df['primary_type'].isin(selected_crimes)].copy()
    if filtered.empty:
        return px.scatter_mapbox(
            pd.DataFrame(columns=["latitude", "longitude", "primary_type"]),
            lat="latitude",
            lon="longitude",
            mapbox_style="carto-positron",
            zoom=9,
            center={"lat": 41.8781, "lon": -87.6298}
        ).update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=900,
            legend_title="Crime Type"
        )

    # Generate clustered markers per crime
    traces = []
    for crime in selected_crimes:
        crime_df = filtered[filtered['primary_type'] == crime].copy()

        if crime_df.empty:
            continue

        coords = crime_df[['latitude', 'longitude']]
        clustering = DBSCAN(eps=0.007, min_samples=2).fit(coords)
        crime_df['cluster'] = clustering.labels_
        crime_df = crime_df[crime_df['cluster'] != -1]

        if crime_df.empty:
            continue

        grouped = crime_df.groupby('cluster').agg({
            'latitude': 'mean',
            'longitude': 'mean',
            'primary_type': 'count'
        }).rename(columns={'primary_type': 'count'}).reset_index()

        total = grouped['count'].sum()
        grouped['percentage'] = grouped['count'] / total * 100
        grouped['label'] = grouped.apply(
            lambda row: f"<b>{crime}</b> ({row['percentage']:.1f}%)", axis=1
        )

        traces.append(go.Scattermapbox(
            lat=grouped['latitude'],
            lon=grouped['longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=grouped['count'] * 40.0,  # Big and clear
                sizemode='area',
                opacity=0.7
            ),
            text=grouped.apply(lambda row: f"{row['label']}<br>Count={row['count']}", axis=1),
            name=crime,
            hovertemplate="%{text}<extra></extra>",
            hoverlabel=dict(
                font_size=20,  
                font_family="Arial",

            )
        ))

    # Final map with all traces
    fig = go.Figure(data=traces)
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center={"lat": 41.8781, "lon": -87.6298},
            zoom=10
        ),
        height=900,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend_title="Crime Type"
    )

    return fig
