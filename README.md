# 100 Point Backend

Zero start build
--------------------------

Create a local PostgreSQL database with the following parameters:

```javascript
SERVER_NAME: 'travisci'
USER: 'postgres'
PASSWORD: ''
HOST: 'localhost'
PORT: [DEFAULT PORT]
```

_Feel free to edit these parameters in the settings.py file._

Create virtual environment with python 3.5+ as base interpreter

Run `pip install -r requirements.txt`

Finally, run `python manage.py migrate` and then `python manage.py runserver`

_Always make sure you are in the proper virtual environment_


Update from previous version
----------------------------

Run `python manage.py migrate` and then `python manage.py runserver`

Run
---

Just run `python manage.py runserver`

Documentation
-------------

This is the list of endpoints:

![List of endpoints](http://i.imgur.com/neueKnX.png)

This list can be accessed through `127.0.0.1:8000/docs`

Visit each link in the browser for a detailed description of each endpoint. Proper documentation will be created in the future.