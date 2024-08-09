from bs4 import BeautifulSoup
import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd

def get_html_document(url):
    response = requests.get(url)
    return response.text

def get_fixture_url(input_date):
    fixtures_url_prefix = "https://www.skysports.com/football/fixtures-results/"
    return fixtures_url_prefix + input_date

def get_search_date():
    d = datetime.today()
    t = timedelta((12 - d.weekday()) % 7)
    next_saturday = (d + t)
    input_date = st.date_input("When are you planning to do the Soccer Saturday Challenge?", next_saturday)
    return input_date.strftime("%#d-%B-%Y")

def extract_fixture_data(soup):
    fixture_list = []
    for header in soup.find_all("h5", {"class": "fixres__header3"}):
        league = header.text
        next_sibling = header.findNextSibling()
        while next_sibling and next_sibling.name == "div":
            team_one = next_sibling.find_all("span", {"class": "swap-text__target"})[0].get_text()
            team_two = next_sibling.find_all("span", {"class": "swap-text__target"})[1].get_text()
            ko_time = next_sibling.find("span", {"class": "matches__date"}).get_text().strip()
            fixture_data = {'league': league, 'home_team': team_one, 'away_team': team_two, 'kick_off': ko_time}
            fixture_list.append(fixture_data)
            next_sibling = next_sibling.findNextSibling()
    return fixture_list

def filter_data(df):
    kick_off_time = '15:00'
    valid_leagues = ["Premier League", "Sky Bet Championship", "Sky Bet League One", "Sky Bet League Two", "National League"]
    return df[(df['kick_off'] == kick_off_time) & (df['league'].isin(valid_leagues))]

def stack_teams(df):
    df_home_team = df['home_team'].rename('team')
    df_away_team = df['away_team'].rename('team')
    stack_teams = pd.concat([df_home_team, df_away_team], axis=0)
    return stack_teams

def join_addresses(df):
    addresses = pd.read_csv('data/stadium_coordinates.csv')
    merged_df = pd.merge(df, addresses, left_on='team', right_on='team', how='inner')
    return merged_df

def generate_app(df):
    st.write("# Soccer Saturday Challenge")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Teams", value=len(pd.unique(df['team'])))
    with col2:
        st.metric("Leagues", value=len(pd.unique(df['league'])))
    st.map(df[['lat', 'lon']], zoom=5)
    st.dataframe(df[['team', 'stadium', 'league', 'postcode']], use_container_width=True, hide_index=True)

def main():
    input_date = get_search_date()
    fixture_url = get_fixture_url(input_date)
    fixture_html = get_html_document(fixture_url)
    soup = BeautifulSoup(fixture_html, 'html.parser')
    fixture_data = extract_fixture_data(soup)
    fixture_df = pd.DataFrame(fixture_data)
    output_data = filter_data(fixture_df)
    stacked_teams = stack_teams(output_data)
    with_addresses = join_addresses(stacked_teams)
    generate_app(with_addresses)

if __name__ == "__main__":
    main()