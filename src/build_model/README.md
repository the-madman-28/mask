# Building a spacy model to detect PIIs and Sensitive information

To train the model, first modify the `config.cfg` with the train `[paths.train]` and evaluation `[paths.dev]` dataset path. Then run the command `python -m spacy train config.cfg --output .\new\path\for\model` on terminal from the folder OR simply run python script `build_model.py` by running `python build_model.py`.

:warning: Do not change the config unless you're aware of the settings. It is generated to train model on CPU for NER using [spacy website][spacyweb].

[spacyweb]: https://spacy.io/usage/training#quickstart