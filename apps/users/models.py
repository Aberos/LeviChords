"""Models of the users app.

The app uses the ``User`` and ``Group`` models from ``django.contrib.auth``.
This module exists so Django sends ``post_migrate`` to the app, which keeps
the access level groups up to date.
"""
