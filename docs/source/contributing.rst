Contributing
============

This guide is meant for members of NetLab who want to add their code to ``labutils``.
If to contribute to ``labutils``, do the following:

* Make sure you're a "collaborator" on the GitHub repo.
* Pull the latest version of ``labutils``.
* Write and document your code. (See existing functions for examples of how to document functions. Documentation is important so that other people know how to use your function. Any functions with documentation string will automatically be included in the ReadTheDocs page.)
* Add your code to the appropriate ``.py`` file. If your code doesn't make sense in any of the existing files, add it to ``misc.py`` or start a new ``.py`` file.
* If you create a new file, add it to ``__init__.py``.
* Add any functions, classes, submodules, etc. to ``./docs/source/api_ref.rst``.
* Push your changes! Anyone who pulls the latest version will be able to import your code. Documented functions will be automatically added to the API documentation.
