from bs4 import BeautifulSoup
import requests as req

#ouverture page very good trip
VGT = req.get("http://www.franceinter.fr/emissions/very-good-trip/very-good-trip-26-janvier-2017")
#test validité de la page
try:
    VGT.raise_for_status()
except Exception as exc:
    print('there was a proble: %s' %(exc))

#parsing html
VGTtext = BeautifulSoup(VGT.text, 'lxml')
#parsing html récent (bulletpoint)
elems = VGTtext.select('#content > div.page-diffusion > div > div > article > ul')


if elems == []:
    #si plus ancien parsing balise <p>""éé"""""""""""""""""""""""""""""""""""é
    elems = VGTtext.find_all('p')
    elems = VGTtext.select('#content > div.page-diffusion > div > div > article > p:nth-child(13)')
    if elems ==[]:
        #si encore plus ancien parsing <H3>
        elems = VGTtext.get_text()
        
        #elems = VGTtext.select('#content > div.page-diffusion > div > div > article > h3:nth-child(4)')
#print(elems)
#print(str(elems[0]))
print(elems[0].getText())