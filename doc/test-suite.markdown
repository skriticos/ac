Quality Control
================

Steps to be taken between taggin a revision and releasing it, to avoid dissatisfying users.

Installation
------------

Install the release on a clean Python as shipped with the target operating system. Any missing dependencies?

TODO instructions for using virtualenv to this end. Wile has no idea.

Synchronization
---------------

* Sync, delete a series on the site, sync again. Does AniChou show that deletion?
* Out-comment login, rename ac.dat, set user name to crono22, sync. Does it crash?

###Unicode

Navigate to the following series in the GUI and check for broken characters or escaped entities:

* Maria Holic
* Hell's Angels

Regression tests
----------------

Look at old issues and test that they are *still* fixed.
