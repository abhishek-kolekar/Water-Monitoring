import datetime
from flask import Flask, render_template, flash, redirect, request, url_for
import MySQLdb
from flask_toastr import Toastr 
from config import credential


app = Flask(__name__)

toastr = Toastr(app)

# Set the secret_key on the application to something unique and secret.
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


# home route....landing page
@app.route("/", methods = ['GET', 'POST'])
@app.route("/index", methods=["GET", "POST"])
def index():
    print("landing page running...")
    if request.method == 'POST':
        username = request.form['username']
        passwd = request.form['password']

        # credentials from config files imported
        if username == credential['name'] and passwd == credential['passwd']:
            flash('Login successful :)', 'success')
            # flash("You have successfully logged in.", 'success')    # python Toastr uses flash to flash pages
            return redirect(url_for('dashboard')) 
        else:
            flash('Login Unsuccessful. Please check username and password', 'error')

    return render_template("index.html", todayDate=datetime.date.today(), )



@app.route("/dashboard", methods=["GET"])
def dashboard():
    print(">>> dashboard running ...")
    con = MySQLdb.connect(host="sql.freedb.tech", user="freedb_rajkolekar", password="Q7j&N&&KZx%7fBD", database="freedb_watermonitoring")
    cursor = con.cursor()

    # selecting current hour data ...ie, 120 for every 30 seconds of posting
    cursor.execute(" SELECT * FROM iot_wqms_table ORDER BY id DESC LIMIT 120") 
    data = cursor.fetchall()
    data = list(data)

    print(".........Page refreshed at", datetime.datetime.now())

    # data collector
    temp_data = []
    turbidity_data = []
    ph_data = []
    waterlevel_data = []

    # collecting individual data to collectors
    for row in data:
        temp_data.append(row[2])   
        turbidity_data.append(row[3])
        ph_data.append(row[4])
        waterlevel_data.append(row[5])

    # last value added to database...current data recorded 
    last_temp_data = temp_data[0]
    last_turbidity_data = turbidity_data[0]
    last_ph_data = ph_data[0]
    last_waterlevel_data = waterlevel_data[0]

    # current sum of 1hour data rounded to 2dp
    current_temp_sum = round(sum(temp_data), 2)
    current_turbidity_sum = round(sum(turbidity_data), 2)
    current_ph_sum = round( sum(ph_data), 2 )
    current_waterlevel_sum = round( sum(waterlevel_data), 2)  
    
    # fetching 240 data from db to extract the penultimate 120 data to calculate percentage change
    cursor.execute(" SELECT * FROM iot_wqms_table ORDER BY id DESC LIMIT 240") 
    data = list(cursor.fetchall())

    # collecting individual data
    prev_temp_data = []  # collecting temp values
    prev_turbidity_data = []
    prev_ph_data = []
    prev_waterlevel_data = []
    for row in data:
        prev_temp_data.append(row[2])
        prev_turbidity_data.append(row[3])
        prev_ph_data.append(row[4])
        prev_waterlevel_data.append(row[5])

    # slicing for immediate previous 120 data 
    prev_temp_data = prev_temp_data[120:240]
    prev_temp_sum = round( sum(prev_temp_data), 2 )

    prev_turbidity_data = prev_turbidity_data[120:240]
    prev_turbidity_sum = round( sum(prev_turbidity_data), 2 )

    prev_ph_data = prev_ph_data[120:240]
    prev_ph_sum = round( sum(prev_ph_data), 2 )

    prev_waterlevel_data = prev_waterlevel_data[120:240]
    prev_waterlevel_sum = round( sum(prev_waterlevel_data), 2 )

    # temp, getting the percentage change
    temp_change = prev_temp_sum - current_temp_sum
    temp_change = round(temp_change, 2)
    percentage_temp_change = (temp_change/current_temp_sum) * 100
    percentage_temp_change = round(percentage_temp_change, 1)
    
    # ph, getting the percentage change
    ph_change = prev_ph_sum - current_ph_sum
    ph_change = round(ph_change, 2)
    percentage_ph_change = (ph_change/current_ph_sum) * 100
    percentage_ph_change = round(percentage_ph_change,1)

    # turbidity, getting the percentage change
    turbidity_change = prev_turbidity_sum - current_turbidity_sum
    turbidity_change = round(turbidity_change, 2)
    percentage_turbidity_change = (turbidity_change/current_turbidity_sum) * 100
    percentage_turbidity_change = round(percentage_turbidity_change,1)

    # waterlevel, getting the percentage change
    waterlevel_change = prev_waterlevel_sum - current_waterlevel_sum
    waterlevel_change = round(waterlevel_change, 2)
    percentage_waterlevel_change = (waterlevel_change/current_waterlevel_sum) * 100
    percentage_waterlevel_change = round(percentage_waterlevel_change,1)


    return render_template("dashboard.html", data=data, percentage_temp_change=percentage_temp_change, percentage_ph_change=percentage_ph_change, percentage_turbidity_change=percentage_turbidity_change, percentage_waterlevel_change=percentage_waterlevel_change, temp_change=temp_change, ph_change=ph_change, turbidity_change=turbidity_change, waterlevel_change=waterlevel_change, last_temp_data=last_temp_data, last_ph_data=last_ph_data, last_turbidity_data=last_turbidity_data, last_waterlevel_data=last_waterlevel_data)

# main function
if  __name__ == "__main__":
    try:
        # using local ip address and auto pick up changes
        app.run(debug=False, host='0.0.0.0')
        
        # using static ip
        # app.run(debug=True, host='192.168.43.110 ', port=5050)   # setting your own ip

    except Exception as rerun:
        print(">>> Failed to run main program : ",rerun)