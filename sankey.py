import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.colors as mcolors

def create_sankey(df: pd.DataFrame):
    import plotly.graph_objects as go

    # Étapes : flux entre Crime_Type → Resolution
    flow = df.groupby(['Crime_Type', 'Resolution']).size().reset_index(name='Count')

    crime_types = sorted(df['Crime_Type'].unique())
    resolutions = ['Arrested', 'Not Arrested']

    all_nodes = crime_types + resolutions
    node_dict = {node: i for i, node in enumerate(all_nodes)}

    sources, targets, values, colors = [], [], [], []

    for _, row in flow.iterrows():
        sources.append(node_dict[row['Crime_Type']])
        targets.append(node_dict[row['Resolution']])
        values.append(row['Count'])

        # Liens verts ou rouges selon la résolution
        if row['Resolution'] == 'Arrested':
            colors.append('rgba(46,204,113,0.8)')  # Vert
        else:
            colors.append('rgba(231,76,60,0.8)')   # Rouge

    # Couleur des nœuds : crimes = neutre, résolutions = colorés
    node_colors = ['#1E1E1E'] * len(crime_types) + ['#2ECC71', '#E74C3C']

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors,
            hovertemplate='%{label}<br>Total: %{value}<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors,
            hovertemplate='%{source.label} → %{target.label}<br>Volume: %{value:,}<extra></extra>'
        )
    )])

    fig.update_layout(
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        font=dict(color="white"),
        font_size=12,
        height=800,
        margin=dict(l=50, r=50, t=60, b=40)
    )

    return fig


