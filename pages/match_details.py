import streamlit as st
from scripts.database import get_all_matches
import datetime
from scripts.visualizations import plot_match_goals, plot_team_performance
import pandas as pd
import json

with open('assets/styles.css', encoding='utf-8') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

match_id = st.session_state.get('selected_match_id', None)

if match_id is not None:
    stored_matches = get_all_matches()
    selected_match = stored_matches[stored_matches['id'] == int(match_id)]

    if not selected_match.empty:
        home_team = selected_match.iloc[0]['home_team']
        away_team = selected_match.iloc[0]['away_team']
        home_team_logo = selected_match.iloc[0]['home_team_logo']
        away_team_logo = selected_match.iloc[0]['away_team_logo']

        st.markdown("## ⚽ Match Details")

        match_details = f"""
        <div style="display: flex; align-items: center;">
            <img src="{home_team_logo}" width="30" style="margin-right: 10px;"/> 
            <h3 style="margin-right: 10px;">{home_team}</h3> 
            <span>vs</span>
            <h3 style="margin-left: 10px;">{away_team}</h3> 
            <img src="{away_team_logo}" width="30" style="margin-left: 10px;"/>
        </div>
        """
        st.markdown(match_details, unsafe_allow_html=True)

        raw_date = selected_match.iloc[0]['date']
        try:
            parsed_date = datetime.datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S+00:00")
            formatted_date = parsed_date.strftime("%d %B %Y, %H:%M UTC")
            st.write(f"📅 **Date:** {formatted_date}")
        except:
            st.write(f"📅 **Date:** {raw_date}")

        st.markdown(f"- 🏆 **Competition:** {selected_match.iloc[0]['competition']}")
        st.markdown(f"- 📅 **Season:** {selected_match.iloc[0]['season']}")
        st.markdown(f"- 🔴 **Status:** {selected_match.iloc[0]['status']}")
        st.markdown(f"- ⚽ **Score:** `{selected_match.iloc[0]['home_score']} - {selected_match.iloc[0]['away_score']}`")

        st.markdown("---")

        with st.expander("#### 📊 **Match Summary**"):
            fig = plot_match_goals(selected_match)
            st.plotly_chart(fig, use_container_width=False)

        with st.expander("#### 📈 **Teams performance over time**"):
            team_options = [home_team, away_team]

            team1 = st.selectbox("Select first team", team_options, key="team1_perf")

            team2 = st.selectbox("Select second team", team_options, key="team2_perf")

            if team1 == team2:
                st.warning("Both teams are the same! Switching the second team automatically.")
                team2 = [team for team in team_options if team != team1][0]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**{team1} performance:**")
                fig1 = plot_team_performance(team1)
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                st.markdown(f"**{team2} performance:**")
                fig2 = plot_team_performance(team2)
                st.plotly_chart(fig2, use_container_width=True)

        lineups_raw = selected_match.iloc[0].get("lineups")
        if lineups_raw:
            try:
                #print(f"Lineups Raw: {lineups_raw}") Debug
                lineups = json.loads(lineups_raw)
                st.markdown("### 🧩 Lineups")
                for team_lineup in lineups:
                    team_name = team_lineup['team']['name']
                    st.markdown(f"**{team_name}**")
                    starting = [p['player']['name'] for p in team_lineup.get('startXI', [])]
                    subs = [p['player']['name'] for p in team_lineup.get('substitutes', [])]
                    st.markdown("**STARTING**")
                    st.write(", ".join(starting) if starting else "Not available")
                    st.markdown("**Substitutes:**")
                    st.write(", ".join(subs) if subs else "Not available")
            except Exception as e:
                st.error(f"Failed to parse lineups: {e}")
        else:
            st.warning("No lineups available for this match.")
    else:
        st.error("Match not found")
else:
    st.warning("No match selected. Please select a match on the previous page.")
