import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.colors as mcolors

def create_sankey(df: pd.DataFrame):
    import plotly.graph_objects as go

    # 1. Nettoyage et validation des données
    df = df.copy()
    if not {'Crime_Type', 'Resolution'}.issubset(df.columns):
        raise ValueError("DataFrame must contain 'Crime_Type' and 'Resolution' columns")
    
    # 2. Préparation des nœuds de manière exhaustive
    crime_types = df['Crime_Type'].unique().tolist()
    resolutions = ['Arrested', 'Not Arrested']  # On force ces deux valeurs
    
    # Vérification que toutes les résolutions existent
    actual_resolutions = df['Resolution'].unique().tolist()
    for res in ['Arrested', 'Not Arrested']:
        if res not in actual_resolutions:
            print(f"Warning: Resolution '{res}' not found in data")

    all_nodes = crime_types + resolutions
    node_dict = {node: i for i, node in enumerate(all_nodes)}

    # 3. Calcul des flux avec vérification
    flow = df.groupby(['Crime_Type', 'Resolution']).size().reset_index(name='Count')
    
    sources, targets, values, colors = [], [], [], []
    
    for _, row in flow.iterrows():
        try:
            sources.append(node_dict[row['Crime_Type']])
            targets.append(node_dict[row['Resolution']])
            values.append(row['Count'])
            
            if row['Resolution'] == 'Arrested':
                colors.append('rgba(46,204,113,0.8)')  # Vert
            else:
                colors.append('rgba(231,76,60,0.8)')   # Rouge
        except KeyError as e:
            print(f"Warning: Missing node in dictionary - {e}. Skipping row.")
            continue

    # 4. Création du diagramme avec style amélioré
    node_colors = ['#3498db'] * len(crime_types) + ['#2ECC71', '#E74C3C']  # Bleu pour crimes
    
    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="black", width=0.8),
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
        title_text="Flux des types de crime vers leur résolution",
        title_font_size=20,
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        font=dict(color="white", family="Arial"),
        font_size=14,
        height=900,
        margin=dict(l=80, r=80, t=100, b=60)
    )

    return fig