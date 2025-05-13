import time

import streamlit as st
from scripts.database import init_db, insert_matches, get_all_matches, filter_matches
from scripts.api import get_matches, get_leagues, get_seasons, BASE_URL, HEADERS
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
import requests
import json

st.set_page_config(page_title="Football Dashboard", page_icon="⚽", layout="wide")

init_db()
with open('assets/styles.css', encoding='utf-8') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("FOOTBALL DASHBOARD 🚀")
st.write("Welcome to the admin panel")

menu = ["Main", "Load matches", "View matches"]
choice = st.sidebar.selectbox("Menu", menu)

df = get_all_matches()

leagues = get_leagues()
seasons = sorted([season for season in get_seasons() if int(season) <= 2023], reverse=True)
league_name_to_id = {league['league']['name']: league['league']['id'] for league in leagues}

if choice == 'Main':
    st.subheader("Main page")
    st.write("Use menu for navigation")

elif choice == 'Load matches':
    st.subheader("Load Past Matches")

    if not leagues or not seasons:
        st.error("Failed to load data from the API. Please check your API key, quota, or internet connection.")

    if leagues and seasons:
        league_name_to_id = {l['league']['name']: l['league']['id'] for l in leagues}

        selected_league_name = st.selectbox(
            "Select a league",
            list(league_name_to_id.keys()),
            key="league_select"
        )

        selected_season = st.selectbox(
            "Select a season",
            seasons,
            key="season_select"
        )

        if st.button("Load Past Matches", key="load_past_matches"):
            league_id = league_name_to_id.get(selected_league_name)

            if league_id and selected_season:
                st.info(f"Fetching matches for {selected_league_name} ({selected_season})...")
                matches = get_matches(league_id, selected_season)
                st.session_state.loaded_matches = matches
                st.write(f"[DEBUG] Got {len(matches)} matches")

        if "loaded_matches" in st.session_state:
            matches = st.session_state.loaded_matches
            if matches:
                st.success(f"Fetched {len(matches)} past matches")
                st.header("Finished Matches")

                for match in matches:
                    cols = st.columns([1, 4, 1])
                    with cols[0]:
                        logo = match['teams']['home']['logo']
                        if logo:
                            st.image(logo, width=50)
                        st.write(match['teams']['home']['name'])

                    with cols[1]:
                        st.write(
                            f"**{match['teams']['home']['name']}** vs **{match['teams']['away']['name']}**")
                        st.write(
                            f"Date: {match['fixture']['date']} | Status: {match['fixture']['status']['short']}")

                    with cols[2]:
                        logo = match['teams']['away']['logo']
                        if logo:
                            st.image(logo, width=50)
                        st.write(match['teams']['away']['name'])

                if st.button("Save All Finished Matches", key="save_matches"):
                    st.write("[DEBUG] Saving to database...")
                    try:
                        insert_matches(matches)
                        st.success(f"Saved {len(matches)} matches into the database!")
                    except Exception as a:
                        st.write(f"Error with insert,type of error {a}")


elif choice == 'View matches':
    st.subheader('View matches')

    stored_matches = get_all_matches()

    if not stored_matches.empty:

        stored_matches['short_date'] = pd.to_datetime(stored_matches['date']).dt.strftime('%Y-%m-%d')

        seasons = sorted(stored_matches['season'].dropna().unique())
        teams = sorted(set(stored_matches['home_team'].dropna()) | set(stored_matches['away_team'].dropna()))
        competitions = sorted(stored_matches['competition'].dropna().unique())
        dates = sorted(stored_matches['short_date'].dropna().unique())

        season_filter = st.selectbox("Filter by season", ['ALL'] + list(seasons))
        team_filter = st.selectbox("Filter by teams", ['ALL'] + list(teams))
        competition_filter = st.selectbox("Filter by competition", ['ALL'] + list(competitions))
        date_filter = st.selectbox("Filter by date", ['ALL'] + list(dates))

        if st.button('Show filtered matches'):
            season = None if season_filter == 'ALL' else season_filter
            team = None if team_filter == 'ALL' else team_filter
            competition = None if competition_filter == 'ALL' else competition_filter
            date = None if date_filter == 'ALL' else date_filter

            filtered_matches = filter_matches(season=season, team=team, competition=competition, date=date)
            st.session_state.filtered_matches = filtered_matches
        else:
            filtered_matches = st.session_state.get("filtered_matches", None)

        if filtered_matches is not None and not filtered_matches.empty:
            st.success(f"Found {len(filtered_matches)} matches")

            filtered_matches["formatted_date"] = pd.to_datetime(filtered_matches["date"]).dt.strftime("%d %b, %Y %H:%M")
            filtered_matches["match_display"] = filtered_matches["home_team"] + " vs " + filtered_matches["away_team"] + \
                                                " (" + filtered_matches["formatted_date"] + ")"

            with st.expander("Click to view filtered matches"):
                for _, match in filtered_matches.iterrows():
                    cols = st.columns([1, 4, 1])
                    with cols[0]:
                        if pd.notna(match.get('home_team_logo')):
                            st.image(match['home_team_logo'], width=50)
                        st.write(match['home_team'])
                    with cols[1]:
                        st.write(f"**{match['home_team']}** vs **{match['away_team']}**")
                        st.write(f"Date: {match['formatted_date']} | Status: {match['status']}")
                    with cols[2]:
                        if pd.notna(match.get('away_team_logo')):
                            st.image(match['away_team_logo'], width=50)
                        st.write(match['away_team'])

            selected_match_display = st.selectbox("Select a match", filtered_matches["match_display"])
            selected_match_id = \
                filtered_matches.loc[filtered_matches["match_display"] == selected_match_display, "id"].values[0]

            if st.button("View match details"):
                st.session_state.selected_match_id = selected_match_id
                switch_page("match_details")
        else:
            st.warning("No matches found for the selected filters.")
    else:
        st.info("No matches stored in database.")
