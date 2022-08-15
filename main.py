from enum import auto
import os
from time import sleep
from tkinter.messagebox import YESNOCANCEL
from searchSite import Driver, citilink, regard, dnsshop, ozon
from web_main import website
from cgitb import text



#s = input("Поиск: ")




#read2_xlsx('Итоговый реестр ШАБЛОН_2.xlsx',"Отчет","c","b","Наименование необходимых позиций",citilink,"Отчет","h","Примечание")
#read2_xlsx('Итоговый реестр ШАБЛОН_2.xlsx',"Отчет","c","b","Наименование необходимых позиций",regard,"Отчет","n","Примечание")
#read2_xlsx('Итоговый реестр ШАБЛОН_2.xlsx',"Отчет","c","b","Наименование необходимых позиций",dnsshop,"Отчет","t","Примечание")

website()
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
