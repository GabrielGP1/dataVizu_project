import pandas as pd
import plotly.express as px
import legend

def create_bar_chart(df):
    """
    Crée un graphique à barres empilées montrant la distribution des crimes
    en semaine vs fin de semaine, groupés par type de crime.

    Args:
        df (pd.DataFrame): DataFrame contenant les colonnes 'Crime_Type', 'Period', et 'Count'.

    Returns:
        plotly.graph_objects.Figure: Graphique à barres personnalisé.
    """
    
    df = legend.preprocess_labels(df, ['Crime_Type', 'Period'])

    fig = px.bar(
        df,
        x="Period",
        y="Count", 
        color="Crime_Type",
        barmode="stack",
        color_discrete_map=legend.CUSTOM_COLORS,
        labels={'Crime_Type': 'Crime Type', 'Count': 'Number of Crimes'}
    )


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
        yaxis=dict(
            title='Number of Crimes',
            tickformat='~s' 
        ),
        legend_title="Crime Type",
        height=600,
    )


    def format_hover_k(y):
        if y >= 1_000_000:
            return f"{y / 1_000_000:.1f}M"
        elif y >= 1_000:
            return f"{y / 1_000:.1f}k"
        else:
            return str(y)


    for trace in fig.data:
        counts = df[df['Crime_Type'] == trace.name]['Count'].values
        formatted = [format_hover_k(y) for y in counts]
        trace.hovertemplate = (
            '<b>%{x}</b><br>'
            f'Crime Type: {trace.name}<br>'
            'Count: %{customdata}<extra></extra>'
        )
        trace.customdata = formatted
        trace.hoverlabel = legend.COMMON_HOVER_CONFIG['hoverlabel']

    return fig
