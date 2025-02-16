import requests
from bs4 import BeautifulSoup
import csv
import json
import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Web Scraper Class
class WebScraper:
    def __init__(self, url):
        self.url = url
        self.data = []

    def fetch_data(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an error for bad status codes
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.RequestException as e:
            print(f"Error fetching the URL: {e}")
            logging.error(f"Error fetching the URL: {e}")
            return None

    def extract_data(self, soup):
        # Example: Extract headlines and links from a news website
        headlines = soup.find_all('h2')  # Adjust based on the website's structure
        for headline in headlines:
            title = headline.text.strip()
            link = headline.find('a')['href'] if headline.find('a') else 'No link'
            self.data.append({'title': title, 'link': link})

    def save_to_csv(self, filename):
        if not self.data:
            print("No data to save.")
            return
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'link'])
            writer.writeheader()
            writer.writerows(self.data)
        print(f"Data saved to {filename}")
        logging.info(f"Data saved to {filename}")

    def save_to_json(self, filename):
        if not self.data:
            print("No data to save.")
            return
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4)
        print(f"Data saved to {filename}")
        logging.info(f"Data saved to {filename}")

# Calculator Class
class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero!")
        return a / b

    def log_operation(self, operation, result):
        self.history.append((operation, result))
        logging.info(f"Operation: {operation}, Result: {result}")

    def save_history_to_db(self):
        conn = sqlite3.connect('calculator_history.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS history
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           operation TEXT,
                           result REAL)''')
        for operation, result in self.history:
            cursor.execute("INSERT INTO history (operation, result) VALUES (?, ?)", (operation, result))
        conn.commit()
        conn.close()
        print("History saved to database.")
        logging.info("History saved to database.")

# Main Application
def main():
    print("Welcome to the Multi-Functional Application!")
    while True:
        print("\nChoose an option:")
        print("1. Web Scraper")
        print("2. Calculator")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            # Web Scraper
            url = input("Enter the URL to scrape: ")
            output_format = input("Choose output format (csv/json): ").strip().lower()
            if output_format not in ['csv', 'json']:
                print("Invalid format. Defaulting to CSV.")
                output_format = 'csv'

            scraper = WebScraper(url)
            soup = scraper.fetch_data()
            if soup:
                scraper.extract_data(soup)
                output_dir = 'output'
                os.makedirs(output_dir, exist_ok=True)
                if output_format == 'csv':
                    scraper.save_to_csv(os.path.join(output_dir, 'data.csv'))
                elif output_format == 'json':
                    scraper.save_to_json(os.path.join(output_dir, 'data.json'))

        elif choice == '2':
            # Calculator
            calc = Calculator()
            try:
                num1 = float(input("Enter the first number: "))
                num2 = float(input("Enter the second number: "))
                operation = input("Choose operation (add/subtract/multiply/divide): ").strip().lower()

                if operation == 'add':
                    result = calc.add(num1, num2)
                elif operation == 'subtract':
                    result = calc.subtract(num1, num2)
                elif operation == 'multiply':
                    result = calc.multiply(num1, num2)
                elif operation == 'divide':
                    result = calc.divide(num1, num2)
                else:
                    print("Invalid operation!")
                    continue

                print(f"Result: {result}")
                calc.log_operation(f"{num1} {operation} {num2}", result)

                save_to_db = input("Save history to database? (yes/no): ").strip().lower()
                if save_to_db == 'yes':
                    calc.save_history_to_db()

            except ValueError as e:
                print(f"Error: {e}")
                logging.error(f"Error: {e}")

        elif choice == '3':
            print("Exiting the application. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
