# pyalumni

This project is designed to be a quick and fairly simple alumni website. This is written in Python utilizing Flask, SQLAlchemy, Bootstrap, BootStrapTable, BlueImp and a couple of other projects. All licenses are MIT.

Key notes, there is a WSGI python.ini file present, this can be used as a webserver. Config items belong in pyalumni.conf. I've attempted to keep all options as simple, and as modular as possible.

As a note, this is my first real project and I will be working on and updating this as time goes on. There are large portions of this project that could be re-written to be more pythonic.

Todo items:
Install. If this becomes popular, a quick 'howto' regarding Nginx, UWSGI, and the python server.
Ease of use. Related to above, should this start getting use create an issue and I'll add a Dockerfile.
Security. The important stuff is secure (passwords), but ensure nothing is exposed past that, forms aren't vulnerable to redirects, all permissions are done, etc. May look at Flask-Security, but the project looks to be in limbo ATM.
Features. A key principal here is simplicity.
Unit Testing. This is important and tests will be added. Was focused on learning the language and framework first.
