import urllib
from bson import ObjectId
from flask import Flask, render_template, request, url_for, redirect, session, flash
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
app.secret_key = "testing"

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

db_dump_themes = themes_db.find()
list_of_themes_db = []
for theme in db_dump_themes:
    if theme not in list_of_themes_db:
        list_of_themes_db.append(theme)
# print(list_of_themes_db)

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


def get_details_from_ip():
    url = 'http://ipinfo.io/json'
    response = urlopen(url)
    data = json.load(response)
    IP = data['ip']
    org = data['org']
    city = data['city']
    country = data['country']
    region = data['region']
    # for dat in data:
    #     print(dat)

    print('Your IP detail\n ')
    print('IP : {4} \nRegion : {1} \nCountry : {2} \nCity : {3} \nOrg : {0} \nLocation: {5} \nPO: '
          '{6}'.format(org, region, country, city, IP, data['loc'], data['postal']))
    curr_loc = data['loc']
    return curr_loc


# Create an object of GridFs for the above database.


@app.route("/", methods=['post', 'get'])
def index():
    # message = ''
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
            response = records.insert_one(user_input)
            # print(response.inserted_id)

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


@app.route('/search_page', methods=["POST", "GET"])
def search_page():
    if "email" in session:
        email = session["email"]
        search = request.form.get('search')
        if search is not None:
          search = search.lower()
        query = {
            "tags": {
                "$regex": search,
                "$options": 'i'  # case-insensitive
            }
        }
        if "email" in session:
            if search is None or search == '':
                return render_template('search_page.html', email=email)
            else:
                posts = list(postings.find({"tags": {"$regex": search}}))
                images = {}
                for post in posts:
                    # print(post)
                    image = fs.get(post['image_id'])
                    base64_data = codecs.encode(image.read(), 'base64')
                    image = base64_data.decode('utf-8')
                    images.update({post['image_id']: image})
                return render_template('search_page.html', email=email, posts=posts, images=images)

    else:
        return redirect(url_for("login"))


@app.route("/new_post")
def new_post():
    db_dump_themes = themes_db.find()
    list_of_themes_db = []
    for theme in db_dump_themes:
        if theme not in list_of_themes_db:
            list_of_themes_db.append(theme)
    return render_template('new_post.html',list_of_themes_db=list_of_themes_db)


@app.route("/post_action", methods=['POST'])
def post_action():
    # Adding a Post
    if "email" in session:
        user_id = session["email"]
        type_of_pet = request.form.get("type")
        tags = request.values.get("tags")
        tags = tags.lower()
        post_date = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
        title = request.values.get("title")
        desc = request.values.get("description")
        location = request.values.get("location")
        # image = request.values.get('pet_image')
        # print(request.files)
        if 'file' in request.files:
            print('Here')
            image = request.files["file"]
            title = request.values.get('title')
            img_id = fs.put(image, content_type=image.content_type, filename=title)

        query = {
            'id': img_id,
            'title': request.form.get('title'),
        }
        # status = postings.insert_one(query)
        status = "Open"
        post_response = postings.insert_one(
            {"user_id": user_id, "tags": tags, "date_posted": post_date, "detailed_description": desc,
             "post_title": title, "location": location, "image_id": img_id, "type": type_of_pet, "status": status})
        # print(str(post_response.inserted_id))
        post_id = str(post_response.inserted_id)
        # insert document ID into User_data table
        user_data.insert_one({"user_id": user_id, "posts": [post_id], })
        # print(post_id)
        session["post_id"] = post_id
        '''item = postings.find_one({'id': img_id})
        image = fs.get(item['id'])
        base64_data = codecs.encode(image.read(), 'base64')
        image = base64_data.decode('utf-8')'''
        return redirect("/manage")
    else:
        return redirect(url_for("login"))


@app.route("/view_post", methods=['GET', 'POST'])
def view_post():
    # Viewing Ad posted by user on submit
    if "email" in session:
        # print(session["post_id"])
        post_id = session["post_id"]
        document_posted = postings.find_one({"_id": ObjectId(post_id)})
        item = postings.find_one({'id': document_posted['image_id']})
        # print(document_posted)
        image = fs.get(document_posted['image_id'])
        base64_data = codecs.encode(image.read(), 'base64')
        image = base64_data.decode('utf-8')

        return render_template('view_post.html', title='View your post', document_posted=document_posted, image=image)
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


