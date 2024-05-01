from flask import Flask, render_template, request, jsonify
import requests
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
import google.generativeai as genai
from forex_python.converter import CurrencyRates
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import geocoder


app = Flask(__name__)

# Configure Google API key
GOOGLE_API_KEY = 'Enter Key'
genai.configure(api_key=GOOGLE_API_KEY)

# Connect to MySQL
try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Password",
        database="Database name"
    )
    if connection.is_connected():
        cursor = connection.cursor()

except Error as e:
    print("Error while connecting to MySQL", e)

# Functions
def get_location_by_ip():
    try:
        location = geocoder.ip('me')
        if location.ok:
            city = location.city
            country = location.country
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("SELECT id FROM app_history ORDER BY id DESC LIMIT 1")
            last_id = cursor.fetchone()[0]
            values_to_insert = (current_time, city,last_id)
            sql_insert_query ="INSERT INTO location_history (id, time, location) SELECT id, %s, %s FROM app_history WHERE id = %s"
            cursor.execute(sql_insert_query, values_to_insert)
            connection.commit()
            return city, country
        else:
            print("Failed to get device location.")
            return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

city, country = get_location_by_ip()




#App Routes:
@app.route('/', methods=['GET', 'POST'])
def default_route():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    values_to_insert = (current_time,)
    sql_insert_query = "INSERT INTO app_history (time) VALUES (%s)"
    cursor.execute(sql_insert_query, values_to_insert)
    connection.commit()
    return render_template('index.html')


@app.route('/Expense', methods=['GET', 'POST'])
def expense():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    application = "Expense"
    cursor.execute("SELECT id FROM app_history ORDER BY id DESC LIMIT 1")
    last_id = cursor.fetchone()[0]
    values_to_insert = (last_id, current_time, application)
    sql_insert_query = "INSERT INTO in_app_history (id, time, in_app_history) VALUES (%s, %s, %s)"
    cursor.execute(sql_insert_query, values_to_insert)
    connection.commit()
    if request.method == 'POST':
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        category = request.form.get("category")
        amount = float(request.form.get("amount"))
        cursor.execute("SELECT id FROM app_history ORDER BY id DESC LIMIT 1")
        values_to_insert = (current_time, category, amount)
        sql_insert_query = "INSERT INTO expense (id, time, category, amount) VALUES ((SELECT id FROM app_history ORDER BY id DESC LIMIT 1), %s, %s, %s)"
        cursor.execute(sql_insert_query, values_to_insert)
        connection.commit()
        return render_template('expense.html',msg="Record Added Successfully")
    else:
        return render_template('expense.html')


@app.route('/Currency', methods=['GET', 'POST'])
def currency():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    application = "Currency"
    cursor.execute("SELECT id FROM app_history ORDER BY id DESC LIMIT 1")
    last_id = cursor.fetchone()[0]
    values_to_insert = (last_id, current_time, application)
    sql_insert_query = "INSERT INTO in_app_history (id, time, in_app_history) VALUES (%s, %s, %s)"
    cursor.execute(sql_insert_query, values_to_insert)
    if request.method == 'POST':
        amount = float(request.form['amount'])
        from_currency = request.form['from_currency']
        to_currency = request.form['to_currency']
        print("amount: ",amount)
        # Functionality of curncy_convrt integrated within the route
        try:
            cr = CurrencyRates()
            rate = cr.get_rate(from_currency, to_currency)
            print(rate)
            conversion = rate * amount
            result =conversion,"@rate: ",rate
            result=str(result)
            result=result.replace("(","").replace(")","").replace("'","").replace(",","")
            cursor.execute("SELECT id FROM app_history ORDER BY id DESC LIMIT 1")
            last_id = cursor.fetchone()[0]
            values_to_insert = (last_id, from_currency, to_currency)
            sql_insert_query = "INSERT INTO currency_converter (id,source_currency_code, target_currency_code) VALUES (%s, %s)"
            cursor.execute(sql_insert_query, values_to_insert)
            connection.commit()
            return render_template('currency.html', result=result)
        except:
            return render_template('currency.html', result="ERROR OCCURED!<br> Can be the following reasons:<br>1. API Key Usage Exhausted<br>2. You are not connected to the web<br>3. API not functional")
    
    return render_template('currency.html')


@app.route('/Translator', methods=['GET', 'POST'])
def translator():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    application = "Translator"
    cursor.execute("SELECT id FROM app_history ORDER BY id DESC LIMIT 1")
    last_id = cursor.fetchone()[0]
    values_to_insert = (last_id, current_time, application)
    sql_insert_query = "INSERT INTO in_app_history (id, time, in_app_history) VALUES (%s, %s, %s)"
    cursor.execute(sql_insert_query, values_to_insert)
    if request.method == 'POST':
        statement = request.form.get("text")
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"you are a translator, translate the following statement to hindi\nRULES:\n1. Use the info about the state the city is in and convert to the major language spoken in the state\n2. keep the dialect in English for easy reading\n3. You will only translate and give that answer\n4. Just generate the translation, nothing else apart from it\n5. keep discrete about any other information apart from translation\n6. Use correct grammar and the names and their spelling should remain same\n\nExample if the text is 'my name is abc' and if the target language is hindi it should convert to 'Mera naam abc hain'. Statement: {statement}"
        response = model.generate_content(prompt)
        
        if response.candidates:
            translated_text = response.text
        else:
            translated_text = "Translation not available"

        return render_template('translator.html', translated_text=translated_text)
    else:
        return render_template('translator.html', translated_text=None)

@app.route('/Places')
def show_places():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    application = "Places"
    cursor.execute("SELECT id FROM app_history ORDER BY id DESC LIMIT 1")
    last_id = cursor.fetchone()[0]
    values_to_insert = (last_id, current_time, application)
    sql_insert_query = "INSERT INTO in_app_history (id, time, in_app_history) VALUES (%s, %s, %s)"
    cursor.execute(sql_insert_query, values_to_insert)
    model = genai.GenerativeModel('gemini-pro')
    prompt2 = f'Suggest me good places near or in the {city} the results should be based on the weather condition, time of the day. The result should be text only and made in points'
    response = model.generate_content(prompt2)
    response = response.text
    response = response.split("**")
    response = str(response)
    response = response.split("*")
    response = str(response)
    response = response.replace('[', '').replace(']', '').replace(',', '').replace('\\n', '<br>').replace("'", '').replace('"', '').replace('/', '').replace('\\', '')
    print(response)
    return render_template('places.html', places_text=response)

if __name__ == '__main__':
    app.run(debug=True)
