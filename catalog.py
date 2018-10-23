from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify, make_response, session as login_session
from sqlalchemy import create_engine
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import OAuth2WebServerFlow

import httplib2
import random
import string
import json
import requests
import os
import sys

from models import BaseModel, UserModel, ItemsModel, CategoryModel

# database string
db_string = "postgresql://postgres:postgres@localhost:5432/catalog"
# db_string = 'sqlite:///catalog01.db'

app = Flask(__name__)

# For local dev, read OAuth data from client_secrets.json
client_id = json.loads(open('client_secrets.json', 'r')
                           .read())['web']['client_id']
client_secret = json.loads(open('client_secrets.json', 'r')
                           .read())['web']['client_secret']
auth_uri = json.loads(open('client_secrets.json', 'r')
                      .read())['web']['auth_uri']
token_uri = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['token_uri']
auth_provider_x509_cert_url = json.loads(open('client_secrets.json', 'r')
                                             .read())['web']['auth_provider_x509_cert_url']
scope = ""
redirect_uri = "postmessage"

# For Heroku, read from heroku config variables
# client_id = os.environ.get('client_id')
# client_secret = os.environ.get('client_secret')
# scope = ""
# redirect_uri = "postmessage"
# auth_uri = os.environ.get('auth_uri')
# token_uri = os.environ.get('token_uri')
# auth_provider_x509_cert_url = os.environ.get('auth_provider_x509_cert_url')


@app.before_first_request
def create_all():
    # create only once
    if not os.path.exists('init.done'):
        engine = create_engine(db_string)
        BaseModel.metadata.create_all(engine)
        admin = UserModel(username='admin', email='admin@xyz.com')
        admin.create_user()
        seed_file = open('categories.txt', 'r')
        for line in seed_file:
            cat = line.split(':')
            category = CategoryModel(name=cat[0], desc=cat[1],
                                     user_id=admin.id, user=admin)
            category.create_category()

        # create a file to denote that setup is complete
        f = open("init.done", "x")


# Login & Logout
@app.route('/login', methods=['GET'])
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state, client_id=client_id)


# List all categories and latest items
@app.route('/', methods=['GET'])
@app.route('/catalog/', methods=['GET'])
def catalogList():
    cats = CategoryModel.get_all()
    items = ItemsModel.get_new_items()
    current_user = UserModel.get_by_id(login_session.get('user_id'))

    return render_template("catalog.html", categories=cats,
                           items=items, user=current_user)


# List all items in a category
@app.route('/catalog/<string:category_name>/items', methods=['GET'])
def category_items(category_name):
    category = CategoryModel.get_by_name(category_name)

    if category is None:
        error = 'No such category!'
        return render_template('errors.html', error=error)

    items = ItemsModel.get_all_in_a_category(category.id)
    current_user = UserModel.get_by_id(login_session.get('user_id'))

    return render_template("categoryItems.html", category=category,
                           items=items, user=current_user,
                           noOfItems=len(items))


# List details of one particular item
@app.route('/catalog/<string:category_name>/<string:item_name>',
           methods=['GET'])
def category_item_details(category_name, item_name):
    category = CategoryModel.get_by_name(category_name)

    if category is None:
        error = 'No such category or item!'
        return render_template('errors.html', error=error)

    item = ItemsModel.get_by_name_and_category(item_name, category.id)
    current_user = UserModel.get_by_id(login_session.get('user_id'))

    if item is None or category is None:
        error = 'No such item!'
        return render_template('errors.html', error=error)

    return render_template("itemDetails.html", category=category, item=item,
                           user=current_user)


