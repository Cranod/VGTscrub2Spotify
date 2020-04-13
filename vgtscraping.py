from lxml import html
import requests

page = requests.get('https://www.franceinter.fr/emissions/very-good-trip/very-good-trip-09-mars-2020')
tree = html.fromstring(page.content)
phrase = tree.xpath('//*[@id="content"]/div[2]/div/div/article/p[2]')
print(phrase)