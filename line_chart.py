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
        font=dict(family='Arial'),
         title={
            'text': f"Crime Distribution by {time_unit.capitalize()}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20},
        },       
    )
    
    if time_unit == 'hour':
        hover = "<b>Hour: %{x}:00</b><br>Crime Type: %{fullData.name}<br>Average Count: %{y:.0f}<extra></extra>"
    elif time_unit == 'month':
        hover = "<b>Month: %{x}</b><br>Crime Type: %{fullData.name}<br>Average Count: %{y:.0f}<extra></extra>"
    elif time_unit == 'year':
        hover = "<b>Year: %{x}</b><br>Crime Type: %{fullData.name}<br>Total Count: %{y:.0f}<extra></extra>"

    fig.update_traces(
        hovertemplate=hover,
        hoverlabel=legend.COMMON_HOVER_CONFIG['hoverlabel']
    )
        
    if time_unit == 'hour':
        fig.update_xaxes(
            tickmode='array',
            tickvals=list(range(1, 24)),
            title='Hour',
            range=[0.1, None]
        )
    
    elif time_unit == 'month':
        fig.update_yaxes(
            tickmode='array',
            range=[grouped['count'].min() - 0.2, None]
        )
        fig.update_xaxes(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            title='Month',
            range=[df['month'].min() - 0.2, None]
        )
    
    elif time_unit == 'year':
        fig.update_yaxes(
            tickmode='array',
            range=[grouped['count'].min() - 0.2, None]
        )
        fig.update_xaxes(
            tickmode='linear',
            title='Year',
            range=[df['year'].min() - 0.1, None]
        )
    
    return fig
