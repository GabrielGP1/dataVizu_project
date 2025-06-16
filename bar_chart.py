
import pandas as pd
import matplotlib.colors as mcolors
import plotly.express as px


def create_bar_chart(df):
    
    fig = px.bar(
        df,
        x="Period",               # Weekday / Weekend
        y="Count",                # Nombre de crimes
        color="Crime_Type",       # Empilement par type de crime
        barmode="stack",          # Stacked bars
        color_discrete_sequence=px.colors.qualitative.Bold  # Palette stylée type Bloomberg
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
        yaxis=dict(title='Number of Crimes'),
        legend_title="Crime Type",
        height=600,
    )

    # Affichage du graphique
    return fig
