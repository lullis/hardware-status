To run/install:

0) Clone this repository: git clone ssh://github.com/lullis/hardware-status
1) Please create and activate a virtualenv *with site packages* (it is necessary to use system python's packages for use of system D-Bus): `$ virtualenv --system-site-packages hardware-status`
2) Install django. `$ pip install django`
3) Run syncdb: /path/to/hardware-status/src/manage.py syncdb
4) runserver

There is no configuration database needed. The django app is already setup to use sqlite.
