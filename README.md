# imdb2filmtipset

A small script that transfers ratings from IMDb to Filmtipset.

## Installation

Built for python 3.4. Requirements are stored in requirements.txt. Use pip to install them.

Run as:
```
python imdb2filmtipset.py [ratings.csv]
```
If the `[ratings.csv]` argument is omitted then the latest ratings are downloaded from IMDb. The .csv file can
be downloaded from your ratings page on IMDb.


In settings.json settings are stored. You need to generate an user api key on filmtipset.
```json
{
  "filmtipset_key": "",
  "imdb_userid": "",
  "translation_mapping": [1, 1, 1, 1, 1, 2, 3, 4, 5, 5]
}
```

## Bugs and feature requests

Have a bug or a feature request? Please first search for existing and closed issues. If your problem or idea is not addressed yet, [please open a new issue](https://github.com/smoiz/imdb2filmtipset/issues).

## Authors

**smoiz**
