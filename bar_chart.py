import pandas as pd
import matplotlib.colors as mcolors
import plotly.express as px
import legend


def create_bar_chart(df):
    
    df = legend.preprocess_labels(df, ['Crime_Type', 'Period'])
    df["Count_Label"] = df["Count"].apply(legend.format_number)
    
    fig = px.bar(
        df,
        x="Period",               # Weekday / Weekend
        y="Count_Label",                # Nombre de crimes
        color="Crime_Type",       # Empilement par type de crime
        barmode="stack",          # Stacked bars
        color_discrete_map=legend.CUSTOM_COLORS,  # Palette stylée type Bloomberg
        labels={'Crime_Type': 'Crime Type', 'Count': 'Number of Crimes'}
    )

    # Mise en page personnalisée
    fig.update_layout(
        title={
            'text': "Crime Distribution: Weekday vs Weekend",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        plot_bgcolor='#111111',
        paper_bgcolor='#111111',
        font=dict(color='white'),
        xaxis=dict(title='Period'),
        yaxis=dict(title='Number of Crimes (k)'),
        legend_title="Crime Type",
        height=600,
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Crime Type: %{fullData.name}<br>Count: %{y:,}k<extra></extra>',
        hoverlabel=legend.COMMON_HOVER_CONFIG['hoverlabel']
    )

    # Affichage du graphique
    return fig
