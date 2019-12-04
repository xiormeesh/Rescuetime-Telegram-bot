#!/usr/bin/python3

from google.cloud import firestore


def reset_notifications(request):
    '''
    finds all tasks with 'reached_today' eq True and sets them to False
    should be run once a day at night to reset notifications
    enabling them to be sent the next day
    '''

    if request.method == "GET":

        # https://github.com/googleapis/google-cloud-python/tree/master/firestore
        db = firestore.Client()

        # query: https://googleapis.dev/python/firestore/latest/query.html
        # stream() on Query returns an iterator over DocumentSnapshots
        tasks = db.collection('tasks').where("reached_today", "==", True).stream()

        for task in tasks:
            print("{} => {}".format(task.id, task.to_dict()))
            # document: https://googleapis.dev/python/firestore/latest/document.html
            # since it's a DocumentSnapshot and not DocumentReference, need to extract the reference
            # because DocumentSnapshot is a read-only copy of the document
            task.reference.update({"reached_today": False})

    return "ok"
