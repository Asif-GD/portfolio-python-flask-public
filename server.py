# my first server - this is the very first of many to come :)
import csv
import datetime
import os

from flask import Flask, render_template, send_from_directory, request, make_response
from pymongo import MongoClient

import database

app = Flask(__name__)

"""Setting up the Database"""
# app.config["MONGO_URI"] = "mongodb://localhost:27017/test_db"
# mongodb_client = PyMongo(app)
# db = mongodb_client.db
# collection = db['test_db']
# doc_count = collection.count_documents({})
# print(doc_count)


uri = "mongodb+srv://personal.pczif.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile="portfolio_server.pem")

# set database testDB/prodDB
db = client["testDB"]
collection = db["contacts_list"]
print(db.name)
print(db.list_collection_names())


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


def write_to_file(data):
    with open('database.txt', mode='a') as database_01:
        for item in data:
            database_01.write(f"{str(item.capitalize())} - {str(data[item])} \n")
        database_01.write("\n")


def write_to_csv(data):
    # print(f"data = {data}")  # --> testing
    # print(f"data = {type(data)}")  # --> testing
    with open('database.csv', newline='', mode='a') as database_02:
        headers = data.keys()
        # print(f"headers = {headers}")  # -> testing
        database_02_writer = csv.DictWriter(database_02, fieldnames=headers)
        # to ensure that the headers is written only once and not everytime when the file is written.
        # it will be at 0 only if it's a new file.
        if database_02.tell() == 0:
            database_02_writer.writeheader()
        database_02_writer.writerow(data)


@app.route("/thank_you", methods=["POST", "GET"])
def thank_you():
    if request.method == "POST":
        try:
            contacts_form_data = request.form.to_dict()
            contacts_form_data["date_time"] = str(datetime.datetime.now())
            # write_to_file(contacts_form_data)
            # write_to_csv(contacts_form_data)
            user_email = contacts_form_data["email"]
            # print(user_email)  # --> testing
            # I chose to have a separate collection for a user who have contacted me in the past.
            # finding a collection in a database is less costly than finding a record from a collection
            # if the collection is already available.
            if user_email in db.list_collection_names():
                # print("inside if 1")  # --> testing
                database.add_data(contacts_form_data, user_email)
            else:
                # else, I check if they have contacted me before
                # print("inside else 1")  # --> testing
                user_record = database.find_user_by_email(user_email)
                # print(user_record)  # --> testing
                # if yes, a new collection has to be created and both records of communication are stored into it.
                if user_record:
                    # print("inside if 2")  # --> testing
                    records_to_insert = [user_record, contacts_form_data]
                    for item in records_to_insert:
                        # print("inside for loop")  # --> testing
                        database.add_data(item, user_email)
                    # deleting the existing record of user from the default collection "contacts_list"
                    database.delete_user_by_email(user_email, "contacts_list")
                # else, the data is stored in the default collection "contacts_list"
                else:
                    # print("inside else 2")  # --> testing
                    database.add_data(contacts_form_data)
            contact_response = make_response(
                "Thank you for reaching out to me. I will get back to you as soon as I can. Cheers :)")
            return render_template("thank_you.html", contact_response=contact_response)
        except:
            return "Not saved to the database."
    else:
        contact_response = make_response("Something's wrong!! Please try again")
        # will create a creative error page for errors
        return render_template("thank_you.html", contact_response=contact_response)


# # testing
# @app.route('/urls')
# def url():
#     return '<h1>' + (url_for('favicon')) + '</h1>'

if __name__ == "__main__":
    # host="0.0.0.0" ensures that the server is run on all available IPs in the machine.
    # More information in the EXTERNALLY VISIBLE SERVER: section at
    # https://flask.palletsprojects.com/en/1.1.x/quickstart/
    app.run(debug=True, host="0.0.0.0")
