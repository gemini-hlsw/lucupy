# Lucupy

This package contains data structures and functions to support all the microservices that make up the Schedule app
for the Gemini Program Platform (and other auxiliary services such as Env and Resource)

## Installation

```
$ pip install lucupy
```

## Documentation

You can find our documentation [here](https://gemini-hlsw.github.io/lucupy/docs/lucupy/)

To add new changes to the doc is needed to force push to `gh-pages` branch to trigger an Actions.

See `.github/workflow/docs.yml`.

## Publishing

To build a new version, update the version number [here](https://github.com/gemini-hlsw/lucupy/blob/main/pyproject.toml)
and then execute:

```
$ poetry build && poetry publish
```

You will have to update `lucupy` in any other project that uses it by running:
```
$ pip install -U lucupy
```

## License

Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)

For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause
