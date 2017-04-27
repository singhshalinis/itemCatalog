Item Catalog
============

What is it? (Functionality)
---------------------------
An application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to add, edit and delete their own items.


Last Update Date
-----------------
April 14, 2016


System Specific Notes
-----------------------
* Developed in Python 2.7 using Flask, Jinja and SQLAlchemy.
* Google as the authentication provider.
* SQLLite Database


Testing
----------
* The website is designed for all devices but has been tested only on Chrome browser on Desktop.

Package Details (files involved)
--------------------------------
Below is a brief description of the folders/files that have been used for this application.
1. models (folder): Contains the models used in the application.
    * ItemModel
    * CategoryModel
    * USerModel

2. static (folder): Contains the css and image files for the application.

3. templates (folder): Contains all Jinja templates.

4. catalog.py (file): The python file that receives and handles all requests.

5. categories.txt (file): Allows configuration of categories used in the system. Currently the app does not support managing the categories from web.

6. client_secrets.json (file): Needed by the system, but not provided here. For testing, local client_secrets.json file is needed.

7. catalog01.db (db file): It is created when the application receives request for the first time. Its an SQLLIte database file.

8. runtime.txt, requirements.txt, Procfile, uwsgi.ini are for deployment on Heroku and can be ignored.

How to get started
-------------------
1. Copy the code to local folder.

2. Set the environment by installing the required dependencies mentioned in requirements.txt file.

3. Provide the client_secrets.json file.

4. Access the website at http://localhost:5000.

5. Add, update, remove categories by changing the categories.txt file. Due to the design, this will only reflect when we remove catalog01.db file and restart.

Functionalities
---------------
The app allows below functionalities as of now:
1. Allows login using Google sign in button.
2. Lists all categories and recent items available in the application.
3. Provides details about items, and allows edit and delete of items for logged in users.
4. Provides below JSON endpoints:
    * /catalog/catalog.json: Lists all categories and all items in them.
    * /catalog/items.json: Lists all items.
    * /catalog/<string:item_name>/item.json: Details of one item.
    * /catalog/<string:category_name>/category.json: All items in a category.
    * e.g. http://localhost:5000/catalog/Shoes/category.json


Known issues
------------
* Deployed on Heroku at - http://itemcatalog01.herokuapp.com/. But the login with Google is not working on Heroku due to below error.

      ...
      File "/app/.heroku/python/lib/python2.7/site-packages/httplib2/__init__.py", line 1518, in request
      2017-04-27T22:28:42.538518+00:00 app[web.1]:     connection_type = SCHEME_TO_CONNECTION[scheme]
      2017-04-27T22:28:42.538556+00:00 app[web.1]: KeyError: '"https'


In the browser, there is 503-Service Unavailable error. The error may be due to Heroku sending requests via https but the app currently does not support https.  

References, Credits & Acknowledgements
--------------------------------------
  * Udacity's lectures mostly for OAuth callback, login and logout functionalities.
  * https://www.udemy.com/rest-api-flask-and-python/learn/v4/overview
  * http://stackoverflow.com/
  * https://dashboard.heroku.com/apps
  * https://gist.github.com/milancermak/3451039 for different ways of getting OAuth credentials.
  * https://ryanprater.com/blog/2014/9/25/howto-authorize-google-oauth-credentials-through-a-heroku-environment
  * https://developers.google.com/api-client-library/python/guide/aaa_oauth


Contact Information
--------------------
For any comments, queries, issues, and bugs, please contact singhshalinis@gmail.com.
