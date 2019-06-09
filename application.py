#! /usr/bin/env python
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash, json
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catagories, CatalogItems, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogitem.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Google Login Functions Starts Here#
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Web Application"

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # see if user exists , if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' "style = "width: 300px; height: 300px;border-radius: 150px;'\
        '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print("done!")
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCatagories'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'))
        response.headers['Content-Type'] = 'application/json'
        return response

# Google Login Functions Ends Here#
# Catalog CRUD and JSON Starts Heres
# JSON APIs to view Catagories Information
# Returns all info in catalogitem
@app.route('/catalog.JSON')
def catagoryJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    JSONDict = dict()
    catagories = session.query(Catagories).all()
    JSONDict["Catagories"] = list()
    for c in catagories:
        objDict = dict()
        objDict[c.name] = {'id': c.id, 'name': c.name}
        itemList = []
        items = session.query(CatalogItems).filter_by(catagories_id=c.id).all()
        for item in items:
            obj = {
                'cat_id': c.id,
                'description': item.description,
                'id': item.id,
                'item_name': item.title
            }
            itemList.append(obj)
        objDict[c.name]['Item'] = itemList
        JSONDict['Catagories'].append(objDict)
    return str(json.dumps(JSONDict))

# Returns all of item in selected catagories.
@app.route('/catalog/<int:catagories_id>/items/JSON')
def catalogItemsJSON(catagories_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    catagories = session.query(Catagories).filter_by(id=catagories_id).one()
    items = session.query(CatalogItems).filter_by(catagories_id=catagories_id).all()
    return jsonify(Items=[i.serialize for i in items])

# Returns all of selected item in catalog.
@app.route('/catalog/<int:catagories_id>/<int:id>/JSON')
def catalogItemJSON(catagories_id, id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    items = session.query(CatalogItems).filter_by(id=id).one()
    return jsonify(Item=tems.serialize)

# Show List of Catagories e.g Soccer, Basketball..
@app.route('/JSON')
@app.route('/catalog/JSON')
def catagoriesJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    catagories = session.query(Catagories).all()
    return jsonify(Catagory=[c.serialize for c in catagories])

# JSON CODE ENDS HERE
# Show All Catagories
@app.route('/')
def showCatagories():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    catagories = session.query(Catagories).order_by(asc(Catagories.name)).all()
    allItems = session.query(CatalogItems).all()
    item_list = sorted(allItems, key=lambda x: x.id, reverse=True)[:8]
    if 'username' not in login_session:
        return render_template('publicShowCatagoriesHome.html', catagories=catagories, items=item_list)
    else:
        return render_template('catagoriesHome.html', catagories=catagories, items=item_list)

# Show Catalog Items
@app.route('/catalog/<int:catagories_id>/items')
def showCatalogItem(catagories_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    catagories = session.query(Catagories).filter_by(id=catagories_id).all()
    items = session.query(CatalogItems).filter_by(catagories_id=catagories_id).all()
    creator = getUserInfo(catagories[0].user_id)
    countItems = session.query(CatalogItems).filter_by(catagories_id=catagories_id).count()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicCatalog.html', items=items, catagories=catagories, countItems=countItems, creator=creator)
    else:
        return render_template('catalog.html', items=items, catagories=catagories, countItems=countItems, creator=creator)

# Show an Item
@app.route('/catalog/<int:catagories_id>/<int:id>')
def showItem(catagories_id, id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    catagories = session.query(Catagories).filter_by(id=catagories_id).one()
    items = session.query(CatalogItems).filter_by(id=id, catagories_id=catagories_id).first()
    creator = getUserInfo(catagories.user_id)
    if 'username' not in login_session or creator.id == login_session['user_id']:
        return render_template('publicItem.html', items=items, catagories=catagories, creator=creator)
    else:
        return render_template('item.html', items=items, catagories=catagories, creator=creator)

# Create a new Catalog Items
@app.route('/catalog/new', methods=['GET', 'POST'])
def newCatalogItem():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    allCatagories = session.query(Catagories).all()
    if request.method == 'POST':
        catagories_section = request.form['catagories_section']
        catagories_id = [x for x in allCatagories if x.name == catagories_section][0].id
        newItem = CatalogItems(title=request.form['name'], description=request.form['description'],  catagories_id=catagories_id, user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCatagories'), code=302)
    else:
        return render_template('newItem.html', catagories=[x.name for x in allCatagories])

# Edit a Catalog Item
@app.route('/catalog/<int:id>/edit', methods=['GET', 'POST'])
def editCatalogItem(id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CatalogItems).filter_by(id=id).one()
    allCatagories = session.query(Catagories).all()
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit items to this Catalog App. Please create your own item to edit !');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.title = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['catagories_section']:
            category_name = request.form['catagories_section']
            category_object = [x for x in allCatagories if x.name == category_name][0]
            editedItem.catagories_id = category_object.id
            editedItem.catagories = category_object
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItem', catagories_id=editedItem.catagories.id, id=id))
    else:
        return render_template('editItem.html', item=editedItem, catagories=[categoryList.name for categoryList in allCatagories])

# Delete a Catalog Item
@app.route('/catalog/<int:id>/delete', methods=['GET', 'POST'])
def deleteCatalogItem(id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(CatalogItems).filter_by(id=id).one()
    catagory_id = itemToDelete.catagories_id
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete items to this Catalog App. Please create your own item to delete !');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCatalogItem', catagories_id=catagory_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000, debug=True)
