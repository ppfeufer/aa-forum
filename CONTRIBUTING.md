# Contributing

## Code Formatting

This app is utilizing the [Black](https://black.readthedocs.io/en/stable/the_black_code_style.html)
code style. Every commit has to adhere to it.

This repository uses [pre-commit](https://github.com/pre-commit/pre-commit) to
verify compliance with formatting rules. To use:

1. Install `pre-commit`.
2. From inside the `aa-forum` root directory, run `pre-commit install`.
3. You're all done! Code will be checked automatically using git hooks.

You can check if your code to commit adheres to the given style by simply running:
```shell
pre-commit
```

or to check all files:
```shell
pre-commit run --all-files
```

The following will be checked by `pre-commit`:

- no trailing whitespaces (excluded are: minified js and css, .po and .mo files)
- one, and only one, empty line at the end of every file (excluded are: minified js and css, .po and .mo files)
- line ending is LF
- code formatted according to black code style
- code conforms with flake8


## Contributing via pull requests

To contribute code via pull request, make sure that you fork the repository and branch
your changes from the `development` branch. Only pull requests towards the development
branch will be considered.

Please make sure you have signed the [License Agreement](https://developers.eveonline.com/resource/license-agreement)
by logging in at https://developers.eveonline.com before submitting any pull requests.


### Commits

Commit headers should be short (not longer than 70 characters) and precise. Use
the commit body for a more detailed explanation of the commit.

Commit headers should be prefixed to state what kind of commit it is.

- `[FEATURE] Foobar` When a new feature is introduced
- `[ADDED] Foobar` When something is added to the code base to enhance existing
  functions
- `[REMOVED] Foobar` When something is removed, like deprecated or unused code
- `[FIX] Foobar` For bug fixes or fixes in general. Ideally followed by an issue ID
- `[CHANGE] Foobar` When Code or appearance has been changed that doesn't fit in any
  of the other categories. Usually for changes in templates or optimisations in the
  Python code itself


### Test Coverage

Please make sure your contribution comes with tests covering your additions and
changes. We aim to provide a test coverage of well above 80% in this project. Pull
requests lowering the test coverage will not be considered for merging.

You can run tests locally via:
```shell
make coverage
```

The full tox-test suite can be run via:
```shell
tox
```
