from enum import auto
import os
from time import sleep
from tkinter.messagebox import YESNOCANCEL
from searchengine import Driver, citilink, regard, dnsshop, runSearchBySite
from web_main import website
from cgitb import text


#s = input("Поиск: ")

#website("reestr")
website("one")

"""
buf = citilink.search(driver, s)
print("\nCitilink:\n")

for i in buf:
    print(f"{i.get('name')} - Цена: {i.get('price')}\n")


buf = regard.search(driver, s)
print("\nRegard:\n")

for i in buf:
    print(f"{i.get('name')} - Цена: {i.get('price')}\n")

buf = dnsshop.search(driver, s)
print("\nDNS-shop:\n")

for i in buf:
    print(f"{i.get('name')} - Цена: {i.get('price')}\n")

buf = ozon.search(driver, s)
print("\nOZON:\n")

for i in buf:
    print(f"{i.get('name')} - Цена: {i.get('price')}\n")
"""
#input("\nНажми Enter для завершения...")
quit()
