# What Happened?

A project started in a moment of frustration and lack of satisfaction about the possibilities to store and share character sheets for TTRPG online, in a good way.

While there are great services available for certain games, others were lacking in features and/or usability.

This will probably be no different. The software is written to satisfy the authors need, at least for now. But might grow in the future.

## Features

### Implemented

* User registration, login and password reset.
* Creation and basic editing of a single type of character sheet.

### To be implemented soon

* Sharing of character sheets.
* Completion of sheet for one ruleset.

### Future endeavors

* Better styling.
* Handling campaigns.
* Support for handouts.
* Websockets for dynamically updated views.

In its current state it can not be recommended to anyone, and instructions for setting up will not yet be provided. However, if you do test it, and find something that needs to be fixed, or you have a fix, issues and pull requests are welcome.

Come back later.

*Cthulhu fhtagn.*

## Development and testing

To get started, clone the project with git.

### Prerequisites

* `make` (probably the GNU variety)
* `node` and `npm`
* Python 3

### Setup and build

The following command sets up dependencies for you, and builds and runs the
Flask app. See the terminal output for the URL where it can be reached.

`$ make`

### Notes

#### How to only run the setup part

`$ make setup`

This creates a Python virtual environment for you. All the make targets will
activate it as needed, but feel free to activate it in your shell if you want or
need to:

`$ . .venv/bin/activate`

or if you're running Fish:

`$ . .venv/bin/activate.fish`

#### Cleaning

`$ make clean`

will clean out the build artefacts.
