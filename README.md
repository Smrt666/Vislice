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

Če izgleda, kot da koda ne deluje, ima napisanih nekaj testov. Ukaz `vislice.py test`
izvede dve vrsti testov, teste v `test/`, ki preverjajo pravilnost kode in teste v `collector/`,
ki preverijo, da se spletne strani s katerih se pobirajo podatki niso preveč spremenile.
Ti testi niso preveč zanesljivi, so pa dober prvi korak za odkrivanje težav.

### Podatki
Če nimate naloženega git lfs, lahko že zbrane podatke (in izračunano strategijo) naložite s pomočjo ukaza `./data/get_lf_no_lfs.py`. Če imate git lfs, potem lahko uporabite ukaza
`git lfs fetch --all` in `git lfs pull`.

Podatki so bili pobrani s [SSKJ](https://www.fran.si/iskanje?FilteredDictionaryIds=130&View=1&Query=%2A). Shranjeni
so v `data/nouns_si.txt`. Podatke je možno dobiti tudi s pomočjo skripte `vislice.py sskjcollect --nounsonly`. (Glej
`vislice.py sskjcollect -h` za več informacij.) Z vklopljeno opcijo `--raw` je sortiranje drugačno (splošno sortiranje nizov).
Brez te opcije se sortira po slovenski abecedi.

### Izračun strategije
Izračun strategije lahko poženemo z ukazom `vislice.py getstrategy {dolzina_besed} {datoteka_z_besedami}`.
Primer: `vislice.py getstrategy 5 data/nouns_si.txt --limit 150`. Za ta primer potrebuje program približno
8 sekund. Ta primer je relativno enostaven za računati, tako da program ni primeren za velike količine podatkov.
(Ali tako oblikovane, da je težko poiskati najboljšo strategijo in izločiti slabše.)

Z upoštevanjem dodatnega pravila, ki se pogosto uporablja pri vislicah, to je namig s prvo črko, postanejo podatki obvladljivi.
S pomočjo ukaza `vislice.py hintstrat data/nouns_si.txt --output data/hintstrat.json` lahko izračunamo strategijo
s predpostavko o namigu prve črke. To pomeni, da se razkrije prva črka in kje vse se pojavi v besedi. Program je
izračunal strategijo v nekaj več kot 8 urah, z maksimalno porabo pomnilnika okrog 3 GB.

## Delo na projektu
Priprava okolja (na sistemih Windows):
* `py -m venv venv`
* `.\venv\Scripts\activate.bat` v CMD oziroma `.\venv\Scripts\Activate.ps1` v PowerShell.
* `pip install -r development.txt`
* `pre-commit install`

Projekt nekatere datoteke shranjuje tudi na Git Large File Storage. O namestitvi si lahko
preberete na [https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage).
