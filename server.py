"""A Python-Flask server to serve a portfolio webpage"""
import datetime
import os

from flask import Flask, render_template, send_from_directory, request, make_response
from flask_pymongo import PyMongo
from pymongo import MongoClient

import database
from file_writer import write_to_file, write_to_csv

app = Flask(__name__)

"""Setting up the Database - Local instance"""
app.config["MONGO_URI"] = "mongodb://localhost:27017/test_db"
mongodb_client = PyMongo(app)
db = mongodb_client.db
collection = db["contacts_list"]
print(db.name)
print(db.list_collection_names())

"""If you wish to connect to a cloud MongoDB instance."""
# uri = "<Your cloud MongoDB URI>"
# client = MongoClient(uri,
#                      tls=True,
#                      tlsCertificateKeyFile="<DB certificate>")
# db = client["testDB"]  # set database testDB/prodDB
# collection = db["contacts_list"]  # set collection name
# print(db.name)
# print(db.list_collection_names())


@app.route("/")
def home():
    return render_template("index.html")


# to ensure that the web-server serves the icon.
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/assets/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/<string:page_name>")
def html_page(page_name):
    return render_template(page_name)


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        contacts_form_data = request.form.to_dict()
        contacts_form_data["date_time"] = str(datetime.datetime.now())
        # writing to a text file - database.txt
        write_to_file(contacts_form_data)
        # writing to a csv file - database.csv
        write_to_csv(contacts_form_data)
        try:
            user_email = contacts_form_data["email"]
            """ I chose to have a separate collection for a user who have contacted me in the past.
            Finding a collection in a database is less costly than finding a record from a collection
            if the collection is already available."""
            if user_email in db.list_collection_names():
                database.add_data(contacts_form_data, user_email)
            else:
                # else, I check if they have contacted me before
                user_record = database.find_user_by_email(user_email)
                # if yes, a new collection has to be created and both records of communication are stored into it.
                if user_record:
                    records_to_insert = [user_record, contacts_form_data]
                    for item in records_to_insert:
                        database.add_data(item, user_email)
                    # deleting the existing record of user from the default collection "contacts_list"
                    database.delete_user_by_email(user_email, "contacts_list")
                # else, the data is stored in the default collection "contacts_list"
                else:
                    database.add_data(contacts_form_data)
            contact_response = make_response(
                "Thank you for reaching out to me. I will get back to you as soon as I can. Cheers :)")
            return contact_response
        except:
            return "Not saved to the database."
    else:
        contact_response = make_response("Something's wrong!! Please try again")
        return contact_response


if __name__ == "__main__":
    # host="0.0.0.0" ensures that the server is run on all available IPs in the machine.
    # More information in the EXTERNALLY VISIBLE SERVER: section at
    # https://flask.palletsprojects.com/en/1.1.x/quickstart/
    app.run(debug=True, host="0.0.0.0")
