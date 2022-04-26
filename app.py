import re
from flask import Flask, render_template, request, redirect, session, flash, url_for,send_file
from functools import wraps
from flask_mysqldb import MySQL
import folium
import geocoder
import openrouteservice
from jedi.plugins import flask
from openrouteservice import convert
import requests
import urllib.parse
import os
import geopy.distance




app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'taxi_booking_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route("/")
@app.route("/index")
def Homepage():
    return render_template("index.html", feedback="False")

# Login

@app.route('/driverlogin', methods=['POST', 'GET'])
def driverlogin():
    status = True
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["upass"]
        cur = mysql.connection.cursor()
        cur.execute(
            "select * from driver where EMAIL=%s and UPASS=%s", (email, pwd))
        data = cur.fetchone()
        if data:
            session['logged_in'] = True
            session['username'] = data["UNAME"]
            session['id'] = data["UID"]
            flash('Login Successfully', 'success')
            return redirect('driverhome')
        else:
            flash('Invalid Login. Try Again', 'danger')
    return render_template("driverlogin.html")


@app.route('/userlogin', methods=['POST', 'GET'])
def userlogin():
    status = True
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["upass"]
        cur = mysql.connection.cursor()
        cur.execute(
            "select * from users where EMAIL=%s and UPASS=%s", (email, pwd))
        data = cur.fetchone()
        if data:
            session['logged_in'] = True
            session['username'] = data["UNAME"]
            session['id'] = data["UID"]
            flash('Login Successfully', 'success')
            return redirect('userhome')
        else:
            flash('Invalid Login. Try Again', 'danger')
    return render_template("userlogin.html")

# check if driver logged in


def is_driverlogged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login', 'danger')
            return redirect(url_for('driverlogin'))
    return wrap

# check if user logged in


def is_userlogged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login', 'danger')
            return redirect(url_for('userlogin'))
    return wrap


# Registration
@app.route('/driverreg', methods=['POST', 'GET'])
def driverreg():
    status = False
    if request.method == 'POST':
        name = request.form["uname"]
        email = request.form["email"]
        pwd = request.form["upass"]
        contact = request.form["contact"]
        cur = mysql.connection.cursor()
        cur.execute("insert into driver(UNAME,UPASS,EMAIL,CONTACT) values(%s,%s,%s,%s)",
                    (name, pwd, email, contact))
        mysql.connection.commit()
        cur.close()
        flash('Registration Successfully. Login Here...', 'success')
        return redirect('driverlogin')
    return render_template("driverreg.html", status=status)

# Registration


@app.route('/userreg', methods=['POST', 'GET'])
def userreg():
    status = False
    if request.method == 'POST':
        name = request.form["uname"]
        email = request.form["email"]
        pwd = request.form["upass"]
        contact = request.form["contact"]
        cur = mysql.connection.cursor()
        cur.execute("insert into users(UNAME,UPASS,EMAIL,CONTACT) values(%s,%s,%s,%s)",
                    (name, pwd, email, contact))
        mysql.connection.commit()
        cur.close()
        flash('Registration Successfully. Login Here...', 'success')
        return redirect('userlogin')
    return render_template("userreg.html", status=status)

# Home page


@app.route("/driverhome")
@is_driverlogged_in
def driverhome():
    return render_template('driverhome.html')

@app.route("/driverloc",methods=['POST','GET'])
@is_driverlogged_in
def driverloc():
    if request.method == 'POST':
        source = request.form["source"]
        url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(source) + '?format=json'
        response_src = requests.get(url).json()

        print(response_src[0]["lat"])
        print(response_src[0]["lon"])


        cur = mysql.connection.cursor()
        wait="waiting"
        cur.execute("SELECT * FROM user_booking where status=%s",[wait])
        data = cur.fetchall()
        print(len(data))
        print(data)
        result=[]
        for i in range(len(data)):
            url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(data[0]['source']) + '?format=json'
            response_dest = requests.get(url).json()

            print(response_dest[0]["lat"])
            print(response_dest[0]["lon"])

            coords_1 = (response_src[0]["lat"],response_src[0]["lon"] )
            coords_2 = (response_dest[0]["lat"], response_dest[0]["lon"])

            if (geopy.distance.geodesic(coords_1, coords_2))<=25:
                result.append(data[i])

    print(result)
    return render_template('availusers.html',result=result,len=len(result))


@app.route("/conformride",methods=['POST','GET'])
@is_driverlogged_in
def conformride():
    if request.method == 'POST':
        uid = request.form["uid"]
        ubookid=request.form["ubookid"]

        cur = mysql.connection.cursor()
        cur.execute("update user_booking  set status=%s where uid=%s and ubookid=%s",
                    ("booked",uid, ubookid))
        mysql.connection.commit()
        cur.close()
        print(uid,ubookid)
        print(session['id'])
        cur = mysql.connection.cursor()
        import random
        number = random.randint(1000, 9999)
        cur = mysql.connection.cursor()
        cur.execute(
            "select * from user_driver where ubookid=%s and uid=%s", (ubookid, uid))
        data = cur.fetchone()
        if data:
            pass
        else:
            cur.execute("insert into user_driver(uid,ubookid,did,otp_pin) values(%s,%s,%s,%s)",
                    (uid, ubookid, session['id'], number))
        mysql.connection.commit()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute(
            "select * from users where uid=%s", ( uid))
        data = cur.fetchone()
        print(data)


    return render_template('verifyuser.html',data=data,uid=uid,ubookid=ubookid)