@app.route("/manage", methods=['GET'])
def manage():
    # print('inside manage page')
    current_page = request.args.get('page', 1, type=int)
    delete = request.args.get('delete')
    index = request.args.get('position')
    unsubscribe = request.args.get('unsubscribe')
    # print(f'{current_page} current_page')
    item_per_page = 1
    subs_per_page = 3
    user = []
    if "email" in session:
        user_id = session['email']
        for x in postings.find({"user_id": user_id}):
            user.append(x)
        # print(f'the data is user {user} end')
        # print(user)
        user.reverse()
    if user:
        images = {}
        for post in user:
            # print(post)
            image = fs.get(post['image_id'])
            base64_data = codecs.encode(image.read(), 'base64')
            image = base64_data.decode('utf-8')
            images.update({post['image_id']: image})
        posts = postings.find().sort('date_posted')
        pages = round(len(user) / item_per_page + .499)
        # print(f'{pages} pages')
        from_page = int(current_page) * item_per_page - item_per_page
        upto_page = int(current_page) * item_per_page
        sub_from_page = int(current_page) * subs_per_page - subs_per_page
        sub_upto_page = int(current_page) * sub_from_page - sub_from_page
        list_show = user[from_page:upto_page]
        curr_id = (list_show[0]['_id'])
        curr_img_id = (list_show[0]['image_id'])
        if delete == 'True':
            # print("Ready to delete", curr_id, curr_img_id)
            delpost = postings.find_one(ObjectId(curr_id))
            # print(delpost)
            postings.remove(ObjectId(curr_id))
            fs.delete(curr_img_id)
            return redirect(url_for("manage"))
        # subss = []
        subs_list_show = user
        subs_show = records.find_one({"email" : user_id})
        show_id = subs_show['_id']
        subss = subs_show['subscriptions']
        # print(f'{len(subs_list_show)} is the length')
        # print(f'{subs_show} subs and {subss} final ')
        # print(f' here is what we are sending {list_show} right')
        """if unsubscribe == 'True':
            print(f'here is the index to be deleted {index}')
            db.Login.update({_id: show_id},{'$pull': {'subscriptions': index}})"""

        return render_template('manage.html', users=list_show, subs=subss, pages=pages, current_page=current_page, images=images)
    else:
        flash(u'There are no posts created by you!', 'alert-danger')
        return render_template('logged_in.html', email=user_id)


@app.route('/sub', methods=['GET', 'POST'])
def sub():
    
    db_dump_themes = themes_db.find()
    list_of_themes_db = []
    for theme1 in db_dump_themes:
        if theme1 not in list_of_themes_db:
            list_of_themes_db.append(theme1)
    if "email" in session:
        subscribed_themes = request.form.getlist('themes')
        # print(subscribed_themes)
        if len(subscribed_themes) > 0:
            message = "You have successfully subscribed to  - " + str(subscribed_themes)
        else:
            message = ""
        post_dump = postings.find()
        list_of_themes = []
        for doc in post_dump:
            if doc['type'] not in list_of_themes:
                list_of_themes.append(doc['type'])
        # print(session['email'])
        login_dump = records.find_one({'email': session['email']})
        if 'subscriptions' in login_dump.keys():
            updated_subs = login_dump['subscriptions']
        else:
            updated_subs = []
        if 'subscriptions' in login_dump.keys():
            # print("subscriptions exist")
            for theme in subscribed_themes:
                if theme not in updated_subs:
                    updated_subs.append(theme)
            response_update = records.update_one({'email': session['email']},
                                                 {"$set": {"subscriptions": updated_subs}})
        else:
            response_update = records.update_one({'email': session['email']},
                                                 {"$set": {"subscriptions": subscribed_themes}})
        # for record in records.find():
            # print(record)
        return render_template('sub.html', title='Subscribe', list_of_themes_db=list_of_themes_db, message=message)
    else:
        return redirect(url_for("login_in"))


@app.route('/view_own_posts', methods=['GET', 'POST'])
def view_own_posts():
    # Viewing posts made by user, show newest posts first
    if "email" in session:
        posts = postings.find().sort('date_posted', -1)
        images = {}
        for post in posts:
            # print(post)
            image = fs.get(post['image_id'])
            base64_data = codecs.encode(image.read(), 'base64')
            image = base64_data.decode('utf-8')
            images.update({post['image_id']: image})
        posts = postings.find({'user_id': session['email']}).sort('date_posted', -1)
        return render_template('view_own_posts.html', title='View posts', posts=posts, images=images)
    else:
        return redirect(url_for("login"))


