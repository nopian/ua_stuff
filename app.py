import streamlit as st
import requests
import json
from datetime import datetime, date

# Define a constant for the user agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'

def get_authorization_token():
    token_url = "https://www.united.com/api/svc/token/anonymous"
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json',
        'Accept-Language': 'en-US'
    }
    response = requests.get(token_url, headers=headers)
    if response.status_code == 200:
        token_data = response.json()
        return token_data['data']['token']['hash']
    else:
        st.error(f"Error: Unable to fetch authorization token. Status code: {response.status_code}")
        return None

def get_cabin_availability(flight_number, flight_date, from_airport_code):
    url = f"https://www.united.com/api/flight/upgradeListExtended?flightNumber={flight_number}&flightDate={flight_date}&fromAirportCode={from_airport_code}"
    
    token = get_authorization_token()
    if not token:
        return None

    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json',
        'Accept-Language': 'en-US',
        'Referer': f'https://www.united.com/en/us/flightstatus/details/{flight_number}/{flight_date}/{from_airport_code}',
        'x-authorization-api': f'bearer {token}'
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None

def display_cabin_availability(data):
    if data:
        st.subheader("Cabin Availability:")
        for cabin in data['pbts']:
            st.write(f"\n**{cabin['cabin']} Cabin:**")
            st.write(f"- Capacity: {cabin['capacity']}")
            st.write(f"- Booked: {cabin['booked']}")
            st.write(f"- Available: {cabin['capacity'] - cabin['booked']}")

        st.subheader("Upgrade and Standby Information:")
        for cabin in ['front', 'rear']:
            if cabin in data:
                st.write(f"\n**{cabin.capitalize()} Cabin:**")
                st.write(f"- Cleared: {len(data[cabin]['cleared'])}")
                st.write(f"- Standby: {len(data[cabin]['standby'])}")

def main():
    st.title("United Airlines Cabin Availability Checker")

    flight_number = st.text_input("Enter Flight Number:", "1274")
    flight_date = st.date_input("Select Flight Date:", date.today())
    from_airport_code = st.text_input("Enter Departure Airport Code:", "IAD")

    if st.button("Check Availability"):
        with st.spinner("Fetching data..."):
            data = get_cabin_availability(flight_number, flight_date.strftime("%Y-%m-%d"), from_airport_code)
        
        if data:
            display_cabin_availability(data)

if __name__ == "__main__":
    main()