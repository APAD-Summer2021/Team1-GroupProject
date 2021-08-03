import urllib
from bson import ObjectId
from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt
import certifi
import datetime

app = Flask(__name__)
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb+srv://MSITM_User:" + urllib.parse.quote_plus('admin@1234') + "@apadcluster.egsqq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", tlsCAFile=certifi.where())
    
db = client.get_database('APAD_Group1_DB')
records = db.Login
postings = db.Postings
user_data = db.Userdata
db = client.test


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
            print(response.inserted_id)

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
        type_of_pet = request.form.get("type")
        tags = request.values.get("tags")
        post_date = datetime.date.strftime(datetime.date.today(), "%m/%d/%Y")
        print(post_date)
        title = request.values.get("title")
        desc = request.values.get("description")
        location = request.values.get("location")
        image = request.values.get('pet_image')
        status = "Open"
        post_response = postings.insert_one(
            {"user_id": user_id, "tags": tags, "date_posted": post_date, "detailed_description": desc,
             "post_title": title, "location": location, "image": image, "type": type_of_pet, "status": status})
        print(str(post_response.inserted_id))
        post_id = str(post_response.inserted_id)
        # insert document ID into User_data table
        user_data.insert_one({"user_id": user_id, "posts": [post_id], })
        print(post_id)
        session["post_id"] = post_id
        return redirect("/view_post")
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
        # print(type(document_posted))
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


@app.route('/sub', methods=['GET', 'POST'])
def sub():
    if "email" in session:
        subscribed_tags = request.form.getlist('tags')
        print(subscribed_tags)
        message = "You have successfully subscribed to  - " + str(subscribed_tags)

        db_dump = postings.find()
        list_of_tags = []
        for doc in db_dump:
            # print(doc)
            for tag_list in doc['tags'].split(','):
                if tag_list not in list_of_tags:
                    list_of_tags.append(tag_list)
        # print(list_of_tags)
        return render_template('sub.html', title='Subscribe', list_of_tags=list_of_tags, message=message)
    else:
        return redirect(url_for("login_in"))


@app.route('/view_own_posts', methods=['GET', 'POST'])
def view_own():
    # Viewing all posts, show newest posts first
    if "email" in session:
        posts = postings.find({'user_id': session['email']}).sort('date_posted', -1)
        return render_template('view_own_posts.html', title='View Own posts', posts=posts)
    else:
        return redirect(url_for("login"))


@app.route("/view_all", methods=['GET', 'POST'])
def view_all():
    # Viewing all posts, show newest posts first
    if "email" in session:
        list_of_posted_locations = []
        locations = postings.find()
        for loc in locations:
            if loc['location'] not in list_of_posted_locations:
                list_of_posted_locations.append(loc['location'])
        print(list_of_posted_locations)
        type_of_pet = request.form.get("type")
        location = request.form.get("location")
        print(type_of_pet, location)
        if (type_of_pet is None or type_of_pet == 'all') and (location == 'all' or location is None):
            posts = postings.find().sort('date_posted', -1)
            return render_template('all_posts.html', title='View posts', posts=posts,
                                   locations=list_of_posted_locations)
        elif type_of_pet == 'all':
            posts = postings.find({"location": location}).sort('date_posted', -1)
        elif location == 'all':
            posts = postings.find({"type": type_of_pet}).sort('date_posted', -1)
        else:
            posts = postings.find({"type": type_of_pet, 'location': location}).sort('date_posted', -1)
        print("Display all the fetched posts")
        print(posts)
        for test in posts:
            print("Items in result")
            print(test['post_title'])
        return render_template('all_posts.html', title='View posts', posts=posts, locations=list_of_posted_locations)
    else:
        return redirect(url_for("login"))


@app.route('/manage', methods=['GET'])
def manage():
    if "email" in session:
        user = {"reports": {"title": "Test", "date": "Test Date", "desc": "Test Desc", "tag": "Test Tag",
                            "theme:": "Test Theme", "img": "https://via.placeholder.com/350x350"}}
        return render_template("manage.html", user=user)
    else:
        return redirect(url_for("login"))


# end of code to run it
if __name__ == "__main__":
    app.run(debug=True)
