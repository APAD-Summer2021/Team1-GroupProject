import urllib
from bson import ObjectId
from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify, Blueprint
import pymongo
import bcrypt
import datetime
import gridfs
import codecs
import re
import json
from urllib.request import urlopen
import googlemaps
import certifi
import requests
import sys


app = Flask(__name__)
app.secret_key = "PetHavenAPAD"

client = pymongo.MongoClient("mongodb+srv://MSITM_User:" +
                             urllib.parse.quote_plus(
                                 'admin@1234') + "@apadcluster.egsqq.mongodb.net/myFirstDatabase?"
                                                 "retryWrites=true&w=majority", tlsCAFile=certifi.where())
AUTH_KEY = "AIzaSyDN7PBqfHZG5S3RE2_R7ECzeRVokiLS9BA"

db = client.get_database('APAD_Group1_DB')
records = db.Login
postings = db.Postings
user_data = db.Userdata
themes_db = db.Themes
fs = gridfs.GridFS(db)
db = client.test

api_setup = Blueprint('api', __name__)

app.register_blueprint(api_setup, url_prefix='/api')

db_dump_themes = themes_db.find()
list_of_themes_db = []
for theme in db_dump_themes:
    if theme not in list_of_themes_db:
        list_of_themes_db.append(theme)

