from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Function to get the property data from the sale listing URL
def get_sale_property_data(property_url):
    response = requests.get(property_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract sale price - you need to inspect the HTML to find the right tag/class
    sale_price_tag = soup.find('span', {'class': 'sale-price-class'})  # Adjust the class to the site you're scraping
    sale_price = int(re.sub('[^0-9]', '', sale_price_tag.text))  # Removing non-numeric characters for price

    # Extract location (just an example, modify accordingly)
    location_tag = soup.find('span', {'class': 'location-class'})
    location = location_tag.text.strip()

    return sale_price, location

# Function to find rental properties in the area and calculate the average rental price
def get_rental_properties(location):
    rental_url = f'https://www.example.com/rentals/{location}'  # Construct rental URL (site-dependent)
    response = requests.get(rental_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    rental_prices = []
    
    # Find all rental listings in the area
    rental_tags = soup.find_all('span', {'class': 'rental-price-class'})  # Modify based on the site
    for tag in rental_tags:
        rental_price = int(re.sub('[^0-9]', '', tag.text))
        rental_prices.append(rental_price)
    
    # Calculate the average rental price
    if rental_prices:
        avg_rent = sum(rental_prices) / len(rental_prices)
        return avg_rent
    else:
        return None

# Function to calculate the rental yield
def calculate_rental_yield(property_url):
    sale_price, location = get_sale_property_data(property_url)
    
    # Get the average rental price for the location
    avg_rent = get_rental_properties(location)
    
    if avg_rent:
        # Calculate the annual rent (monthly rent * 12)
        annual_rent = avg_rent * 12
        
        # Calculate the rental yield
        rental_yield = (annual_rent / sale_price) * 100
        return rental_yield
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    property_url = request.form['property_url']
    rental_yield = calculate_rental_yield(property_url)
    if rental_yield:
        return jsonify({'rental_yield': rental_yield})
    else:
        return jsonify({'error': 'Unable to calculate rental yield.'})

if __name__ == '__main__':
    app.run(debug=True)
