from flask import Flask, render_template, request, jsonify, redirect, url_for
import pymongo
from bson.objectid import ObjectId
import os
from flask import send_from_directory

app = Flask(__name__)

def create_mongodb_connection():
    user = '*******'
    pwd = '*****'
    client = pymongo.MongoClient('mongodb://'+user+':'+pwd+'******')
    db = client['****']
    return db

def insert_todo(date, name, done):
    db = create_mongodb_connection()
    todo = {
        'tododate': date,
        'name': name,
        'done': done
    }
    db.todo.insert_one(todo)

def show_todo(date):
    db = create_mongodb_connection()
    todos = db.todo.find({"tododate": date})
    return todos

@app.route('/')
def home():
    db = create_mongodb_connection()
    todos = db.todo.find()
    return render_template('index.html', todos=todos)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

def convert_objectid_to_str(todo):
    todo['_id'] = str(todo['_id'])
    return todo

@app.route('/calendar')
def calendar():
    db = create_mongodb_connection()
    cursor = db.todo.find()
    todos = [convert_objectid_to_str(todo) for todo in cursor]
    return render_template("calendar.html", todos=todos)

@app.route('/detail')
def detail():
    date = request.args.get('date')
    date_list = date.split("-")
    todos = show_todo(date)
    return render_template('detail.html', todos=todos, year=date_list[0], month=date_list[1], day=date_list[2])

@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    todo_id = data.get('id')
    db = create_mongodb_connection()
    db.todo.update_one({'_id': ObjectId(todo_id)}, {'$set': {'done': True}})
    return jsonify({'status': 'success', 'id': todo_id})

@app.route('/uncheck', methods=['POST'])
def uncheck():
    data = request.get_json()
    todo_id = data.get('id')
    db = create_mongodb_connection()
    db.todo.update_one({'_id': ObjectId(todo_id)}, {'$set': {'done': False}})
    return jsonify({'status': 'success', 'id': todo_id})

@app.route('/delete', methods=['POST'])
def delete():
    db = create_mongodb_connection()
    todo_id = request.json['id']

    # 指定されたIDのタスクを削除
    result = db.todo.delete_one({"_id": ObjectId(todo_id)})
    return redirect(url_for('home'))

@app.route('/add', methods=['POST'])
def add():
    db = create_mongodb_connection()
    todo = {
        "tododate": request.form['date'],
        "name": request.form['todo'],
        "done": False
    }
    db.todo.insert_one(todo)
    return redirect(url_for('home'))




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=11026)
