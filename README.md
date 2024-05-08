# Vislice
Projekt pri predmetu UVP. Namen tega projekta je poiskati najboljšo strategijo za ugibanje posameznih besed pri igri [vislice](https://en.wikipedia.org/wiki/Hangman_(game)).
Pr tem uporabljamo "vse" besede iz [SSKJ](https://www.fran.si/iskanje?page=2&FilteredDictionaryIds=130&View=1&Query=*).

Za najboljšo strategijo definiramo strategijo, pri kateri bomo v najslabšem primeru naredili najmanjše število napačnih ugibanj.
Recimo, da imamo seznam 100 besed in dve strategiji. Recimo, da s prvo strategijo uganemo 95 besed brez napak, eno z dvema,
eno s tremi, eno s štirimi in eno s petimi napakami. Z drugo strategijo uganemo 1 besedo brez napak, 96 besed z eno napako, eno besedo
z dvema, eno s tremi in eno s štirimi. Potem je boljša 2. strategija.

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
