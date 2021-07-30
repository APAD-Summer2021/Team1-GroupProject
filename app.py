import urllib

from bson import ObjectId
from flask import Flask, render_template, request, url_for, redirect, session
import requests
from requests_toolbelt.utils import dump
import pymongo
import bcrypt
from datetime import datetime
import json


app = Flask(__name__)
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb+srv://MSITM_User:" +
                             urllib.parse.quote_plus(
                                 'admin@1234') + "@apadcluster.egsqq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.get_database('APAD_Group1_DB')
records = db.Login
postings = db.Postings

db = client.test


@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

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
            try:
                response = records.insert_one(user_input)
                print(response.inserted_id)
            except:
                print("ERROR")

            user_data = records.find_one({"email": email})
            new_email = user_data['email']

            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))


@app.route('/search_page')
def search_page():
    if "email" in session:
        email = session["email"]
        return render_template('search_page.html', email=email)
    else:
        return redirect(url_for("login"))


@app.route("/new_post")
def new_post():
    return render_template('new_post.html')


@app.route("/post_action", methods=['POST'])
def post_action():
    # Adding a Post
    if "email" in session:
        user_id = session["email"]
        # type_of_pet = request.values.get("type")
        type_of_pet = request.form.get("type")
        tags = request.values.get("tags")
        post_date = datetime.now()
        title = request.values.get("title")
        desc = request.values.get("description")
        location = request.values.get("location")
        image = "dummy for now"
        post_response = postings.insert_one(
            {"user_id": user_id, "tags": tags, "date_posted": post_date, "detailed_description": desc,
             "post_title": title,
             "location": location, "image": image, "type": type_of_pet})
        print(str(post_response.inserted_id))
        post_id = str(post_response.inserted_id)
        print(post_id)
        session["post_id"] = post_id
        return redirect("/view_post")
        # return redirect("/logged_in")
    else:
        return redirect(url_for("login"))


@app.route("/view_post", methods=['GET', 'POST'])
def view_post():
    # Viewing Ad posted by user on submit
    if "email" in session:
        print(session["post_id"])
        post_id = session["post_id"]
        document_posted = postings.find_one({"_id": ObjectId(post_id)})
        print(document_posted)
        print(type(document_posted))
        # json_object = json.dumps(document_posted)
        # print(type(json_object))
        # return redirect("/logged_in")
        return render_template('view_post.html', title='View your post', document_posted=document_posted)
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("manage"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')

<<<<<<< HEAD
#Working on this , will update :- Yamini
#@app.route("/manage", methods=["POST","GET"])
#def manage():
    user_data=[]
    # when the page is loaded show current users data
    #from user email we can query their reports and subscription
    #if request.method =="GET":
        #rep_email = records.find_one(session.get("email"))

        #user_data.append()
        # main default display

        # previous lin display
        # next display




#end of code to run it
if __name__ == "__main__":
  app.run(debug=True)

#testing
=======

if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> main
