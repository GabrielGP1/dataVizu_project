import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import DBSCAN
import numpy as np

import legend


def create_map(df: pd.DataFrame, selected_year: int = None, selected_crimes: list = None):
    df['primary_type'] = df['primary_type'].astype(str).apply(legend.format_proper_name)
    if selected_year is None:
        selected_year = df['year'].max()
    year_df = df[df['year'] == selected_year].copy()

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
            legend_title="Crime Types",
            plot_bgcolor='#111111',
            paper_bgcolor='#111111',
            font=dict(color='white', family='Arial')
        )

    selected_crimes = [legend.format_proper_name(crime) for crime in selected_crimes]
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
            legend_title="Crime Types",
            plot_bgcolor='#111111',
            paper_bgcolor='#111111',
            font=dict(color='white', family='Arial')
        )

    crime_counts = filtered['primary_type'].value_counts().reset_index()
    crime_counts.columns = ['crime_type', 'count']
    top_5_crimes = crime_counts.nlargest(5, 'count')['crime_type'].tolist()

    traces = []
    for crime in selected_crimes:
        crime_df = filtered[filtered['primary_type'] == crime].copy()

        if crime_df.empty:
            continue

        coords = crime_df[['latitude', 'longitude']]
        clustering = DBSCAN(eps=0.013, min_samples=1).fit(coords)
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
        grouped['label'] = crime
        grouped['latitude'] += np.random.uniform(-0.0005, 0.0005, size=len(grouped))
        grouped['longitude'] += np.random.uniform(-0.0005, 0.0005, size=len(grouped))

        marker_color = legend.CUSTOM_COLORS.get(crime, px.colors.qualitative.Bold[len(traces) % len(px.colors.qualitative.Bold)])
        
        visible = True if crime in top_5_crimes else 'legendonly'
        
        traces.append(go.Scattermapbox(
            lat=grouped['latitude'],
            lon=grouped['longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size = np.sqrt(grouped['count']) * 120,
                sizemode='area',
                opacity=0.7,
                color=marker_color
            ),
            text=grouped.apply(
                lambda row: f"<b>{row['label']}</b><br>Count: {row['count']:,}<br>Percentage: {row['percentage']:.1f}%", 
                axis=1
            ),
            name=crime,
            hovertemplate="%{text}<extra></extra>",
            hoverlabel=legend.COMMON_HOVER_CONFIG['hoverlabel'],
            visible=visible
        ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center={"lat": 41.8781, "lon": -87.6298},
            zoom=10
        ),
        height= 900,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend_title="Crime Types",
        plot_bgcolor='#111111',
        paper_bgcolor='#111111',
        font=dict(color='white', family='Arial'),
        title={
            'text': f"Crime Distribution - {selected_year}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        }
    )

    return fig
