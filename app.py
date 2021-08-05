import urllib
from bson import ObjectId
from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt
import datetime
import gridfs
import codecs

app = Flask(__name__)
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb+srv://MSITM_User:" +
                             urllib.parse.quote_plus(
                                 'admin@1234') + "@apadcluster.egsqq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.get_database('APAD_Group1_DB')
records = db.Login
postings = db.Postings
user_data = db.Userdata
fs = gridfs.GridFS(db)
db = client.test


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
        post_date = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
        title = request.values.get("title")
        desc = request.values.get("description")
        location = request.values.get("location")
        # image = request.values.get('pet_image')
        print(request.files)
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
        print(str(post_response.inserted_id))
        post_id = str(post_response.inserted_id)
        # insert document ID into User_data table
        user_data.insert_one({"user_id": user_id, "posts": [post_id], })
        print(post_id)
        session["post_id"] = post_id
        '''item = postings.find_one({'id': img_id})
        image = fs.get(item['id'])
        base64_data = codecs.encode(image.read(), 'base64')
        image = base64_data.decode('utf-8')'''
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
        item = postings.find_one({'id': document_posted['image_id']})
        print(document_posted)
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


@app.route('/sub', methods=['GET', 'POST'])
def sub():
    if "email" in session:
        subscribed_themes = request.form.getlist('themes')
        print(subscribed_themes)
        if len(subscribed_themes) > 0:
            message = "You have successfully subscribed to  - " + str(subscribed_themes)
        else:
            message = ""
        db_dump = postings.find()
        list_of_themes = []
        for doc in db_dump:
            if doc['type'] not in list_of_themes:
                list_of_themes.append(doc['type'])
        return render_template('sub.html', title='Subscribe', list_of_themes=list_of_themes, message=message)
    else:
        return redirect(url_for("login_in"))


@app.route('/view_own_posts', methods=['GET', 'POST'])
def view_own():
    # Viewing posts made by user, show newest posts first
    if "email" in session:
        posts = postings.find({'user_id': session['email']}).sort('date_posted', -1)
        return render_template('view_own_posts.html', title='View Own posts', posts=posts)
    else:
        return redirect(url_for("login"))


@app.route("/view_all", methods=['GET', 'POST'])
def view_all():
    # Viewing all posts, show newest posts first
    type_of_pet = request.form.get('type')
    if "email" in session:
        if type_of_pet is None or type_of_pet == 'all':
            print(type_of_pet)
            posts = postings.find().sort('date_posted', -1)
            #posts01 = list(posts)
            images = {}
            for post in posts:
                #print(post)
                image = fs.get(post['image_id'])
                base64_data = codecs.encode(image.read(), 'base64')
                image = base64_data.decode('utf-8')
                images.update({post['image_id']: image})
            posts = postings.find().sort('date_posted', -1)
            return render_template('all_posts.html', title='View posts', posts=posts,images=images)
        else:
            print(type_of_pet)
            posts = postings.find({"type": type_of_pet}).sort('date_posted', -1)
            images = {}
            for post in posts:

                print(post)
                image = fs.get(post['image_id'])
                base64_data = codecs.encode(image.read(), 'base64')
                image = base64_data.decode('utf-8')
                images.update({post['image_id']: image})
            posts = postings.find({"type": type_of_pet}).sort('date_posted', -1)
            return render_template('all_posts.html', title='View posts', posts=posts, images=images)
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
