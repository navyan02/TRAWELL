import streamlit as st
import google.generativeai as palm
import os
from ics import Calendar, Event
from datetime import datetime, timedelta
import json

# Configure page settings
st.set_page_config(page_title="TRAWELL", page_icon="🌏", layout="wide")

# Add Image to sidebar
with st.sidebar:
    st.image("TraWell.png", width=300)
    st.markdown("---")
    st.markdown("Welcome to **TRAWELL**")
    st.markdown("A personalized weekend getaway itinerary generator for all your traveling wants and needs!")
    st.markdown("---")
    st.markdown("Enter your preferences on the sidebar and get ready for an amazing trip!")
    st.markdown("Happy Traveling!")

# Add custom CSS for the main layout and header
st.markdown("""
    <style>
        body {
            background-color: #FFFBF3; /* Set background color */
        }
        .main {
            max-width: 1500px;
            padding: 3rem;
        }
        .header-container {
            background-color: #7295C6; /* Background color */
            padding: 30px; /* Add some padding for spacing */
            border-radius: 5px; /* Add rounded corners */
            text-align: center; /* Center-align the text */
            margin-bottom: 2rem; /* Add margin to separate from other content */
        }
        .sidebar .sidebar-content {
            background-color: #7C99BB; /* Lighter Blue for sidebar */
        }
        @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap');
        .fancy-font {
            font-family: 'Times New Roman', sans-serif;
            font-size: 36px;
            color: #C7D3DC; /* Font color */
        }
    </style>
""", unsafe_allow_html=True)

# Add styled header
st.markdown("<div class='header-container'>"
            "<h1 class='fancy-font'>Plan Your Weekend Getaway with TRAWELL</h1>"
            "</div>", unsafe_allow_html=True)

# Add description
st.write("TRAWELL is here to help you plan your next weekend getaway with ease. "
         "Simply select your preferences below and let TRAWELL generate a personalized itinerary "
         "tailored to your needs. Whether you're looking for adventure, relaxation, or cultural experiences, "
         "TRAWELL has you covered. Start planning your perfect trip today!")

# Add additional header
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap');
        .fancy-font {
            font-family: 'Bellaza', cursive;
            font-size: 50px;
            color: #0C274E;
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("<h1 class='fancy-font'>Where to?</h1>", unsafe_allow_html=True)



palm.configure(api_key=os.getenv("PALM_API_KEY"))
models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name


city = st.text_input("Which city do you want to visit?:")
days = st.number_input("Enter the duration of your trip:", min_value=1, max_value=4, step=1)
days = int(days)
budget = st.slider("Select your budget", min_value=0, max_value=1000, step=50)
budget = int(budget)
people = st.slider("Select the number of people coming", min_value=1, max_value=10, step=1)
people = int(people)


# User preferences checkboxes
st.text("Which 3 are most important to you?")
art = st.checkbox("Art 🎨")
music = st.checkbox("Music 🎵")
food = st.checkbox("Food 🍴")
indoor = st.checkbox("Indoor Activities")
nature = st.checkbox("Nature 🌿")
sports = st.checkbox("Sports 🏈")
acc = st.checkbox("Accessibility accommodations available ♿")


itinerary_json = None  # Define the variable outside the button click condition


# Generate itinerary button
if st.button("Generate Itinerary"):
    # Create a prompt based on user input
    prompt = f"""You are a travel expert. Give me an itinerary for {city}, for {days} days, with reasonable timings for each day. Ensure the total budget for {people} people is within {budget}. I like """
    if art:
        prompt += " art,"
    if music:
        prompt += " music,"
    if food:
        prompt += " food,"
    if indoor:
        prompt += " exploring indoor activities,"
    if nature:
        prompt += " nature,"
    if sports:
        prompt += " sports,"
    if acc:
        prompt += " exploring areas that have accessibility accommodations,"


    prompt += """Limit the length of the output json string to 10000 characters. Generate a structured JSON representation for the travel itinerary.


    {
  "days": [
    {
      "day": 1,
      "activities": [
        {
          "title": "Activity 1",
          "description": "Description of Activity 1",
          "link": "https://example.com/activity1",
          "start": "10:00 AM",
          "end": "12:00 PM",
          "location": "https://maps.google.com/?q=location1",
          "cost": "price for Activity 1",
          "accessibility": "Overall ranking and type of accommodations available for Activity 1"
        },
        {
          "title": "Activity 2",
          "description": "Description of Activity 2",
          "link": "https://example.com/activity2",
          "start": "02:00 PM",
          "end": "04:00 PM",
          "location": "https://maps.google.com/?q=location2",
          "cost": "price for Activity 2",
          "accessibility": "Overall ranking and type of accommodations available for Activity 2"
        }
      ]
    }
  ]
}


    """


    # Call the OpenAI API
    try:
        completion = palm.generate_text(
            model=model,
            prompt=prompt,
            temperature=0,
            max_output_tokens=50000,
        )

        if completion.result is None:
            st.error("Failed to generate itinerary. Please try again.")
        else:
            itinerary = completion.result.strip()
            #st.write("Debugging: Response from API:")
            #st.write(itinerary)
            itinerary = itinerary[7:-3]
            try:
                itinerary_json = json.loads(itinerary)
            except json.JSONDecodeError as e:
                st.error("An error occurred. Please try again.")
    except Exception as e:
        st.error("An error occurred. Please try again.")
        st.error(str(e))


# Display the itinerary
if itinerary_json:
    for day in itinerary_json["days"]:
        st.header(f"Day {day['day']}")
        for activity in day["activities"]:
            st.subheader(activity["title"])
            st.write(f"Description: {activity.get('description', 'No description available')}")
            st.write(f"Location: {activity.get('location', 'No Location available')}")
            st.write(f"Link: {activity.get('link', 'No link available')}")
            st.write(f"Time: {activity.get('start')} - {activity.get('end')}")
            # Calculate the cost for the number of people. 
            if 'cost' in activity and activity['cost'].strip().lower() == 'free':
                total_cost = 0
            else:
                try:
                    activity_cost = int(activity['cost'].split()[0].replace('$', ''))
                    total_cost = activity_cost * people
                except ValueError:
                    total_cost = 'Varies'
            st.write(f"Cost for {people} people: ${total_cost}")
            if acc:
                st.write(f"Accessibility rating: {activity.get('accessibility', 'No accessibility information')}")
            else:
                pass
            st.write("\n")

def export_to_icloud(itinerary_json):
    cal = Calendar()
    
    # Loop through each day in the itinerary
    for day in itinerary_json["days"]:
        for activity in day["activities"]:
            # Extract activity details
            title = activity["title"]
            start_time = datetime.strptime(activity["start"], "%I:%M %p")
            end_time = datetime.strptime(activity["end"], "%I:%M %p")
            description = activity.get("description", "No description available")
            location = activity.get("location", "No location available")
            
            # Create event
            event = Event()
            event.name = title
            event.begin = start_time
            event.end = end_time
            event.description = description
            event.location = location
            
            # Add event to calendar
            cal.events.add(event)
    
    # Save calendar to .ics file
    file_path = "itinerary.ics"
    with open(file_path, "w") as f:
        f.writelines(cal)
    
    return file_path

# Button to export to iCloud calendar
if itinerary_json:
    if st.button("Export to iCloud Calendar"):
        file_path = export_to_icloud(itinerary_json)
        st.success(f"Download the itinerary file [here](data:file/ics;base64,{file_path})")
