import legend
import plotly.express as px
import plotly.graph_objects as go

def create_interactive_hour_chart(df, time_unit: str = "hour"):
    if time_unit not in ['hour', 'month', 'year']:
        time_unit = 'hour'
        
    df = legend.preprocess_labels(df, ['crime_grouped'])

    if time_unit in ['hour', 'month']:
        grouped = (
            df.groupby(['year', time_unit, 'crime_grouped'])
            .size()
            .reset_index(name='count')
            .groupby([time_unit, 'crime_grouped'])['count']
            .mean()
            .reset_index()
        )
    else:
        grouped = (
            df.groupby([time_unit, 'crime_grouped'])
            .size()
            .reset_index(name='count')
        )

    fig = px.area(
        grouped,
        x=time_unit,
        y='count',
        color='crime_grouped',
        title=f"Crime Distribution by {time_unit.capitalize()}",
         labels={
            time_unit: time_unit.capitalize(), 
            'count': 'Number of Crimes',
            'crime_grouped': 'Crime Type'
        },
        color_discrete_map=legend.CUSTOM_COLORS
    )

    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        template='plotly_dark',
        height=600,
        font=dict(family='Arial')
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Type: %{fullData.name}<br>Count: %{y:,}<extra></extra>',
        hoverlabel=legend.COMMON_HOVER_CONFIG['hoverlabel']
    )
    
    if time_unit == 'hour':
        fig.update_xaxes(tickformat="%H:%M")
    
    return fig

