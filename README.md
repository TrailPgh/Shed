# Introduction

This web app is a Django/Python project intended to be used for 
any python-based code that TrailPgh wants to deploy.

Our first use will be GPS-related functionality.


## Shed: Where tools are stored

Python was chosen because its what Ricky already has some 
code written in, it's easy to install and use, its popular and free,
and its an excellent choice for data-related projects.

Django was chosen because it's a web framework that is easy to 
use and has a lot of documentation, it is popular and has a vast
community and ecosystem, and also because its a full-featured full-stack
web appplciation framework that includes tooling for not just HTTP handler
functions and UI templates, but also database models, authentication, an
ORM (object-relational mapper), and more. As opposed to Flask, which is a 
microframework, and does not include all the tooling that Django does.

# Code Policy

## Current

### Style

This project follows the 
[Django Coding Style Standards](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/).
* [black](https://pypi.org/project/black/) is used for formatting
* [isort](https://pypi.org/project/isort/) is used for sorting imports
* [pre-commit](https://pypi.org/project/pre-commit/) is used to enforce at commit time via a git pre-commit hook:
  * use of black for style
  * use of isort for import sorting

### Static Analysis (Linting)

Static analysis means checking the code without actually running it.
It checks for errors, may enforce a coding standard,
warns about unused variables,
looks for code smells,
and can make suggestions about how the code could be improved to be
less error-prone.

The static analysis tool we use is called [pylint](https://pypi.org/project/pylint/).
Pylint is a popular Python static analysis tool and the one recommended by
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

Pylint is a static code analyzer for Python
Pylint analyses your code without actually running it. It checks for errors, 
enforces a coding standard, looks for code smells, and can make suggestions about how
the code could be refactored.

### Some day?

Maybe one day we'll use:
* Mypy for type checking
* Flake8 for linting

### Resources

* [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
  * This focuses less on code style and formatting, though it does have some 
good advice on how to write good code. It focuses more on linting, semantics, 
and other static code quality properties.
* [Django Coding Style Standards](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)

