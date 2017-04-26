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

from models import BaseModel, UserModel, ItemsModel, CategoryModel

app = Flask(__name__)

# CLIENT_ID = json.loads(
    # open('client_secrets.json', 'r').read())['web']['client_id']
CLIENT_ID = os.environ.get('client_id', None)

@app.before_first_request
def create_all():
    # create only once
    if not os.path.exists('catalog01.db'):
        engine = create_engine('sqlite:///catalog01.db')
        BaseModel.metadata.create_all(engine)
        admin = UserModel(username='admin', email='admin@xyz.com')
        admin.create_user()
        seed_file = open('categories.txt', 'r')
        for line in seed_file:
            cat = line.split(':')
            category = CategoryModel(name=cat[0], desc=cat[1], user_id=admin.id, user=admin)
            category.create_category()


# Login & Logout
@app.route('/login', methods=['GET'])
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)


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
    items = ItemsModel.get_all_in_a_category(category.id)
    current_user = UserModel.get_by_id(login_session.get('user_id'))

    return render_template("categoryItems.html", category=category,
                           items=items, user=current_user,
                           noOfItems=len(items))


# List details of one particular item
@app.route('/catalog/<string:category_name>/<string:item_name>', methods=['GET'])
def category_item_details(category_name, item_name):
    category = CategoryModel.get_by_name(category_name)
    item = ItemsModel.get_by_name_and_category(item_name, category.id)
    current_user = UserModel.get_by_id(login_session.get('user_id'))

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
            # ItemModel.updateItem(old_name=old_item.name, name=nm, desc=ds, category=category)
            old_item.name = nm
            old_item.desc = ds
            old_item.category = category
            old_item.save_to_db() # only save no update???
            return redirect(url_for('catalogList'))
    else:
        current_user = UserModel.get_by_id(login_session.get('user_id'))
        cats = CategoryModel.get_all()
        item = ItemsModel.get_by_name(item_name=item_name)
        return render_template("editItem.html", item=item, categories=cats,
                               user=current_user)


# Delete details of one particular item
@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def category_item_delete(item_name):
    if request.method == 'POST':

        id = request.form['iid']
        item = ItemsModel.get_by_id(id)

        # check if user is logged in
        if not login_session.get('user_id'):
            error = 'You are not logged in! Please login to continue.'
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
        return render_template("deleteItem.html", item=item, user=current_user)


# Misc - about
@app.route('/contact/', methods=['GET'])
def contact():
    return render_template("contactus.html")


# JASON for the catalog
@app.route('/catalog/catalog.json')
def category_json():
    cats = CategoryModel.get_all()
    return jsonify(CategoryModel=[c.serialize for c in cats])


@app.route('/catalog/items.json')
def items_json():
    items = ItemsModel.get_all()
    return jsonify(ItemsModel=[i.serialize for i in items])


@app.route('/catalog/<string:item_name>/item.json')
def item_json(item_name):
    item = ItemsModel.get_by_name(item_name)
    if item:
        return jsonify(item.serialize)
    else:
        response = make_response(json.dumps('Invalid item name.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/catalog/<string:category_name>/category.json')
def catalog_items_json(category_name):
    cat = CategoryModel.get_by_name(category_name)
    if cat:
        return jsonify(cat.serialize)
    else:
        response = make_response(json.dumps('Invalid category name.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

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

    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object

        # On Heroku, we cannot read from the files
        # oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')

        # Read environment variables from Heroku env
        client_id = os.environ.get("client_id")
        client_secret = os.environ.get("client_secret")
        redirect_uri = os.environ.get("redirect_uris")
        scope=''

        oauth_flow = OAuth2WebServerFlow(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope)

        # oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print credentials

    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
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
        response = make_response(json.dumps(
                                            "Token's user ID doesn't match \
                                            given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
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
    login_session['credentials'] = credentials
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
    em = login_session['email']
    user_id = UserModel.get_by_email(user_email=em)
    # print 'user_id = %s' % user_id
    if user_id:
        login_session['user_id'] = user_id
    else:
        user = UserModel(username=login_session['username'], email=login_session['email'])
        user.create_user()
        login_session['user_id'] = user.id

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
    output += ' " style = "width: 200px; border-radius: 150px;"> '
    flash("You are now logged in as %s." % login_session['username'])
    return output


@app.route('/logout')
def gdisconnect():
    c = login_session.get('credentials')
    access_token = None
    if c:
        access_token = c.access_token

    print 'In gdisconnect access token is %s', access_token
#    print 'User name is: '
#    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result

    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        flash('Successfully disconnected.')
        return redirect(url_for('catalogList'))
    else:
        flash('Failed to revoke token for given user.')
        return redirect(url_for('catalogList'))

app.secret_key = os.environ.get('SECRET_KEY', 'some secret_key')
app.debug = True

if __name__ == "__main__":
    # app.secret_key = os.environ.get('SECRET_KEY', 'some secret_key')
    # app.debug = False
    # port = int(os.environ.get('PORT', 8899))
    app.run(port=5000)
