=====
Usage
=====

To use pystrava in a project:

First off you'll have to create your application on your `Strava profile <https://www.strava.com/settings/api>`_.
Give it a name and as website you can just use ``http://localhost.local/callback``
and in terms of Authorization Callback Domain, ``localhost.local`` will suffice.

Once created, you should have a ``client_id`` and a ``client_secret``.

You will also need to use a ``scope`` to get a token that has access to the resources.
Read more about scopes `here <https://developers.strava.com/docs/authentication/>`_

Scopes can be appended by using a comma. Let's assume we will use
``activity:write,profile:read_all`` as ``scope``.

.. code-block:: bash

    $ pip install pystrava

.. code-block:: python

    from pystrava import Strava
    import logging
    import os

    logging.basicConfig(level=logging.INFO)
    strava = Strava(client_id=os.environ['CLIENT_ID'],
                    client_secret=os.environ['SECRET'],
                    callback=os.environ['CALLBACK_URL'],
                    scope=os.environ['SCOPE'],
                    email=os.environ['EMAIL'],
                    password=os.environ['PASSWORD'])
    athlete = strava.get_athlete()
    print(athlete)

To read more on what available methods and features ``stravalib`` has, go to
this `link <https://pythonhosted.org/stravalib/usage/overview.html>`_.
