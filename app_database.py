import pickle
import json
import pyrebase
import urllib
import random


# return json template

def return_json(data, status, message):

    msg = {
        'status': status,
        'message': message,
        'data': data
    }

    return json.loads(json.dumps(msg))

# make connection

def makeconnection():
    config = {
        "apiKey": "AIzaSyC-eNXcr5DfoDUsx2Dct0Wh3JsHKjO2LSI",
        "authDomain": "ipd-attendance-a3de8.firebaseapp.com",
        "projectId": "ipd-attendance-a3de8",
        "storageBucket": "ipd-attendance-a3de8.appspot.com",
        "messagingSenderId": "618013201727",
        "appId": "1:618013201727:web:358efd45cdb78bb67caf8a",
        "measurementId": "G-0Z3B34G2GQ",
        "databaseURL": "https://ipd-attendance-a3de8-default-rtdb.firebaseio.com",
    }
    firebase = pyrebase.initialize_app(config)
    return firebase

# create realtime database instance

def create_realtime_instance():

    fb = makeconnection()
    db = fb.database()
    return db

# create storeage database instance


def create_storage_instance():

    fb = makeconnection()
    st = fb.storage()

    return st

# read all usersi

def read_all_users():
    rt = create_realtime_instance()
    users = rt.child('users').get().val()
    return users

# fetch model from storage

def get_model():

    st = create_storage_instance()
    classifier_link = st.child(f"model/classifier.pickle").get_url(None)
    classifier = urllib.request.urlopen(classifier_link)
    classifier = pickle.load(
        classifier)
    return (classifier)

# fetch lable encoder

def get_lable_encoder():

    st = create_storage_instance()
    lb_link = st.child(f"encoder/lable_encoder.pickle").get_url(None)
    lable_encoder = urllib.request.urlopen(lb_link)
    lable_encoder = pickle.load(lable_encoder)
    return (lable_encoder)

# write encodings

def write_encodings(name , encoded):
    rt = create_realtime_instance()
    try:
        lis = rt.child(f"users/{name}").get().val()['encoding']    
        lis = list(lis)
    except:
        lis = []
    lis.append(encoded)
    rt.child(f"users/{name}").update(data={'encoding' : lis })

def writepickle(filename, data):

    f = open(f'{filename}', 'wb+')
    f.write(pickle.dumps(data))
    f.close()


def write_model():

    st = create_storage_instance()
    st.child(f'model/classifier.pickle').put(f'classifier.pickle')


def write_lable():

    st = create_storage_instance()
    st.child(f'encoder/lable_encoder.pickle').put(f'lable_encoder.pickle')