@app.route("/view_all", methods=['GET', 'POST'])
def view_all():
    # Viewing all posts, show newest posts first
    type_of_pet = request.form.get('type')   
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
                # print(post)
                if post['type'] not in list_of_themes:
                    list_of_themes.append(post['type'])
                image = fs.get(post['image_id'])
                base64_data = codecs.encode(image.read(), 'base64')
                image = base64_data.decode('utf-8')
                images.update({post['image_id']: image})
            posts = postings.find().sort('date_posted', -1)
            return render_template('all_posts.html', title='View posts', posts=posts, images=images,
                                   list_of_themes_db=list_of_themes_db)
        else:
            list_of_themes =[]
            posts = postings.find().sort('date_posted', -1)
            for post in posts:
                # print(post)
                if post['type'] not in list_of_themes:
                    list_of_themes.append(post['type'])          
            # print(type_of_pet)
            posts = postings.find({"type": type_of_pet}).sort('date_posted', -1)
            images = {}
            for post in posts:
                print(post)
                image = fs.get(post['image_id'])
                base64_data = codecs.encode(image.read(), 'base64')
                image = base64_data.decode('utf-8')
                images.update({post['image_id']: image})
            posts = postings.find({"type": type_of_pet}).sort('date_posted', -1)
            return render_template('all_posts.html', title='View posts', posts=posts, images=images, list_of_themes_db=list_of_themes_db)
    else:
        return redirect(url_for("login"))


@app.route("/view_map", methods=['GET', 'POST'])
def view_map():
    # Viewing Ad posted by user on submit
    if "email" in session:
        list_of_latlong, list_of_titles, list_of_description, list_of_user_id, list_of_status, list_of_themes, list_of_address, list_of_image_ids = [], [], [], [], [], [], [], []
        posts = postings.find()
        images = {}
        for post in posts:
            # print(post['location'])
            list_of_latlong.append(generate_latlong_from_address(post['location']))
            list_of_titles.append(post['post_title'])
            list_of_description.append(post['detailed_description'])
            list_of_user_id.append(post['user_id'])
            list_of_status.append(post['status'])
            list_of_themes.append(post['type'])
            list_of_address.append(post['location'])
            image = fs.get(post['image_id'])
            base64_data = codecs.encode(image.read(), 'base64')
            image = base64_data.decode('utf-8')
            list_of_image_ids.append(image)
            images.update({post['image_id']: image})
        # print(list_of_address,list_of_latlong)

        data = {
            'latlongvalues': list_of_latlong,
            'title_values': list_of_titles,
            'description_values': list_of_description,
            'user_id_values': list_of_user_id,
            'status_values': list_of_status,
            'theme_values': list_of_themes,
            'address_values': list_of_address,
            # 'imageid_values': list_of_image_ids,
            'image_values': list_of_image_ids
        }
        # print(data)
        curr_loc = get_details_from_ip()
        # print(curr_loc)
        return render_template('view_map.html', title='View Posts on the Map', data=data, images=images, posts=posts,
                               curr_loc=curr_loc)
    else:
        return redirect(url_for("login"))

@app.route("/create_theme_action")
def create_theme_action():
    return render_template('create_theme.html')

@app.route("/create_theme", methods=['GET','POST'])
def create_theme():
    if "email" in session:
        user_id = session["email"]
        if user_id != "admin":
            flash(u'You dont have access to perform this function !!', 'alert-danger')
            return render_template('logged_in.html', email=user_id)
        else:
            theme_name = request.form.get("theme")
            post_date = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
            desc = request.values.get("description")
            image = request.files["file"]
            img_id = fs.put(image, content_type=image.content_type, filename=theme_name)
            post_response = themes_db.insert_one(
                {"theme_name": theme_name, "date_posted": post_date, "detailed_description": desc, 
                "image_id": img_id})
            # print(str(post_response.inserted_id))
            message = "Created New Theme : " + theme_name
            flash(message, 'alert-danger')
            return redirect("/logged_in")

    else:
        return redirect(url_for("login"))


# end of code to run it
if __name__ == "__main__":
    db_dump_posts = postings.find()
    app.run(debug=True)
