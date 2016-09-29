#!/usr/bin/python

import os
from flask import Flask, jsonify, send_from_directory, make_response, request, abort, flash, redirect
from werkzeug.utils import secure_filename
from hurry.filesize import size
from filesize import humansize
from ceph import listBuckets, listObjectsInBucket, createObjectFromFile
import json
from pprint import pprint

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'JPG'])

app = Flask(__name__)
#sess = Session();

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }

]

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
               
@app.route('/')
def index():
    return "Hello, World!"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/ceph/api/v1/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks':tasks})

@app.route('/ceph/api/v1/get_bucket_list', methods=['GET'])
def get_bucket_list():
    buckets = listBuckets()
    result = []
    for bucket in buckets:
        #result[i] = "{name}\t{creation_date}".format(name=bucket.name, creation_date=bucket.creation_date)
        each = dict()
        each['name'] = bucket.name
        each['created_at'] = bucket.creation_date
        result.append(each);

    return json.dumps(result, ensure_ascii=False)


@app.route('/ceph/api/v1/get_object_list_in_bucket/<bucket_name>', methods=['GET'])
def get_object_list(bucket_name):
    status, objects = listObjectsInBucket(bucket_name);
    if status:
        result = []
        for obj in objects:
            each = dict()
            each['name'] = obj.name
            each['size'] = humansize(obj.size)
            each['modified'] = obj.last_modified
            result.append(each)
        return json.dumps(result, ensure_ascii=False)
            
    else:
        result = dict()
        result['Status_Code'] = objects.status
        result['Message'] = objects.message
        return json.dumps(result, ensure_ascii=False)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/ceph/api/v1/tasks', methods=['POST'])
def create_tasks():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
        }
    tasks.append(task)
    return jsonify({'task': task}), 201

@app.route('/ceph/api/v1/create_object', methods=['POST'])
def create_object():
    bucket_name = request.headers.get('bucket')
    print bucket_name
    if bucket_name == '':
        return jsonify({"status": 400, "message": "empty bucket name"}), 400
    
    if request.method == 'POST':
        #print request.method
        # check if the post request has the file part
        #print request.files
        if 'file' not in request.files:
            flash('No file part')
            return jsonify({"status": 400, "message": "no file part"}), 400
            #return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            #return redirect(request.url)
            return jsonify({"status": 400, "message": "empty file name"}), 400
        if file and allowed_file(file.filename):
            #ifilename = secure_filename(file.filename)
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try:
                createObjectFromFile(bucket_name, file.filename, file)
            except err:
                print err
            return jsonify({"status": 200, "message": file.filename + " has been upload."}), 200
        elif not allowed_file(file.filename):
            return jsonify({"status": 400, "message": "not allow file type"}), 400
            
            #return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
    <p><input type=file name=file>
    <input type=submit value=Upload>
    </form>
    '''

    #pprint(vars(request))
    #return jsonify({"status": "Success"}), 200

if __name__ == '__main__':
    app.secret_key = 'this is a secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    #sess.init_app(app)
    app.run(host='0.0.0.0', port=8080, debug=True)
