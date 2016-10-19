from flask import Flask, jsonify, request, render_template, url_for, session, redirect
from flask_pymongo import PyMongo
from pymongo import MongoClient
import bcrypt
import random

############initialization of variables#################

app = Flask(__name__)
client = MongoClient()
db = client['OnlineStore']
coll = db['productdetails']
collUsers  = db['users']

##############################################

def insert_doc():
    retval = db.counter.find_and_modify(
        query={ 'adminid' : 'userid' },
        update={'$inc': {'id': 1}},
        fields={'_id': 1, '_id': 0},
        new=True 
    )

    
@app.route('/')
def index():
	if 'username' in session:
		return render_template('four_buttons.html', token = session['token'])

	return render_template('index.html')

@app.route('/token_display/')
def token_display():
	if 'username' in session:
		return render_template('token_display.html', token = session['token'])

	return render_template('index.html')


@app.route('/login/', methods = ['POST'])
def login():
	login_user = collUsers.find_one({'name' : request.form['username']})

	if login_user:
		if bcrypt.hashpw(request.form['psword'].encode('utf-8'), login_user['psword'].encode('utf-8')) == login_user['psword'].encode('utf-8'):
			session['username'] = request.form['username']
			session['token'] = login_user['token']
			return redirect(url_for('index'))
	return 'Invalid username or password'	


@app.route('/register/', methods = ['POST'])
def register():
	existing_user = collUsers.find_one({'name' : request.form['username']})
	if existing_user is None:
		hashpass = bcrypt.hashpw(request.form['psword'].encode('utf-8'), bcrypt.gensalt())
		token = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(32))
		collUsers.insert({'name' : request.form['username'], 'psword' : hashpass,'token' : token})
		session['username'] = request.form['username']
		return redirect(url_for('index'))

	return 'Already exists!'


@app.route('/get_product/' , methods = ['POST'])
def get_all_products():
	username = request.form['username']
	token = request.form['token']
	login_user = collUsers.find_one({'name' : request.form['username']})
	if(login_user['token'] == token):
		
		result=[]
		
		for document in coll.find():
			document.pop('_id')
			result.append(document)
		
		return jsonify({"results" : result}) 
	return jsonify({"status" : "Authentication Error"})

@app.route('/get_one_product/' , methods = ['POST'])
def get_one_product():
	username = request.form['username']
	token = request.form['token']
	login_user = collUsers.find_one({'name' : request.form['username']})
	if(login_user['token'] == token):
	
		result=[]
		
		q = coll.find_one({'name' : request.form['name']})
		
		if q:
			output = {'name' : q['name'], 'cost' : q['cost'], 'quantity' : q['quantity']}
		else:
			output = 'No results found'

		return jsonify({"result" : output}) 
	return jsonify({"status" : "Authentication Error"})


@app.route('/insert_product/', methods=['POST'])
def hello():
	username = request.form['username']
	token = request.form['token']
	login_user = collUsers.find_one({'name' : request.form['username']})
	if(login_user['token'] == token):
	    prodname = request.form['prodname']
	    cost = request.form['cost']
	    quantity = request.form['quantity']
	    #_id = insert_doc()
	    #print id
	    coll.insert({'name' : prodname, 'cost' : cost, 'quantity' : quantity})
	    #return render_template('form_action.html', prodname = prodname, cost = cost, quantity = quantity)
	    return jsonify({"status" : "Ok"})
	return jsonify({"status" : "Authentication Error"})


@app.route('/form_update/')
def form_updt():
	if 'username' in session:
		return render_template('form_update.html')

@app.route('/update_product/', methods=['POST'])
def updt():
	username = request.form['username']
	token = request.form['token']
	login_user = collUsers.find_one({'name' : request.form['username']})
	if(login_user['token'] == token):
	
		name = request.form['prodname']
		newName = request.form['nwname']
		newCost = request.form['nwCost']
		newQuant = request.form['nwQuant']
		coll.update_one(
	        {"name": name},
	        {
	        "$set": {
	            "name":newName,
	            "cost":newCost,
	            "quantity":newQuant
	        }
	        }
	    )
		return jsonify({"status" : "Done"})
	return jsonify({"status" : "Authentication Error"})


@app.route('/delete_product/', methods=['POST'])
def delt():
	username = request.form['username']
	token = request.form['token']
	login_user = collUsers.find_one({'name' : request.form['username']})
	if(login_user['token'] == token):
	
		name = request.form['prodname']
		coll.delete_many({'name' : name})
		return jsonify({"status" : "Done"})
	return jsonify({"status" : "Authentication Error"})


if __name__ == "__main__":
	app.secret_key = 'mysecret'
	app.run(debug = True)