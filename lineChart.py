import plotly.express as px
import plotly.graph_objects as go

def create_interactive_hour_chart(df, time_unit: str = "hour"):
    if time_unit not in ['hour', 'month', 'year']:
        time_unit = 'hour'

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
        labels={time_unit: time_unit.capitalize(), 'count': 'Number of Crimes'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        template='plotly_dark',
        height=600
    )
    return fig

