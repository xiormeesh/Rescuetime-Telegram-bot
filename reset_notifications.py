#!/usr/bin/python3

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def reset_notifications(request):
	'''
	finds all tasks with 'reached_today' eq True and sets them to False
	should be run once a day at night to reset notifications enabling them to be sent the next day
	'''

    if request.method == "GET":
        
        # https://firebase.google.com/docs/reference/admin/python/firebase_admin.credentials
        cred = credentials.ApplicationDefault()
        
        # https://firebase.google.com/docs/reference/admin/python/firebase_admin
        firebase_admin.initialize_app(cred, {
        	# firebase and function must be in the same project
            'projectId': cred.project_id,
        })

        # https://firebase.google.com/docs/reference/admin/python/firebase_admin.firestore
        db = firestore.client()
        
        # query: https://googleapis.dev/python/firestore/latest/query.html
        tasks_query = db.collection('tasks').where("reached_today", "==", True)
        # stream() on Query returns an iterator over DocumentSnapshots
        tasks = tasks_query.stream()

        for task in tasks:
            print("{} => {}".format(task.id, task.to_dict()))
            # document: https://googleapis.dev/python/firestore/latest/document.html
            # since it's a DocumentSnapshot and not DocumentReference, need to extract the reference
            # because DocumentSnapshot is a read-only copy of the document
            task.reference.update({"reached_today": False})
    
    return "ok"