# Add a particular item
@app.route('/catalog/add', methods=['GET', 'POST'])
def category_item_add():
    if request.method == 'POST':
        # check if user is logged in else error
        if not login_session.get('user_id'):
            error = 'You are not logged in! Login to continue.'
            return render_template('errors.html', error=error)

        nm = request.form['iname']
        ds = request.form['idesc']
        ct = request.form['icategory']
        category = CategoryModel.get_by_name(ct)
        cats = CategoryModel.get_all()
        current_user = UserModel.get_by_id(login_session.get('user_id'))

        # check if there is a name
        if not nm or nm == "":
            flash('Item name needed!')
            return render_template("addItem.html", categories=cats,
                                   user=current_user, i_name=nm, i_desc=ds,
                                   i_ct=ct)

        # check if the new item has same name
        if ItemsModel.get_by_name(nm) is not None:
            flash('Item with same name already exists, try another name.')
            return render_template("addItem.html", categories=cats,
                                   user=current_user, i_name=nm, i_desc=ds,
                                   i_ct=ct)

        item = ItemsModel(name=nm, desc=ds, category_id=category.id,
                          user_id=login_session['user_id'])
        item.save_to_db()
        return redirect(url_for('catalogList'))
    else:
        current_user = UserModel.get_by_id(login_session.get('user_id'))
        cats = CategoryModel.get_all()
        return render_template("addItem.html", categories=cats,
                               user=current_user)


# Edit details of one particular item
@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def category_item_edit(item_name):
    if request.method == 'POST':

        # check if user is logged in
        if not login_session.get('user_id'):
            error = 'You are not logged in! Please login to continue.'
            return render_template('errors.html', error=error)

        nm = request.form['iname']
        ds = request.form['idesc']
        ct_name = request.form['icategory']
        id = request.form['iid']

        category = CategoryModel.get_by_name(ct_name)
        old_item = ItemsModel.get_by_id(id)

        # check if the item exists (someone else has not already deleted it)
        if old_item is None:
            error = 'No such item!'
            return render_template('errors.html', error=error)

        # check if this user owns the item
        if old_item.user_id != login_session['user_id']:
            error = 'You are not authorized to update this item.'
            return render_template('errors.html', error=error)

        # check if there were updates
        if old_item.name == nm and old_item.desc == ds and old_item.category.name == ct_name:
            error = 'Nothing to update'
            return render_template("errors.html", error=error)
        else:
            # if updates, save
            # updated_item =
            # ItemModel.updateItem(old_name=old_item.name,
            # name=nm, desc=ds, category=category)
            old_item.name = nm
            old_item.desc = ds
            old_item.category = category
            old_item.save_to_db()  # only save no update???
            return redirect(url_for('catalogList'))
    else:
        current_user = UserModel.get_by_id(login_session.get('user_id'))
        cats = CategoryModel.get_all()
        item = ItemsModel.get_by_name(item_name=item_name)

        if current_user is None:
            error = 'You are not logged in! Please login to continue.'
            return render_template('errors.html', error=error)

        if item is None:
            error = 'No such item!'
            return render_template('errors.html', error=error)

        return render_template("editItem.html", item=item, categories=cats,
                               user=current_user)


# Delete details of one particular item
@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def category_item_delete(item_name):
    if request.method == 'POST':

        id = request.form['iid']
        item = ItemsModel.get_by_name(item_name)

        # check if user is logged in
        if not login_session.get('user_id'):
            error = 'You are not logged in! Please login to continue.'
            return render_template('errors.html', error=error)

        # check if the item exists (someone else has not already deleted it)
        if item is None:
            error = 'No such item!'
            return render_template('errors.html', error=error)

        # check if this user owns the item
        if item.user_id != login_session['user_id']:
            error = 'You are not authorized to delete this item.'
            return render_template('errors.html', error=error)

        to_be_del_item = ItemsModel.get_by_id(id)
        to_be_del_item.delete_item()
        return redirect(url_for('catalogList'))
    else:
        item = ItemsModel.get_by_name(item_name=item_name)
        current_user = UserModel.get_by_id(login_session.get('user_id'))

        if current_user is None:
            error = 'You are not logged in! Please login to continue.'
            return render_template('errors.html', error=error)

        if item is None:
            error = 'No such item!'
            return render_template('errors.html', error=error)

        return render_template("deleteItem.html", item=item, user=current_user)


# Misc - about
@app.route('/contact/', methods=['GET'])
def contact():
    return render_template("contactus.html")


# JASON for the catalog
@app.route('/catalog.json')
def category_json():
    cats = CategoryModel.get_all()
    return jsonify(CategoryModel=[c.serialize for c in cats])