# Home page


@app.route("/journeystarts",methods=['POST','GET'])
@is_driverlogged_in
def journeystarts():
    if request.method == 'POST':
        uid = request.form["uid"]
        ubookid=request.form["ubookid"]
        otp = request.form["otp"]
        cur = mysql.connection.cursor()
        cur.execute(
            "select * from user_driver where ubookid=%s and uid=%s", (ubookid, uid))
        data = cur.fetchone()
        # print(type(data['otp_pin']),type(otp))
        if int(otp)==data['otp_pin']:
            cur = mysql.connection.cursor()
            cur.execute("update user_driver  set verify=%s , journey_status=%s where uid=%s and ubookid=%s",
                        ("yes",'started', uid, ubookid))
            mysql.connection.commit()
            return render_template('journeystarteddriver.html',uid=uid,ubookid=ubookid);
        cur.execute(
            "select * from users where uid=%s", (uid))
        data = cur.fetchone()
    flash("INVALID OTP","danger")
    return render_template('verifyuser.html',data=data,uid=uid,ubookid=ubookid)

@app.route("/endride",methods=['POST','GET'])
@is_driverlogged_in
def endride():
    if request.method == 'POST':
        uid = request.form["uid"]
        ubookid=request.form["ubookid"]
        cur = mysql.connection.cursor()
        cur.execute("update user_driver  set completed=%s  where uid=%s and ubookid=%s",
                    ("yes", uid, ubookid))
        mysql.connection.commit()
        flash("ride completed successfully","success")
        return  render_template('driverhome.html')


@app.route('/userhome',methods=['POST','GET'])
@is_userlogged_in
def userhome():
    if os.path.exists("templates/mapsrcdest.html"):
        os.remove("templates/mapsrcdest.html")
        print("The file has been deleted successfully")
    else:
        print("The file does not exist!")
    return render_template('userhome.html')
# logout

@app.route('/usersrcdest',methods=['POST','GET'])
@is_userlogged_in
def usersrcdest():
    if request.method == 'POST':
        source = request.form["source"]
        dest = request.form["destination"]

        # lat=request.form["lat"]
        # long=request.form["long"]
        print(source, dest)

    if source!="" and dest!="":
        url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(source) + '?format=json'
        response_src = requests.get(url).json()

        print(response_src[0]["lat"])
        print(response_src[0]["lon"])

        url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(dest) + '?format=json'
        response_dest = requests.get(url).json()

        print(response_dest[0]["lat"])
        print(response_dest[0]["lon"])
        g = geocoder.ip('me')

        client = openrouteservice.Client(key='5b3ce3597851110001cf6248ef6af4cfbd7147f18189b7aded6b4e64')
        coords = ((response_src[0]["lon"], response_src[0]["lat"]), (response_dest[0]["lon"], response_dest[0]["lat"]))
        res = client.directions(coords)


        # call API

        # test our response

        geometry = client.directions(coords)['routes'][0]['geometry']
        decoded = convert.decode_polyline(geometry)

        distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>" + str(
            round(res['routes'][0]['summary']['distance'] / 1000, 1)) + " Km </strong>" + "</h4></b>"
        duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>" + str(
            round(res['routes'][0]['summary']['duration'] / 60, 1)) + " Mins. </strong>" + "</h4></b>"
        m = folium.Map(location=[response_src[0]["lat"], response_src[0]["lon"]], zoom_start=10, control_scale=True,
                       tiles="cartodbpositron",width='100%',height='50%')

        # county_path = os.path.join(os.getcwd(),'data', 'test.json')
        # county_geojson = json.load(open(county_path))
        # folium.GeoJson(decoded).add_child(folium.Popup(distance_txt + duration_txt,max_width=300)).add_to(m)

        # folium.GeoJson(
        #     # decoded
        #      county_geojson,
        #     name='geojson'
        #     ).add_to(m)

        # folium.GeoJson.add_child(folium.Popup(distance_txt+duration_txt,max_width=300)).add_to(m)
        folium.GeoJson(decoded).add_child(folium.Popup(distance_txt + duration_txt, max_width=300)).add_to(m)

        folium.Marker(
            location=list(coords[0][::-1]),
            popup=source,
            icon=folium.Icon(color="green"),
        ).add_to(m)

        folium.Marker(
            location=list(coords[1][::-1]),
            popup=dest,
            icon=folium.Icon(color="red"),
        ).add_to(m)

        m.save('templates/mapsrcdest.html')
        # iframe='templates/mapsrcdest.html'
        # return m._repr_html_()

    distance_txt=str(round(res['routes'][0]['summary']['distance'] / 1000, 1)) + "KM"
    duration_txt=str(round(res['routes'][0]['summary']['duration'] / 60, 1)) + "MINS"
    cost=round(res['routes'][0]['summary']['distance'] / 1000, 1)*4;
    print(distance_txt,duration_txt)
    list_send=[]
    list_send.append(source)
    list_send.append(dest)
    list_send.append(duration_txt)
    list_send.append(distance_txt)
    list_send.append(str(cost)+"RS")

    return render_template('usersrcdest.html',ls=list_send)

