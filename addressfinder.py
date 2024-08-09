from bs4 import BeautifulSoup
import requests
import pandas as pd

def import_data_to_df():
    df = pd.read_csv('data/input_stadium_names.csv')
    return df

def get_html_document(url):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0"}
    cookies = {"CONSENT": "YES+cb.20220419-08-p0.cs+FX+111"}
    response = requests.get(url, headers=headers, cookies=cookies)
    return response.text

def get_google_search_url(stadium_search):
    address_search_prefix = "https://www.google.co.uk/search?q="
    return address_search_prefix + stadium_search

def get_addresses(df):
    for index, row in df.iterrows():
        stadium = df.at[index, 'stadium']
        stadium_search_url = get_google_search_url(stadium + ' stadium')
        stadium_html = get_html_document(stadium_search_url)
        soup = BeautifulSoup(stadium_html, 'html.parser')
        address = soup.find("span", {"class": "LrzXr"})
        if address is None:
            continue
        else:
            df.at[index, 'address'] = address.get_text()
    return df

def output_data(df):
    return df.to_csv('data/output_stadium_addresses.csv')

def main():
    input_addresses = import_data_to_df()
    output_df = get_addresses(input_addresses)
    output_data(output_df)

if __name__ == "__main__":
    main()