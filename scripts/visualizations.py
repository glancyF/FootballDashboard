import plotly.graph_objects as go
from scripts.database import get_all_matches
import pandas as pd


def plot_match_goals(match_df):
    home_goals = match_df.iloc[0]['home_score']
    away_goals = match_df.iloc[0]['away_score']
    home_team = match_df.iloc[0]['home_team']
    away_team = match_df.iloc[0]['away_team']

    teams = [home_team, away_team]
    goals = [home_goals, away_goals]

    fig = go.Figure(data=[go.Bar(
        x=teams,
        y=goals,
        marker=dict(color=['#EB8A3E', '#EBB582'],
                    line=dict(color='#FFFFFF', width=2)),
        text=[f'{home_goals} Goals' if team == home_team else f'{away_goals} Goals' for team in teams],
        hoverinfo='text',
        opacity=0.8,
        hoverlabel=dict(bgcolor="black", font_size=16, font_family="Arial")
    )])

    fig.update_layout(
        title='Goals per Team',
        title_font=dict(size=24, color='#EB8A3E', family="Arial, sans-serif"),
        xaxis=dict(
            title='Teams',
            tickmode='array',
            tickvals=teams,
            ticktext=[f'<b>{team}</b>' for team in teams],
            showgrid=False,
            tickangle=45
        ),
        yaxis=dict(
            title='Goals',
            showgrid=True,
            gridcolor='#555555',
            zeroline=False
        ),
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white', size=14),
        margin=dict(l=20, r=20, t=40, b=40)
    )

    return fig


def plot_team_performance(team_name):
    matches = get_all_matches()
    team_data = matches[(matches['home_team'] == team_name) | (matches['away_team'] == team_name)]

    team_data['date'] = pd.to_datetime(team_data['date'])
    team_data = team_data.sort_values('date')

    team_data_home = team_data[team_data['home_team'] == team_name]
    team_data_away = team_data[team_data['away_team'] == team_name]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=team_data_home['date'],
        y=team_data_home['home_score'],
        mode='lines+markers',
        name=f'{team_name} Home',
        line=dict(color='#EB8A3E', width=4),
        marker=dict(size=8, color='#EB8A3E')
    ))

    fig.add_trace(go.Scatter(
        x=team_data_away['date'],
        y=team_data_away['away_score'],
        mode='lines+markers',
        name=f'{team_name} Away',
        line=dict(color='#EBB582', width=4),
        marker=dict(size=8, color='#EBB582')
    ))

    fig.update_layout(
        title=f'{team_name} Performance Over Time',
        title_font=dict(color='#EB8A3E', size=24),
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white', size=14),
        xaxis=dict(
            tickangle=45,
            showgrid=True,
            gridcolor='#555555',
            zeroline=False,
            title='Date'
        ),
        yaxis=dict(
            title='Goals Scored',
            showgrid=True,
            gridcolor='#555555',
            zeroline=False
        ),
        hoverlabel=dict(bgcolor="black", font_size=16, font_family="Arial")
    )

    return fig
