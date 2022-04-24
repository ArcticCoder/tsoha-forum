# Keskustelusovellus - Vili Sinervä
*Idea [kurssimateriaalin](https://hy-tsoha.github.io/materiaali/aiheen_valinta/) esimerkistä "Keskustelusovellus".* 

## Konsepti

Alusta, jonne käyttäjät voivat luoda keskusteluketjuja eri aiheisiin liittyvillä alueilla. Perinteinen foorumi.

## Toteutetut ominaisuudet
* Sisään-/uloskirjautuminen ja uuden käyttäjän luominen
* Erikseen tavalliset käyttäjät ja ylläpitäjät
* Käyttäjä näkee sovelluksen etusivulla listan alueista sekä jokaisen alueen ketjujen ja viestien määrän ja viimeksi lähetetyn viestin ajankohdan.
	* Avaamalla alueen näkee kaikki alueen ketjut viimeisimmän viestin ajankohdan mukaan
* Ylläpitäjä voi lisätä ja poistaa keskustelualueita.
* Käyttäjä voi luoda alueelle uuden ketjun antamalla ketjun otsikon ja aloitusviestin sisällön
* Käyttäjä voi kirjoittaa uuden viestin olemassa olevaan ketjuun.
* Käyttäjä voi poistaa oman ketjun tai viestin.
* Ylläpitäjä voi poistaa yksittäisiä viestejä tai kokonaisia ketjuja

## Testaaminen Herokussa
Ohjelman uusin versio löytyy [Herokusta](https://secure-thicket-61219.herokuapp.com/). Huomioi, että vain yllämainittu rajallinen määrä ominaisuuksia on toteutettu. Testaamisen mahdollistamiseksi alustalle on luotu valmiiksi muutama (tyhjä) alue ja testauskäyttöön soveltuva väliaikainen ylläpitäjä-tili käyttäjänimellä admin ja salasanalla TestiAdmin

## Suunniteltuja ominaisuuksia
* Käyttäjä voi muokata luomansa ketjun otsikkoa sekä lähettämänsä viestin sisältöä. Muokkauksesta jää muille näkyvä jälki
* Käyttäjä voi etsiä kaikki ketjut, joiden otsikossa on annettu sana.
* Käyttäjä voi etsiä kaikki viestit, koko sivulta tai tietystä ketjusta, joiden osana on annettu sana.
* Käyttäjä voi lähettää yksityisviestejä toisille käyttäjille ja estää yksityisviestit tietyltä käyttäjältä