# @app.route('/catalog/<string:category_name>/items.json')
# conflicting
@app.route('/catalog/<string:category_name>.json')
def catalog_items_json(category_name):
    cat = CategoryModel.get_by_name(category_name)
    if cat:
        return jsonify(cat.serialize)
    else:
        response = make_response(json.dumps('Invalid category name.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/catalog/<string:category_name>/<string:item_name>.json')
def item_json(category_name, item_name):

    item = ItemsModel.get_by_name(item_name)
    cat = CategoryModel.get_by_name(category_name)

    if item and cat and item.category_id == cat.id:
        return jsonify(item.serialize)
    else:
        response = make_response(json.dumps('Invalid request parameters.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/catalog/allitems.json')
def items_json():
    items = ItemsModel.get_all()
    return jsonify(ItemsModel=[i.serialize for i in items])





# # delete this
# @app.route('/users', methods=['GET'])
# def category_users():
#     users = dataSQL.getAllUsers()
#     output = ""
#     for user in users:
#         output += user.name
#     return output


# Additional Functionalities for future
# Categories
@app.route('/catalog/category/add', methods=['GET', 'POST'])
def category_add():
    return render_template("addCategory.html")


@app.route('/catalog/category/<string:category>/edit', methods=['GET', 'POST'])
def category_edit(category):
    return render_template("editCategory.html")


@app.route('/catalog/category/<string:category>/delete',
           methods=['GET', 'POST'])
def category_delete(category):
    return render_template("deleteCategory.html")


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code that login.html received
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow = OAuth2WebServerFlow(
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            redirect_uri=redirect_uri,
            auth_uri=auth_uri,
            token_uri=token_uri,
            auth_provider_x509_cert_url=auth_provider_x509_cert_url
        )

        # Step 1
        oauth_flow.step1_get_authorize_url()

        # Step 2
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Next, check that the access token is valid
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
        response = make_response(json.dumps(
                                            "Token's user ID doesn't match \
                                            given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != client_id:
        response = make_response(json.dumps(
                                 "Token's client ID does not match app's."),
                                 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
                                            connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check if new user, and add to DB
    em1 = login_session['email']
    user = UserModel.get_by_email(user_email=em1)
    # print 'user_id is not none = %s' % user_id
    # login_session['user_id'] = user_id

    if user is None:  # Its a new user
        user = UserModel(username=login_session['username'],
                         email=login_session['email'])
        user.create_user()

    login_session['user_id'] = user.id
    # print "created new user_id %s" %(user.id)
    # print 'created new user_id %s' %user_id

    # print "login_session['user_id']"
    # print login_session['user_id']

    # print "----------------------------------"
    # print login_session
    # print "----------------------------------"

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += '!</h3> <br><br>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; border-radius: 50px;"> '
    flash("You are now logged in as %s." % login_session['username'])
    return output


@app.route('/logout')
def gdisconnect():
    c = login_session.get('credentials')
    print "c is: " + c
    access_token = None
    if c:
        json_obj = json.loads(c)
        access_token = json_obj["access_token"]

    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # if the status = 200, it means we successfully revoked access
    if result['status'] == '200':
        message = 'Successfully disconnected.'
    else:  # else it means that the token has expired
        message = 'You are not connected!'

    # In either case, do below
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    flash(message)
    return redirect(url_for('catalogList'))


app.secret_key = os.environ.get('SECRET_KEY', 'some secret_key')
app.debug = True

if __name__ == "__main__":
    client_id = json.loads(open('client_secrets.json', 'r')
                           .read())['web']['client_id']

    client_secret = json.loads(open('client_secrets.json', 'r')
                               .read())['web']['client_secret']

    scope = ""
    redirect_uri = "postmessage"

    auth_uri = json.loads(open('client_secrets.json', 'r')
                          .read())['web']['auth_uri']

    token_uri = json.loads(open('client_secrets.json', 'r')
                           .read())['web']['token_uri']

    auth_provider_x509_cert_url = json.loads(open('client_secrets.json', 'r')
                                             .read())['web']['auth_provider_x509_cert_url']

    app.run(host="0.0.0.0", port=5000)
