# Lopputyön ovat tehneet yhteistyössä Kasper Rintala ja Jenni Lahti 
# Päivämäärä 27.8.2021

import os
import numpy as np
import ikkunasto as ik

elementit = {
    "ikkuna": None,
    "tekstilaatikko": None,
    "piirtoalue": None,
    "kuvaaja": None,
    "alikuvaaja": None,
    "x_data": [],
    "y_data": [],
    "pisteetx": [],
    "pisteety": []
}

def laske_parametrit(x1, y1, x2, y2):
    return (
        (y2 - y1)/(x2 - x1), 
        (x2 * y1 -x1 * y2)/(x2 -x1)
    )

def virhetied(viesti):
    ik.avaa_viesti_ikkuna("Error", viesti, True)

def main():
    elementit["ikkuna"] = ik.luo_ikkuna("Spektri")
    tekstikehys = ik.luo_kehys(elementit["ikkuna"], ik.VASEN)
    nappikehys = ik.luo_kehys(tekstikehys, ik.ALA)
    kuvaajakehys = ik.luo_kehys(elementit["ikkuna"], ik.OIKEA)
    elementit["piirtoalue"], elementit["kuvaaja"], elementit["alikuvaaja"] = ik.luo_kuvaaja(
        kuvaajakehys, 
        valitse_datapiste, 
        800, 
        600
    )
    elementit["alikuvaaja"].set_xlabel("Binding energy (eV)")
    elementit["alikuvaaja"].set_ylabel("Intensity (arbitrary units)")
    ik.luo_nappi(nappikehys, "Lataa kansio", lataa_kansio)
    ik.luo_nappi(nappikehys, "Piirrä data", piirra_data)
    ik.luo_nappi(nappikehys, "Poista lineaarinen tausta", poista_tausta)
    ik.luo_nappi(nappikehys, "Laske piikin intensiteetti", laske_intensiteetti)
    ik.luo_nappi(nappikehys, "Tallenna kuvaaja", tallenna_kuvaaja)
    ik.luo_nappi(nappikehys, "Sammuta", ik.lopeta)
    elementit["tekstilaatikko"] = ik.luo_tekstilaatikko(tekstikehys)
    elementit["piirtoalue"].draw()
    ik.kaynnista()
    
def lataa_kansio():
    kansio = ik.avaa_hakemistoikkuna("Valitse kansio")
    lukumaara = 0
    kineettisetenergiat = []
    intensiteettisumma = []
    elementit["x_data"] = []
    elementit["y_data"] = []
    alkuperainen = True
    try:
        tiedostot = os.listdir(kansio)
    except FileNotFoundError:
        pass
    else:
        for tiedosto in tiedostot:
            intensiteettisummaTEMP = []
            kineettisetenergiatTEMP = []
            if tiedosto.endswith(".txt") and tiedosto.startswith("measurement_"):
                tiedostoviittaus = os.path.join(kansio, tiedosto)
                with open(tiedostoviittaus) as tiedostokasittely:
                    tiedostoarvot = tiedostokasittely.readlines()
                    for i, esirivi in enumerate(tiedostoarvot):
                        rivi = esirivi.strip("\n").split(" ")
                        rivi[0] = float(rivi[0])
                        rivi[1] = float(rivi[1])
                        if len(rivi) == 2:
                            kineettisetenergiatTEMP.append(rivi[0])
                            intensiteettisummaTEMP.append(rivi[1])
                        else:
                            ik.kirjoita_tekstilaatikkoon(
                                elementit["teksilaatikko"],
                                ("Tiedostossa {} virhe, ohitetaan".format(tiedosto))
                            )
                            break
                    if alkuperainen:
                        kineettisetenergiat.extend(kineettisetenergiatTEMP)
                        intensiteettisumma.extend(intensiteettisummaTEMP)
                        lukumaara += 1
                        alkuperainen = False
                    else:
                        for i, _ in enumerate(intensiteettisumma):
                            intensiteettisumma[i] += intensiteettisummaTEMP[i]
                        intensiteettisummaTEMP = []
                        lukumaara += 1
        elementit["x_data"].extend(kineettisetenergiat)
        elementit["y_data"].extend(intensiteettisumma)
        ik.kirjoita_tekstilaatikkoon(
            elementit["tekstilaatikko"],
            "{} tiedostoa ladattiin".format(lukumaara)
        )

