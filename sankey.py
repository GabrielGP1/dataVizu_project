import pandas as pd
import numpy as np
import plotly.graph_objects as go

def format_count_k(n):
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)

def prepare_nodes(df):
    crime_types = df['Crime_Type'].unique().tolist()
    resolutions = ['Arrested', 'Not Arrested']
    mid = len(crime_types) // 2
    crime_left = crime_types[:mid]
    crime_right = crime_types[mid:]
    all_nodes = crime_left + resolutions + crime_right
    node_dict = {node: i for i, node in enumerate(all_nodes)}
    return all_nodes, node_dict, crime_left, crime_right, resolutions

def calculate_flows(df, node_dict):
    flow = df.groupby(['Crime_Type', 'Resolution']).size().reset_index(name='Count')
    total_by_crime = df.groupby('Crime_Type').size().reset_index(name='Total')
    flow = pd.merge(flow, total_by_crime, on='Crime_Type')
    flow['Percentage'] = (flow['Count'] / flow['Total']) * 100
    
    sources, targets, values = [], [], []
    colors, hover_colors, counts, totals = [], [], [], []
    
    for _, row in flow.iterrows():
        try:
            sources.append(node_dict[row['Crime_Type']])
            targets.append(node_dict[row['Resolution']])
            values.append(row['Percentage'])
            colors.append('rgba(128,128,128,0.4)')
            hover_colors.append('rgba(46,204,113,0.8)' if row['Resolution'] == 'Arrested' else 'rgba(231,76,60,0.8)')
            counts.append(format_count_k(row['Count']))
            totals.append(format_count_k(row['Total']))
        except KeyError:
            continue
    
    return sorted(sources), targets, values, colors, hover_colors, counts, totals

def get_node_positions(all_nodes, crime_left, resolutions, crime_right):
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

def get_node_colors(crime_left, crime_right):
    return ['#3498db'] * len(crime_left) + ['#2ECC71', '#E74C3C'] + ['#9b59b6'] * len(crime_right)

def create_sankey_figure(all_nodes, node_colors, x, y, totals, sources, targets, values, colors, hover_colors, counts):
    return go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors,
            customdata=totals,
            x=x,
            y=y,
            hoverlabel=dict(font=dict(color="white")),
            hovertemplate='%{label}<br>Total Cases: %{customdata}<extra></extra>'
        ),
        link=dict(
        source=sources,
        target=targets,
        value=values,
        color=colors,
        customdata=counts,
        hoverlabel=dict(font=dict(color="white"), bgcolor="rgba(0,0,0)"),
        hovertemplate='%{target.label}<br>Crime: %{source.label}<br>Total: %{customdata}<br>Percentage: %{value:.1f}%<extra></extra>'
    )

    )])

def create_sankey(df):
    if not {'Crime_Type', 'Resolution'}.issubset(df.columns):
        raise ValueError("Missing required columns")
    
    all_nodes, node_dict, crime_left, crime_right, resolutions = prepare_nodes(df)
    sources, targets, values, colors, hover_colors, counts, totals = calculate_flows(df, node_dict)
    x, y = get_node_positions(all_nodes, crime_left, resolutions, crime_right)
    node_colors = get_node_colors(crime_left, crime_right)
    fig = create_sankey_figure(all_nodes, node_colors, x, y, totals, sources, targets, values, colors, hover_colors, counts)
    
    fig.update_layout(
        title_font_size=20,
        font=dict(color="white"),
        plot_bgcolor='black',
        paper_bgcolor='black'
    )
    
    return fig