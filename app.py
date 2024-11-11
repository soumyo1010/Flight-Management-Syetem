import streamlit as st
import sqlite3
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Database path
db_name = 'airline_50.db'

# Database query function
def run_query(query, parameters=()):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, parameters)
        conn.commit()
    return result

# Add Passenger Information
def add_passenger(pid, name, age, sex, address, contact, email):
    if name and age and sex and address and contact and email:
        query = 'INSERT INTO passenger (pid, name, age, sex, address, contact, email) VALUES (?, ?, ?, ?, ?, ?, ?)'
        parameters = (pid, name, age, sex, address, contact, email)
        run_query(query, parameters)
        st.success("Passenger data added successfully!")
    else:
        st.error("Please fill all fields!")

# Fetch Available Flights
def get_available_flights():
    query = "SELECT flight_id, departure_place, departure_time, destination, arrival_time FROM flights"
    return run_query(query).fetchall()

# Book a Ticket
def book_ticket(pid, selected_flight):
    if selected_flight:
        query = 'INSERT INTO bookings (pid, flight_id, booking_date) VALUES (?, ?, ?)'
        parameters = (pid, selected_flight, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        run_query(query, parameters)
        st.success("Flight booked successfully!")
    else:
        st.error("Please select a flight to book.")

# Fetch Booking Details for Boarding Pass
def get_booking_details(pid):
    query = """
    SELECT p.name, f.destination, f.departure_time, f.arrival_time, f.flight_id
    FROM passenger p
    JOIN bookings b ON p.pid = b.pid
    JOIN flights f ON b.flight_id = f.flight_id
    WHERE p.pid = ?
    """
    result = run_query(query, (pid,)).fetchone()
    return result if result else None

# Generate Boarding Pass
def generate_boarding_pass(name, flight_from, flight_to, flight_id, date, time):
    image = Image.new('RGB', (570, 230), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Define colors and font
    header_color = (237, 27, 36)
    text_color = (0, 0, 0)
    font = ImageFont.load_default()

    # Draw header and text
    draw.rectangle([(0, 0), (570, 40)], fill=header_color)
    draw.text((285, 10), "Boarding Pass", fill=(255, 255, 255), anchor="mm")
    draw.text((20, 60), f"Passenger Name: {name}", fill=text_color)
    draw.text((20, 100), f"From: {flight_from}", fill=text_color)
    draw.text((20, 140), f"To: {flight_to}", fill=text_color)
    draw.text((300, 100), f"Flight: {flight_id}", fill=text_color)
    draw.text((300, 140), f"Date: {date}", fill=text_color)
    draw.text((300, 180), f"Time: {time}", fill=text_color)

    return image

# Streamlit App Layout
st.title("Flight Management System")

# Passenger Information
st.header("Enter Passenger Details")
pid = st.text_input("Passenger ID")
name = st.text_input("Name")
age = st.number_input("Age", min_value=1, max_value=120, step=1)
sex = st.selectbox("Sex", ["Male", "Female", "Other"])
address = st.text_input("Address")
contact = st.text_input("Contact")
email = st.text_input("Email")

if st.button("Add Passenger"):
    add_passenger(pid, name, age, sex, address, contact, email)

# Flight Booking
st.header("Book a Flight")
flights = get_available_flights()
flight_options = {
    f"Flight ID: {flight[0]}, From: {flight[1]} at {flight[2]}, To: {flight[3]} at {flight[4]}": flight[0]
    for flight in flights
}
selected_flight = st.selectbox("Available Flights", list(flight_options.keys()))

if st.button("Book Ticket"):
    book_ticket(pid, flight_options[selected_flight])

# Boarding Pass Generation
st.header("Generate Boarding Pass")
if st.button("Generate Boarding Pass"):
    booking_details = get_booking_details(pid)
    if booking_details:
        name, destination, departure_time, arrival_time, flight_id = booking_details
        date = datetime.strptime(departure_time, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
        time = datetime.strptime(departure_time, "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p")

        # Generate and display boarding pass
        boarding_pass_image = generate_boarding_pass(name, "BOM", destination, f"AI {flight_id}", date, time)
        st.image(boarding_pass_image, caption="Boarding Pass")

        # Save boarding pass image as downloadable file
        boarding_pass_image_path = f"{pid}_boarding_pass.png"
        boarding_pass_image.save(boarding_pass_image_path)
        with open(boarding_pass_image_path, "rb") as file:
            st.download_button(label="Download Boarding Pass", data=file, file_name=boarding_pass_image_path, mime="image/png")
    else:
        st.error("No booking found for the given Passenger ID.")