@app.route('/userbooking',methods=['POST','GET'])
@is_userlogged_in
def userbooking():
    if request.method == 'POST':
        source = request.form["source"]
        dest = request.form["dest"]
        dist = request.form["dist"]
        time = request.form["time"]
        cost= request.form["cost"]
        cost = (cost.replace("RS", ""))
        cost=(int(float(cost)))
        dist = (dist.replace("KM", ""))
        dist = ((float(dist)))
        print(source,dest,dist,time,cost,session['id'])
        cur = mysql.connection.cursor()
        cur.execute("insert into user_booking(source,destination,cost,distance,uid) values(%s,%s,%s,%s,%s)",
                    (source,dest,cost,dist,session['id']))
        mysql.connection.commit()
        userbid = cur.lastrowid
        print(userbid)

        cur.close()

        flash('Booked Successfully', 'success')

    return render_template('userwaiting.html',userbid=userbid)


@app.route('/bookstatus',methods=['POST','GET'])
@is_userlogged_in
def bookstatus():
    if request.method == 'POST':
        userbid = request.form["userbid"]
        cur = mysql.connection.cursor()
        cur.execute("select status from user_booking where ubookid="+userbid)
        data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        print(data[0]['status'])
        if (data[0]['status'])=='booked':
            print(session['username'])
            cur = mysql.connection.cursor()
            cur.execute(
                "select * from user_driver where uid=%s and ubookid=%s ", (session['id'],userbid))
            data = cur.fetchone()
            print(data)
            driverdetails=str(data['did'])
            print(driverdetails)
            otp=data['otp_pin']
            cur = mysql.connection.cursor()
            cur.execute("select * from driver where UID=%s", [driverdetails])
            data = cur.fetchone()

            cur.execute("select * from user_booking where ubookid=%s", [userbid])
            travel= cur.fetchone()
            cur.close()
            # cur = mysql.connection.cursor()
            # cur.execute(
            #     "select * from drivers where uid=%s", (uid))
            # data = cur.fetchone()
            return render_template('verifydriver.html',data=data,otp=otp,uid=session['id'],userbid=userbid,travel=travel,did=driverdetails)
        print(userbid)


    return render_template('userwaiting.html',userbid=userbid)



@app.route('/journeybegin',methods=['POST','GET'])
@is_userlogged_in
def journeybegin():
    if request.method == 'POST':
        uid = request.form["uid"]
        ubookid = request.form["ubookid"]
        did=request.form["did"]
        otp = request.form["otp"]

        cur = mysql.connection.cursor()
        cur.execute("select * from user_driver where ubookid=%s and uid=%s", (ubookid, uid))
        data = cur.fetchone()
        if data['verify']=="yes" and data["journey_status"]=="started":
            return render_template('journeybeginsuser.html',ubookid=ubookid,uid=uid)
        cur = mysql.connection.cursor()
        cur.execute("select * from driver where UID=%s", [did])
        data = cur.fetchone()
        cur.execute("select * from user_booking where ubookid=%s", [ubookid])
        travel = cur.fetchone()
        cur.close()
    return render_template('verifydriver.html',data=data,otp=otp,uid=session['id'],userbid=ubookid,travel=travel,did=did)



@app.route('/endjourney',methods=['POST','GET'])
@is_userlogged_in
def endjourney():
    if request.method == 'POST':
        uid = request.form["uid"]
        ubookid = request.form["ubookid"]
        cur = mysql.connection.cursor()
        cur.execute("select * from user_driver where uid=%s and ubookid=%s", (uid,ubookid))
        data = cur.fetchone()
        if data['completed']=="yes":
            flash("Ride completed Successfull","success")
            return render_template('driverhome.html')
        return render_template('journeybeginsuser.html',ubookid=ubookid,uid=uid)




@app.route('/templates/mapsrcdest.html')
def show_map():
    return send_file('templates/mapsrcdest.html')


@app.route("/driverlogout")
def driverlogout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('driverlogin'))

# logout


@app.route("/userlogout")
def userlogout():
    # print(userbid)
    # if(userbid!=0):
    #     cur = mysql.connection.cursor()
    #     s='declined'
    #     cur.execute("update user_booking set status="+s+" where ubookid="+userbid)
    #     print("declined")
    #     mysql.connection.commit()
    #     cur.close()

    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('userlogin'))


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.secret_key = 'secret'
    app.run(debug=True)
