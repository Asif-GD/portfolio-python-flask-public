from pymongo import MongoClient

uri = "mongodb+srv://personal.pczif.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile="portfolio_server.pem")

db = client["testDB"]
collection = db["contacts_list"]


# insert record
def add_data(contact_record, collection_name="contacts_list"):
    # to ensure that the data is added to the collection that we require.
    # always specify the collection name db.<collection_name>.insert_one()
    current_collection = db.get_collection(collection_name)
    return current_collection.insert_one(contact_record)


# read record
def find_user_by_email(user_email, collection_name="contacts_list"):
    current_collection = db.get_collection(collection_name)
    # find_one() returns a Dict Object, find() returns a Cursor Object
    user_record = current_collection.find_one({"email": user_email})
    return user_record


# delete record
def delete_user_by_email(user_email, collection_name="contacts_list"):
    current_collection = db.get_collection(collection_name)
    current_collection.delete_one({"email": user_email})

