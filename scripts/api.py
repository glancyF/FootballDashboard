import os
import requests
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://v3.football.api-sports.io/"

HEADERS = {"x-apisports-key": API_KEY}


def get_leagues():
    url = f"{BASE_URL}/leagues"
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"[LEAGUES] GET {url}")
        print(f"[LEAGUES] Status Code: {response.status_code}")
        print(f"[LEAGUES] Response Snippet: {response.text[:500]}")

        if response.status_code == 200:
            return response.json().get('response', [])
        else:
            return []
    except Exception as e:
        print(f"[LEAGUES] Exception: {e}")
        return []


def get_seasons():
    url = f"{BASE_URL}/leagues"
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"[SEASONS] GET {url}")
        print(f"[SEASONS] Status Code: {response.status_code}")
        print(f"[SEASONS] Response Snippet: {response.text[:500]}")

        if response.status_code == 200:
            data = response.json()
            seasons = set()
            for league in data['response']:
                for season in league['seasons']:
                    seasons.add(season['year'])
            return sorted(seasons, reverse=True)
        else:
            return []
    except Exception as e:
        print(f"[SEASONS] Exception: {e}")
        return []


def get_matches(league_id, season):
    url = f"{BASE_URL}fixtures"
    params = {
        'league': league_id,
        'season': season,
        'status': 'FT'

    }
    response = requests.get(url, headers=HEADERS, params=params)

    print(f"Request to: {url} | Params: {params}")
    print(f"Status: {response.status_code}, Body: {response.text[:500]}")

    if response.status_code == 200:
        data = response.json()
        return data['response']
    else:
        print(f"Error API: {response.status_code} - {response.text}")
        return []


def get_lineups_for_match(match_id):
    url = f"{BASE_URL}/fixtures/lineups?fixture={match_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("response", [])
    return None
