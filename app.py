import streamlit as st
from utils import *
import json

def main():
    # Set the page configuration
    st.set_page_config(page_title="Travel Guide Assistant", layout="wide")

    # Create a sidebar with navigation options
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("📌 Go to", ["🏠 Home", "🎫 Ticket Info", "🗺️ Itinerary", "🏨 Hotels"])

    # Navigate to the selected page
    if page == "🏠 Home":
        home_page()
    elif page == "🎫 Ticket Info":
        ticket_info_page()
    elif page == "🗺️ Itinerary":
        itinerary_page()
    elif page == "🏨 Hotels":
        hotels_page()

def home_page():
    # Display the home page
    st.title("Travel Guide Assistant...✈️")
    st.image("image/Flughafen.jpg", use_container_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.write("Welcome to the Travel Guide Assistant! Upload your ticket and let's start planning your trip.")
    st.write("### How to Use This Page")
    st.write("""
        1. **Upload Your Ticket:** Use the 'Ticket Info' section to upload your travel ticket in PDF format.
        2. **Enter Your Stay Duration:** Specify the number of days you'll be staying.
        3. **Extract Data:** Click the 'Extract Data' button to process your ticket and get details about your trip.
        4. **View Itinerary:** Go to the 'Itinerary' section to see a planned itinerary with tourist places to visit.
        5. **Find Hotels:** Check the 'Hotels' section for recommended hotels based on your destination and stay duration.
    """)

def ticket_info_page():
    # Display the ticket information extraction page
    st.image("image/Ticket.jpg", use_column_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("Ticket Information Extraction")
    st.write("Upload your travel ticket and enter your stay duration to get personalized trip details.")

    # Step 1: Upload ticket
    with st.expander("Step 1: Upload Your Ticket"):
        pdf = st.file_uploader("Upload Ticket here (PDF only)", type=["pdf"], accept_multiple_files=True)
        st.write("Make sure your ticket is in PDF format.")

    # Step 2: Enter stay duration
    with st.expander("Step 2: Enter Stay Duration"):
        custom_test_value = st.number_input("Enter the number of days of your stay", min_value=1, step=1)
        st.write("Specify the number of days you'll be staying at your destination.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Extract data from uploaded ticket
    extract_button = st.button("Extract Data", help="Click to extract information from your ticket")
    if extract_button and pdf:
        with st.spinner('Extracting data, please wait...'):
            try:
                df = create_docs(pdf, custom_test_value)
                if df.empty:
                    st.warning("No data extracted from the provided PDF.")
                    return

                # Extract necessary information from the dataframe
                arrive = df["Arrive"][0]
                date_of_arrive = df["Date of Arrive"][0]
                days = df["Days"][0]

                # Define the city based on the arrival information
                city = define_city(arrive)
                hotels = search_hotel(f"hotel in {city} for {days} days from {date_of_arrive}")['output']
                place = planning_days(city, date_of_arrive, days)

                # Store extracted data in session state
                st.session_state['ticket_data'] = df
                st.session_state['place'] = place
                st.session_state['hotels'] = hotels

                st.success("Data extracted successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    # Display extracted ticket information
    if 'ticket_data' in st.session_state:
        st.markdown("<h2>Extracted Ticket Information:</h2>", unsafe_allow_html=True)
        st.dataframe(st.session_state['ticket_data'])
    else:
        st.info("Upload a ticket and click 'Extract Data' to see the extracted information here.")

def itinerary_page():
    # Display the itinerary page
    st.header("Planned Itinerary")
    if 'place' in st.session_state:
        place_output = st.session_state['place']
        
        # Clean up the JSON formatting
        place_output = place_output.replace("```json\n", "").replace("json", "").replace("\n```", "").replace("```", "")
        j = -1
        
        # Ensure proper JSON formatting
        if "}," not in place_output:
            for a in place_output:
                j += 1
                if len(place_output) != j + 1 and ("{" in place_output[j:]):
                    if a == '}' and place_output[j + 1] != ",":
                        place_output = place_output[:j + 1] + ',' + place_output[j + 1:]
                        j += 1
        
        place_output = "[" + place_output + "]"
        places = json.loads(place_output)

        # Display the itinerary
        for pl in places:
            for key in pl.keys():
                if isinstance(pl[key], dict):
                    st.write(key)
                    for k in pl[key].keys():
                        st.write(f"    {k}: {pl[key][k]}")
                else:
                    st.write(f"{key} : {pl[key]}")
    else:
        st.info("Please upload your ticket and extract data first.")

def hotels_page():
    # Display the hotels page
    st.header("Hotels")
    if 'hotels' in st.session_state:
        output = st.session_state['hotels']
        
        # Clean up the JSON formatting
        output = output.replace("```json\n", "").replace("\n```", "")
        i = -1
        
        # Ensure proper JSON formatting
        if "}," not in output:
            for a in output:
                i += 1
                if len(output) != i + 1:
                    if a == '}' and output[i + 1] != ",":
                        output = output[:i + 1] + ',' + output[i + 1:]
                        i += 1
        
        output = "[" + output + "]"
        hotels = json.loads(output)
        
        # Display the hotel information
        for hotel in hotels:
            for key in hotel.keys():
                st.write(f"{key} : {hotel[key]}")
    else:
        st.info("Please upload your ticket and extract data first.")

if __name__ == '__main__':
    main()
