# Vislice
Projekt pri predmetu UVP. Namen tega projekta je poiskati najboljšo strategijo za ugibanje posameznih besed pri igri [vislice](https://en.wikipedia.org/wiki/Hangman_(game)).
Pr tem uporabljamo "vse" besede iz [SSKJ](https://www.fran.si/iskanje?page=2&FilteredDictionaryIds=130&View=1&Query=*).

## Navodila za uporabo
Projekt za delovanje potrebuje [python](https://www.python.org/) in nekatere
python [pakete](requirements.txt), ki jih lahko naložite s pomočjo ukaza:
`pip install -r requirements.txt`.

### Podatki
Podatki so bili pobrani s [SSKJ](https://www.fran.si/iskanje?FilteredDictionaryIds=130&View=1&Query=%2A). Shranjeni
so v `data/sskj_words_static.txt`. Podatke je možno dobiti tudi s pomočjo skripte `vislice.py sskjcollect`. (Glej
`vislice.py sskjcollect -h` za več informacij.) Z vklopljeno opcijo `--raw` je sortiranje drugačno (splošno sortiranje nizov).
Brez te opcije se sortira po slovenski abecedi.

## Delo na projektu
Priprava okolja (na sistemih Windows):
* `py -m venv venv`
* `.\venv\Scripts\activate.bat` v CMD oziroma `.\venv\Scripts\Activate.ps1` v PowerShell.
* `pip install -r development.txt`
* `pre-commit install`
