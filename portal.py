import datetime
from flask import Flask
from flask import render_template
from flask import request
import psycopg2
from flask import jsonify

app = Flask(__name__)


@app.route('/')
def home():

    # Connect to the database just once, and reuse the connection to fetch the latest records for each type
    conn = psycopg2.connect("dbname=readings user=postgres")
    cur = conn.cursor()

    current_temp = get_latest_reading(cur, 'temperature')
    current_humidity = get_latest_reading(cur, 'humidity')
    current_light_level = get_latest_reading(cur, 'light')

    return render_template('home.html', temperature=current_temp, humidity=current_humidity, light_level=current_light_level)


def get_latest_reading(cur, type):
    cur.execute("select time, value from readings where type = '%s' order by time DESC LIMIT 1;" % type)
    rows = cur.fetchall()
    if len(rows) > 0:
        return rows[0]

    return '', 'N/A'


@app.route('/temperature')
def temperature():
    conn = psycopg2.connect("dbname=readings user=postgres")
    cur = conn.cursor()
    cur.execute("select time, value from readings where type = 'temperature' order by time asc;")
    rows = cur.fetchall()

    return render_template('data_page.html', rows=rows, page_title='Temperature', column_heading='Temperature (°C)', type='temperature')


@app.route('/humidity')
def humidity():
    conn = psycopg2.connect("dbname=readings user=postgres")
    cur = conn.cursor()
    cur.execute("select time, value from readings where type = 'humidity' order by time asc;")
    rows = cur.fetchall()

    return render_template('data_page.html', rows=rows, page_title='Humidity', column_heading='Humidity (g/m3)', type='humidity')


@app.route('/light_level')
def light_level():
    conn = psycopg2.connect("dbname=readings user=postgres")
    cur = conn.cursor()
    cur.execute("select time, value from readings where type = 'light' order by time asc;")
    rows = cur.fetchall()

    return render_template('data_page.html', rows=rows, page_title='Light Level', column_heading='Light (lumens)', type='light')


@app.route('/graph')
def graph_fragment():
    the_type = request.args.get('type')
    conn = psycopg2.connect("dbname=readings user=postgres")
    cur = conn.cursor()
    cur.execute("select time, value from readings where type = %s order by time asc;", (the_type,))
    rows = cur.fetchall()
    labels = []
    values = []
    for row in rows:
        labels.append(row[0].strftime('%Y-%m-%d %H:%M'))
        values.append(row[1])

    return jsonify({"labels": labels, "datasets": [{"data": values, "label": the_type}]})


app.run(host="0.0.0.0")