def piirra_data():
    if not (elementit["x_data"] and elementit["y_data"]):
        virhetied("Ei ladattua dataa, ei voida piirtää")
    else:
        elementit["alikuvaaja"].cla()
        elementit["alikuvaaja"].set_xlabel("Binding energy (eV)")
        elementit["alikuvaaja"].set_ylabel("Intensity (arbitrary units)")
        elementit["alikuvaaja"].plot(elementit["x_data"], elementit["y_data"])
        elementit["piirtoalue"].draw()

def pisteiden_valinta(f, n=2):
    piirra_data()
    elementit["pisteetx"] = []
    elementit["pisteety"] = []
    if f == 1:
        ik.kirjoita_tekstilaatikkoon(
            elementit["tekstilaatikko"], 
            "Valitse arvo kuvaajan alku- ja sitten loppupäästä"
        )
    elif f == 2:
        ik.kirjoita_tekstilaatikkoon(
            elementit["tekstilaatikko"], 
            "Valitse integroitavan välin alku- ja sitten loppupiste"
        )
    def silmukka():
        if len(elementit["pisteetx"]) < n:
            elementit["ikkuna"].after(1, silmukka)
        else:
            if f == 1:
                k, b = laske_parametrit(
                    elementit["pisteetx"][0], 
                    elementit["pisteety"][0], 
                    elementit["pisteetx"][1], 
                    elementit["pisteety"][1]
                )
                for j, _ in enumerate(elementit["y_data"]):
                    elementit["y_data"][j] -= ((elementit["x_data"][j] * k) + b)
                piirra_data()
            elif f == 2:
                integroitava_x = []
                integroitava_y = []
                for m, alkio in enumerate(elementit["x_data"]):
                    if elementit["pisteetx"][0] < alkio < elementit["pisteetx"][1]:
                        integroitava_x.append(alkio)
                        integroitava_y.append(elementit["y_data"][m])
                pinta_ala = np.trapz(integroitava_y, integroitava_x, 0.05)
                ik.kirjoita_tekstilaatikkoon(
                    elementit["tekstilaatikko"], 
                    "Pinta-ala välillä on {}".format(pinta_ala)
                )
            elementit["ikkuna"].after_cancel(silmukka)
    silmukka()
                
def poista_tausta():
    if not (elementit["x_data"] and elementit["y_data"]):
        virhetied("Ei ladattua dataa, ei voida suorittaa")
    else:
        pisteiden_valinta(1)

def laske_intensiteetti():
    if not (elementit["x_data"] and elementit["y_data"]):
        virhetied("Ei ladattua dataa, ei voida suorittaa")
    else:
        pisteiden_valinta(2)
        
def valitse_datapiste(event):
    elementit["pisteetx"].append(event.xdata)
    elementit["pisteety"].append(event.ydata)

def tallenna_kuvaaja():
    def tallenna():
        nimi = ik.lue_kentan_sisalto(tekstilaatikko)
        elementit["kuvaaja"].savefig(nimi + ".png")
        ik.kirjoita_tekstilaatikkoon(
            elementit["tekstilaatikko"], 
            "Tallennettu nimellä: {}".format(nimi)
        )
        peruuta()
    def peruuta():
        ik.poista_elementti(nimenvalitsija)
    if not (elementit["x_data"] and elementit["y_data"]):
        virhetied("Ei ladattua dataa, ei voida tallentaa")
    else:
        nimenvalitsija = ik.luo_ali_ikkuna("Valitse tiedoston nimi")
        kenttakehys = ik.luo_kehys(nimenvalitsija, ik.YLA)
        nappikehys = ik.luo_kehys(nimenvalitsija, ik.YLA)
        napitoikea = ik.luo_kehys(nappikehys, ik.OIKEA)
        ik.luo_tekstirivi(kenttakehys, "Tiedoston nimi:")
        tekstilaatikko = ik.luo_tekstikentta(kenttakehys)
        ik.luo_nappi(nappikehys, "Tallenna", tallenna)
        ik.luo_nappi(napitoikea, "Peruuta", peruuta)

if __name__ == "__main__":
    main()
