# Vislice
Projekt pri predmetu UVP. Namen tega projekta je poiskati najboljšo strategijo za ugibanje posameznih besed pri igri [vislice](https://en.wikipedia.org/wiki/Hangman_(game)).
Pr tem uporabljamo vse besede iz [SSKJ](https://www.fran.si/iskanje?page=2&FilteredDictionaryIds=130&View=1&Query=*).

## Navodila za uporabo
Projekt za delovanje potrebuje [python](https://www.python.org/) in nekatere
python [pakete](requirements.txt), ki jih lahko naložite s pomočjo ukaza:
`pip install -r requirements.txt`.

## Delo na projektu
Priprava okolja (na sistemih Windows):
* `py -m venv venv`
* `.\venv\Scripts\activate.bat` v CMD oziroma `.\venv\Scripts\Activate.ps1` v PowerShell.
* `pip install -r development.txt`
* `pre-commit install`
