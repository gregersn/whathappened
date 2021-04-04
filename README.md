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

To get started, clone the project with git. Now run:

```
$ make setup
```

This will have created a virtual environment for you. Feel free to activate it
if you want, but all the make targets will do it for you if you only use those.

You can run the flask app with:

```
$ make dev
```

See the output for the URL where it can be reached.

### Other shells

If you are using a different shell than `bash` or `zsh`, e.g. `fish`, the
activation might not work like that, but you can then do

`$ . venv/bin/activate.fish`

### Troubleshooting

### No stylesheet

You probably need to install sass.

### No javascript

You need to have typescript installed.
