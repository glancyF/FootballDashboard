from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text
from dotenv import load_dotenv
import sqlite3
import pandas as pd
import os
import requests
from scripts.api import get_lineups_for_match

load_dotenv()
db_path = os.getenv("DB_PATH")
engine = create_engine(f"sqlite:///{db_path}")
metadata = MetaData()

matches = Table(
    'matches',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('date', String),
    Column('home_team', String),
    Column('away_team', String),
    Column('home_score', Integer),
    Column('away_score', Integer),
    Column('status', String),
    Column('season', String),
    Column('competition', String),
    Column('home_team_logo', String),
    Column('away_team_logo', String),
    Column('lineups', String)

)

leagues = Table(
    'leagues',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('country', String),
    Column('logo', String),
    Column('season', String),
    Column('start_date', String),
    Column('end_date', String),
    Column('type', String),
)


def insert_leagues(league_list):
    with engine.connect() as conn:
        for league_data in league_list:
            league = league_data['league']
            country = league_data.get('country', {})

            seasons = league_data.get('seasons', [])
            for season in seasons:
                if not season.get('current', False):
                    continue

                league_id = league['id']
                existing_league = conn.execute(
                    leagues.select().where(
                        (leagues.c.id == league_id) & (leagues.c.season == str(season['year']))
                    )
                ).fetchone()

                if existing_league is None:
                    conn.execute(leagues.insert().values(
                        id=league_id,
                        name=league['name'],
                        country=country.get('name', 'Unknown'),
                        logo=league.get('logo', ''),
                        season=str(season['year']),
                        start_date=season.get('start'),
                        end_date=season.get('end'),
                        type=league.get('type', 'League')
                    ))
        conn.commit()


def get_all_leagues():
    connection = sqlite3.connect(db_path)
    query = "SELECT * FROM leagues"
    df = pd.read_sql(query, connection)
    connection.close()
    return df


def init_db():
    metadata.create_all(engine)
    print("Initialization complete!")


def insert_matches(match_list):
    with engine.begin() as conn:
        for match_data in match_list:
            try:
                match = match_data['fixture']
                teams = match_data['teams']
                score = match_data['score']
                league = match_data['league']
                match_id = match['id']

                home_logo = teams['home']['logo']
                away_logo = teams['away']['logo']
                home_score = score['fulltime']['home'] if score['fulltime'] else None
                away_score = score['fulltime']['away'] if score['fulltime'] else None
                status = match_data['fixture']['status']['short']

                lineups = get_lineups_for_match(match_id)
                #print(f"[LINEUPS] Match {match_id}: lineups = {lineups}") Debug

                existing_match = conn.execute(
                    matches.select().where(matches.c.id == match_id)
                ).fetchone()

                if existing_match is None:
                    #print(f"[MATCHES] Inserting match {match_id}") debug
                    conn.execute(matches.insert().values(
                        id=match_id,
                        date=match['date'],
                        status=status,
                        home_team=teams['home']['name'],
                        away_team=teams['away']['name'],
                        home_score=home_score,
                        away_score=away_score,
                        season=str(league['season']),
                        competition=league['name'],
                        home_team_logo=home_logo,
                        away_team_logo=away_logo,
                        lineups=json.dumps(lineups) if lineups else None
                    ))
                else:

                    updated_fields = {}
                    if existing_match.home_score != home_score:
                        updated_fields['home_score'] = home_score
                    if existing_match.away_score != away_score:
                        updated_fields['away_score'] = away_score
                    if existing_match.status != status:
                        updated_fields['status'] = status
                    if updated_fields:
                        print(f"[DB] Updating match {match_id} with {updated_fields}")
                        conn.execute(
                            matches.update()
                            .where(matches.c.id == match_id)
                            .values(**updated_fields)
                        )

            except Exception as e:
                print(f"[ERROR] Failed to insert match {match_data.get('fixture', {}).get('id', 'unknown')}: {e}")


def get_all_matches():
    connection = sqlite3.connect(db_path)
    query = "SELECT id, date, home_team, away_team, home_score, away_score, status, season, competition, home_team_logo, away_team_logo, lineups FROM matches"
    df = pd.read_sql(query, connection)
    connection.close()
    return df


def filter_matches(season=None, team=None, competition=None, date=None):
    connection = sqlite3.connect(db_path)
    query = "SELECT * FROM matches WHERE 1=1"
    params = []

    if season:
        query += " AND season = ?"
        params.append(season)

    if team:
        query += " AND (home_team = ? OR away_team = ?)"
        params.extend([team, team])

    if competition:
        query += " AND competition = ?"
        params.append(competition)

    if date:
        query += " AND substr(date, 1, 10) = ?"
        params.append(date)

    df = pd.read_sql(query, connection, params=params)
    connection.close()
    return df