def generate_latlong_from_address(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
    params = {"address": address,
              "key": AUTH_KEY}
    # print(f"{base_url}{urllib.parse.urlencode(params)}")
    r = requests.get(f"{base_url}{urllib.parse.urlencode(params)}")
    data = json.loads(r.content)
    latlong = data.get("results")[0].get("geometry").get("location")
    # print(address,latlong)
    return latlong

@app.route("/api/signup", methods=['post', 'get'])
def index():
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.args.get("fullname")
        email = request.args.get("email")

        password1 = request.args.get("password1")
        password2 = request.args.get("password2")

        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            response = records.insert_one(user_input)
            # print(response.inserted_id)

            user_data = records.find_one({"email": email})
            new_email = user_data['email']

            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')


# @app.route("/new_post")
# def new_post():
#     db_dump_themes = themes_db.find()
#     list_of_themes_db = []
#     for theme in db_dump_themes:
#         if theme not in list_of_themes_db:
#             list_of_themes_db.append(theme)
#     return render_template('new_post.html',list_of_themes_db=list_of_themes_db)


@app.route("/api/post_action", methods=['POST','GET'])
def post_action():
    # Adding a Post
    try:
        if "email" in session:
            user_id = session["email"]
            type_of_pet = request.args.get("type")
            tags = str(request.args.get("tags"))
            tags = tags.lower()
            post_date = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
            title = request.args.get("title")
            desc = request.args.get("description")
            location = request.args.get("location")
            # if 'file' in request.files:
            # print('Here')
            image = request.files["file"]
            title = request.args.get('title')
            img_id = fs.put(image, content_type=image.content_type, filename=title)
            # status = postings.insert_one(query)
            status = "Open"
            if (user_id != None or tags !=None or desc != None or title !=None or location !=None or img_id !=None or type_of_pet !=None):            
                post_response = postings.insert_one(
                    {"user_id": user_id, "tags": tags, "date_posted": post_date, "detailed_description": desc,
                    "post_title": title, "location": location, "image_id": img_id, "type": type_of_pet, "status": status})
                # print(str(post_response.inserted_id))
                post_id = str(post_response.inserted_id)
                # insert document ID into User_data table
                user_data.insert_one({"user_id": user_id, "posts": [post_id], })
                # print(post_id)
                session["post_id"] = post_id
                message = "Successfully Posted"
                return jsonify({'message':message})
            else:
                message = "Invalid Inputs received"
                return jsonify({'message':message})
        else:
            message = 'Please login to your account'
            return jsonify({'message':message})
    except Exception as e:
        print(e)
        return jsonify({'error': e})

@app.route("/api/login", methods=["POST", "GET"])
def login():
    print(request.args)
    message = 'Please login to your account'
    if "email" in session:
        return jsonify("Already Logged in!!")

    if request.method == "GET":
        email = request.args.get("email")
        print(email)
        password = request.args.get("password")
        print(password)
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                message = "Successfully Logged in as " + email 
                return jsonify({'message':message})
            else:
                if "email" in session:
                    return jsonify()
                message = 'Wrong password'
                return jsonify({'message':message})
        else:
            message = 'Email not found'
            return jsonify({'message':message})
    return jsonify({'message':message})



@app.route("/api/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return jsonify({'message': "logged out user"})
    else:
        message = 'Please login to your account'
        return jsonify({'message': message})


@app.route("/api/get_themes", methods=["POST", "GET"])
def get_themes():
    if "email" in session:
        db_dump_themes = themes_db.find()
        list_of_themes_db = []
        for theme in db_dump_themes:
            if theme['theme_name'] not in list_of_themes_db:
                list_of_themes_db.append(theme['theme_name'])
        return jsonify({'list_of_themes': list_of_themes_db})
    else:
        message = 'Please login to your account'
        return jsonify({'message': message})

@app.route("/api/view_all", methods=['GET', 'POST'])
def view_all():
    print(request.args)
    # Viewing all posts, show newest posts first
    list_of_latlong, list_of_titles, list_of_description, list_of_user_id, list_of_status, list_of_themes, list_of_address, list_of_image_ids = [], [], [], [], [], [], [], []
    data = {}
    type_of_pet = request.args.get('type')
    print(type_of_pet)
    db_dump_themes = themes_db.find()
    list_of_themes_db = []
    for theme in db_dump_themes:
        if theme not in list_of_themes_db:
            list_of_themes_db.append(theme)
    if "email" in session:

        if type_of_pet is None or type_of_pet == 'all':
            # print(type_of_pet)
            posts = postings.find().sort('date_posted', -1)
            # posts01 = list(posts)
            images = {}
            list_of_themes = []
            for post in posts:
                if post['type'] not in list_of_themes:
                    list_of_themes.append(post['type'])
                image = fs.get(post['image_id'])
                base64_data = codecs.encode(image.read(), 'base64')
                image = base64_data.decode('utf-8')
                images.update({post['image_id']: image})
                list_of_latlong.append(generate_latlong_from_address(post['location']))
                list_of_titles.append(post['post_title'])
                list_of_description.append(post['detailed_description'])
                list_of_user_id.append(post['user_id'])
                list_of_status.append(post['status'])
                list_of_themes.append(post['type'])
                list_of_address.append(post['location'])
                list_of_image_ids.append(image)                
            data = {
            'latlongvalues': list_of_latlong,
            'title_values': list_of_titles,
            'description_values': list_of_description,
            'user_id_values': list_of_user_id,
            'status_values': list_of_status,
            'theme_values': list_of_themes,
            'address_values': list_of_address,
            'image_values': list_of_image_ids
        }
            return jsonify(data)
            # return jsonify({'images': images,'list_of_themes_db': list_of_themes_db})
        else:
            posts = postings.find({"type": type_of_pet}).sort('date_posted', -1)
            images = {}
            for post in posts:
                image = fs.get(post['image_id'])
                base64_data = codecs.encode(image.read(), 'base64')
                image = base64_data.decode('utf-8')
                images.update({post['image_id']: image})
                list_of_latlong.append(generate_latlong_from_address(post['location']))
                list_of_titles.append(post['post_title'])
                list_of_description.append(post['detailed_description'])
                list_of_user_id.append(post['user_id'])
                list_of_status.append(post['status'])
                list_of_themes.append(post['type'])
                list_of_address.append(post['location'])
                list_of_image_ids.append(image)                
            data = {
            'latlongvalues': list_of_latlong,
            'title_values': list_of_titles,
            'description_values': list_of_description,
            'user_id_values': list_of_user_id,
            'status_values': list_of_status,
            'theme_values': list_of_themes,
            'address_values': list_of_address,
            'image_values': list_of_image_ids
        }
            return jsonify(data)
    else:
        return jsonify("Log in First")

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>", 404


# end of code to run it
if __name__ == "__main__":
    app.run(debug=True)
