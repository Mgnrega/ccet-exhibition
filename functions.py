from pickle import GET
from queue import Empty
from time import time
import app_database
import cv2
import face_recognition
import json
import pyrebase
import numpy as np
import time

# return template
def testing(string):

    return f"hi {string}"


def return_json(data , status , message):

    msg = {
    'status': status,
    'message': message, 
    'data': data 
    }

    return json.loads(json.dumps(msg))

# increment

def increment_pics (name):
    rt = app_database.create_realtime_instance()
    c =  rt.child(f"users/{name}").get().val()['count'] + 1
    if c <= 10:
        rt.child(f"users/{name}").update(data={'count' : c })
    return return_json(
        data=c,
        status=1,
        message='Incremented counter'
    )


# machine learning model

def model(X_train, y_train):

    from xgboost import XGBClassifier
    from sklearn.ensemble import RandomForestClassifier
    from catboost import CatBoostClassifier
    from sklearn.svm import SVC
    classifier = CatBoostClassifier()
    classifier.fit(X_train, y_train , verbose=0)
    return classifier

# get encodings of an individual image of a person

def get_encodings(image , name):

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb)
    encode = face_recognition.face_encodings(rgb, boxes)
    if(len(encode) > 1):

        return return_json(data =0 ,status =  3 , message='More than one faces in image' )
    else:
        encode = encode[0]
        encode = encode.tolist()
        app_database.write_encodings(encoded=encode , name=name)
        return increment_pics(name)

            # return return_json(data = encode , status= 1,message= 'Attendence Taken')
#     except Exception as e:
#         return return_json(data = 0 ,status= 2 , message= str(e))


# read encodings of a persom
def get_stored_encodings():
    
    rt = app_database.create_realtime_instance()
    data  = rt.child('users').get().val()
    print(data)
    encodings = []
    lables =  []
    for i in data:  
        for j in  list(data[i]['encoding']):
            encodings.append(j)
            lables.append(str(i))


    return (encodings , lables)
    

# add encodings of person in database and retrian model

def retrain():

    
    encodings , names = get_stored_encodings()
    from sklearn.preprocessing import LabelEncoder
    lb = LabelEncoder()
    names = lb.fit_transform(names)
    app_database.writepickle('lable_encoder.pickle' , data=lb)
    classifier = model(encodings , names)
    app_database.writepickle('classifier.pickle' , data=classifier)

    app_database.write_model()
    app_database.write_lable()

    return return_json(
        data=None,
        status=1,
        message="done"
    )



def test(X_test, y_test, classifier):
    print("Score of model : ")
    print(classifier.score(X_test, y_test))


# recognize faces in image and mark attendance

def recognize_image(image):

    try:     
      
        classifier = app_database.get_model()
        lb = app_database.get_lable_encoder()

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)
        y_pred = classifier.predict(encodings)
        y_pred = lb.inverse_transform(y_pred)
        pred_prop = classifier.predict_proba(encodings)
        attendance = []
        for i in range(0 , len(y_pred)):
            # TODO: Set Threshold value
            if(max(pred_prop[i]) > 0.75 ):
                attendance.append(y_pred[i])
        
        z=0
        for ((top, right, bottom, left), name) in zip(boxes, y_pred):
   
            if( max(pred_prop[z]) > 0.75 ):
       
                # cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                # y = top - 15 if top - 15 > 15 else top + 15
                print("{} -> {}".format(name , str(max(pred_prop[z]))))
                # name = str(app_database.get_name(name , 'Karnataka' , 'Mangalore' , gid)['data'])
                # cv2.putText(image, name , (left, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 225), 4)
                # print(str(max(pred_prop[z])))
            
            else : 
                print("{} -> {}".format("Unknown" , str(max(pred_prop[z]))))
        #     cv2.putText(image, "Unknown" , (left, y), cv2.FONT_HERSHEY_SIMPLEX, 1.75, (0, 0, 255), 2)
       
            z+=1  
    
        # image = cv2.resize(image,(900,900))
        # cv2.imshow("Image", image)
        # cv2.waitKey(0)
        for i in range(attendance):
            mark_attendence(i)

        return return_json(data = attendance ,status= 1, message='Made Attendance List') 
    
    except Exception as e:
        return return_json(data=0 ,status= 2 , message= str(e) )

# mark attendnece 

def mark_attendence(name):

    try:
        db = app_database.create_realtime_instance()
        cur = db.child(f'users/{name}').get().val()['Attendance']
        db.child(f'users/{name}').update({'Attendance' : (cur+1) , 'time_of_attendance' : time.ctime()})
        return return_json(data = 0 , status= 1 ,message= "Marked attendence" )
    except Exception as e:
        return return_json(data = 0 , status= 2 ,message= "Error : "+str(e) )


def check_user(name):
    
    rt = app_database.create_realtime_instance()
    data = rt.child('users').get().val()

    for i in data:
        if str(i) == name:
            return return_json(
                data=data[str(i)]['count'],
                status=1,
                message="Already Exist"
            )

    setter = {

        
    "Attendance":0,
    "count":0,
    "encoding":[],
    "time_of_attendance":None,


    }
    data = rt.child(f'users/{name}').update(data=setter)
    return return_json(

                data=0,
                status=1,
                message="Created"
            )


