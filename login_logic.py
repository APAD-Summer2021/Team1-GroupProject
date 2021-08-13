from urllib import request
from flask import url_for, render_template, jsonify
from passlib.handlers import bcrypt
from requests import session
from werkzeug.utils import redirect


def login():
    message = 'Please login to your account'
    if "email" in session:
        return jsonify("Already Logged in!!")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                # return redirect(url_for('logged_in'))
                return jsonify()
            else:
                if "email" in session:
                    return jsonify()
                message = 'Wrong password'
                return jsonify({'message':message})
        else:
            message = 'Email not found'
            return jsonify({'message':message})
    return jsonify({'message':message})
