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

def display_flight_info(data):
    segment = data['segment']
    st.header("Flight Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Flight:** {segment['airlineCode']}{segment['flightNumber']}")
        st.write(f"**Date:** {segment['flightDate']}")
        st.write(f"**Aircraft:** {segment['equipmentDescriptionLong']} ({segment['ship']})")
    with col2:
        st.write(f"**From:** {segment['departureAirportName']}")
        st.write(f"**To:** {segment['arrivalAirportName']}")
        st.write(f"**Departure:** {segment['scheduledDepartureTime']}")
        st.write(f"**Arrival:** {segment['scheduledArrivalTime']}")

def display_cabin_availability(data):
    st.header("Cabin Availability")
    for cabin in data['pbts']:
        with st.expander(f"{cabin['cabin']} Cabin"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Capacity", cabin['capacity'])
            col2.metric("Booked", cabin['booked'])
            col3.metric("Available", cabin['capacity'] - cabin['booked'])
            
            st.write("**Additional Information:**")
            st.write(f"- Authorized: {cabin['authorized']}")
            st.write(f"- Revenue Standby: {cabin['revenueStandby']}")
            st.write(f"- Waitlist: {cabin['waitList']}")

def display_upgrade_standby_info(data):
    st.header("Upgrade and Standby Information")
    for cabin_type in ['front', 'rear']:
        if cabin_type in data:
            with st.expander(f"{cabin_type.capitalize()} Cabin"):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Cleared")
                    if data[cabin_type]['cleared']:
                        for passenger in data[cabin_type]['cleared']:
                            st.write(f"- {passenger['passengerName']} (Seat: {passenger['seatNumber']})")
                    else:
                        st.write("No passengers cleared yet.")
                with col2:
                    st.subheader("Standby")
                    if data[cabin_type]['standby']:
                        for passenger in data[cabin_type]['standby']:
                            st.write(f"- {passenger['passengerName']} (Current Seat: {passenger['seatNumber']})")
                    else:
                        st.write("No passengers on standby.")

def main():
    st.set_page_config(page_title="United Airlines Flight Info", page_icon="✈️", layout="wide")
    st.title("✈️ United Airlines Flight Information")

    col1, col2, col3 = st.columns(3)
    with col1:
        flight_number = st.text_input("Enter Flight Number:", "1274")
    with col2:
        flight_date = st.date_input("Select Flight Date:", date.today())
    with col3:
        from_airport_code = st.text_input("Enter Departure Airport Code:", "IAD")

    if st.button("Get Flight Information"):
        with st.spinner("Fetching data..."):
            data = get_cabin_availability(flight_number, flight_date.strftime("%Y-%m-%d"), from_airport_code)
        
        if data:
            display_flight_info(data)
            display_cabin_availability(data)
            display_upgrade_standby_info(data)

            st.success("Data retrieved successfully!")

if __name__ == "__main__":
    main()