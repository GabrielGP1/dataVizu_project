"""
sankey.py

This script generates a customized Sankey diagram using Plotly to visualize the relationship
between crime types and their resolutions (e.g., Arrested / Not Arrested).

Developed by: Team 13
Date: 2025-06-22
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

def format_count_k(n):
    """
    Format a number using 'k' notation if >= 1000.

    Args:
        n (int): Number to format.

    Returns:
        str: Formatted string.
    """
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)


def prepare_nodes(df):
    """
    Prepare node labels and mappings for the Sankey diagram.

    Args:
        df (pd.DataFrame): Data containing 'Crime_Type' and 'Resolution' columns.

    Returns:
        tuple: (all_nodes, node_dict, crime_left, crime_right, resolutions)
    """
    crime_types = sorted(df['Crime_Type'].unique().tolist())
    resolutions = ['Arrested', 'Not Arrested']
    mid = len(crime_types) // 2
    crime_left = crime_types[:mid]
    crime_right = crime_types[mid:]
    all_nodes = crime_left + resolutions + crime_right
    node_dict = {node: i for i, node in enumerate(all_nodes)}
    print(node_dict)
    print(all_nodes)
    return all_nodes, node_dict, crime_left, crime_right, resolutions


def calculate_flows(df, node_dict):
    """
    Calculate flow values and prepare link attributes for the Sankey diagram.

    Args:
        df (pd.DataFrame): Input dataframe.
        node_dict (dict): Mapping of node names to indices.

    Returns:
        tuple: sources, targets, values, colors, hover_colors, counts, totals
    """
    flow = df.groupby(['Crime_Type', 'Resolution']).size().reset_index(name='Count')
    total_by_crime = df.groupby('Crime_Type').size().reset_index(name='Total')
    flow = pd.merge(flow, total_by_crime, on='Crime_Type')
    flow['Percentage'] = (flow['Count'] / flow['Total']) * 100
    flow['Source_Index'] = flow['Crime_Type'].map(node_dict)
    flow = flow.sort_values(by='Source_Index')
    
    sources = flow['Source_Index'].tolist()
    targets = flow['Resolution'].map(node_dict).tolist()
    values = flow['Percentage'].tolist()
    colors = ['rgba(128,128,128,0.4)'] * len(flow)
    hover_colors = flow['Resolution'].map(lambda r: 'rgba(46,204,113,0.8)' if r == 'Arrested' else 'rgba(231,76,60,0.8)').tolist()
    counts = flow['Count'].apply(format_count_k).tolist()
    totals = flow['Total'].apply(format_count_k).tolist()

    return sources, targets, values, colors, hover_colors, counts, totals


def get_node_positions(all_nodes, crime_left, resolutions, crime_right):
    """
    Define the x and y positions of each node in the Sankey diagram.

    Args:
        all_nodes (list): All node names.
        crime_left (list): Left-side crime types.
        resolutions (list): Middle resolution labels.
        crime_right (list): Right-side crime types.

    Returns:
        tuple: x, y coordinates
    """
    x = []
    for node in all_nodes:
        if node in crime_left:
            x.append(0.0)
        elif node in resolutions:
            x.append(0.5)
        elif node in crime_right:
            x.append(1.0)
    
    y = np.linspace(0.0, 1.0, num=len(all_nodes)).tolist()
    return x, y


def get_node_colors():
    """
    Assign a specific color to each node.

    Returns:
        list: List of color strings.
    """
    return [
        "#C10B0B", 
        "#8E44AD",
        "#2980B9",
        "#73C836",
        "#34495E"
    ] + ['#2ECC71', '#E74C3C'] + [
        "#09A283",
        "#F39C12",
        "#B6C0C1",
        "#822C22",
        "#160B6E"
    ]


def create_sankey_figure(all_nodes, node_colors, x, y, totals, sources, targets, values, colors, hover_colors, counts):
    """
    Generate the Sankey figure object.

    Args:
        all_nodes (list): List of node labels.
        node_colors (list): Colors for each node.
        x (list): x coordinates of nodes.
        y (list): y coordinates of nodes.
        totals (list): Total values per node.
        sources (list): Indices of source nodes.
        targets (list): Indices of target nodes.
        values (list): Link values.
        colors (list): Link colors.
        hover_colors (list): Colors for link hover.
        counts (list): Formatted link counts for display.

    Returns:
        go.Figure: Plotly Sankey figure.
    """
    return go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.8),
            label=all_nodes,
            color=node_colors,
            customdata=totals,
            x=x,
            y=y,
            hoverlabel=dict(font=dict(color="white")),
            hovertemplate='%{label}<br>Total Cases: %{customdata}<extra></extra>',
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors,
            customdata=counts,
            hovercolor=hover_colors,
            hoverlabel=dict(font=dict(color="white"), bgcolor="rgba(0,0,0)"),
            hovertemplate='%{target.label}<br>Crime: %{source.label}<br>Total: %{customdata}<br>Percentage: %{value:.1f}%<extra></extra>'
        )
    )])


def create_sankey(df):
    """
    Orchestrates the creation of the Sankey diagram from raw dataframe.

    Args:
        df (pd.DataFrame): Data with 'Crime_Type' and 'Resolution' columns.

    Returns:
        go.Figure: Final Sankey diagram figure.
    """
    if not {'Crime_Type', 'Resolution'}.issubset(df.columns):
        raise ValueError("Missing required columns: 'Crime_Type' and/or 'Resolution'")
    
    all_nodes, node_dict, crime_left, crime_right, resolutions = prepare_nodes(df)
    sources, targets, values, colors, hover_colors, counts, totals = calculate_flows(df, node_dict)
    x, y = get_node_positions(all_nodes, crime_left, resolutions, crime_right)
    node_colors = get_node_colors()
    fig = create_sankey_figure(all_nodes, node_colors, x, y, totals, sources, targets, values, colors, hover_colors, counts)
    
    fig.update_layout(
        title_font_size=20,
        font=dict(color="white"),
        plot_bgcolor="#111111",
        paper_bgcolor="#111111"
    )
    
    return fig
