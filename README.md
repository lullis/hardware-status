Tested only on Ubuntu 12.04 LTS, 64 bits.

To run/install:

  1. Clone this repository: `git clone ssh://github.com/lullis/hardware-status`
 
  2. Please create and activate a virtualenv *with site packages* (it
     is necessary to use system python's packages for use of system
     D-Bus): `$ virtualenv --system-site-packages hardware-status`

  3. Install django. `$ pip install django`
  4. Run syncdb: /path/to/hardware-status/src/manage.py syncdb
  5. runserver

There is no configuration database needed. The django app is already setup to use sqlite.
