from enum import auto
import os
from time import sleep
from tkinter.messagebox import YESNOCANCEL
from searchSite import Driver, citilink, regard, dnsshop, ozon

from cgitb import text
from tkinter import filedialog
from tkinter import *
from numpy import append
import subprocess
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
import traceback

driver = Driver(headless = False)
driver.start()
#s = input("Поиск: ")


def write_file_index(index):
      f = open('index.txt','w')
      f.write(index)
      f.close()

def write_file_index_nach(index):
      f = open('index_0.txt','w')
      f.write(index)
      f.close()

def read_file_index():
      f = open('index.txt','r')
      rindex=f.read()
      f.close()
      return rindex

#(путь к файлу, имя листа, буква основной колонки, буква резервной колонки, имя столбца основного, имя функции поиска цены, имя столбца записи, буква столбца записи)
def read2_xlsx(xlsx, sheet_name, column_number,reserv_column, name_of_cell, function_search, name_sheet_write, name_write, name_col_write):
      check=False
      if not os.path.exists("index.txt"):
        open("index.txt", 'w').close()
      #xlsx='E:\\D disk\WorK\\bat source and compile\\Python\\priceZADA4a\\Итоговый реестр ШАБЛОН_2.xlsx'
      #sheet_name="Отчет"
      #column_number="h"
      #name_of_cell="Примечание"
      list_result=[]
      wb = load_workbook(xlsx)
      ws = wb[sheet_name]
      column=ws[column_number]
      dlina=len(column)
      #проверка наименования столбца
      for cell in column:
            if cell.value==name_of_cell:
                  #print(cell.value)
                  check=True
                  coordinatenachcalo=cell.row
                  print(coordinatenachcalo)
                  write_file_index_nach(str(coordinatenachcalo))
      #считывание данных
      for cell in column:
            if check==True:
                  if cell.value and cell.value!=name_of_cell:
                        print(cell.value)
                        index_of_table=read_file_index()
                        if index_of_table:
                              coordinate_now=int(index_of_table)
                        else:
                              coordinate_now=cell.row
                              write_file_index(str(coordinate_now))
                        if cell.row >= coordinate_now:
                                letter0=cell.column_letter
                                print(letter0, coordinate_now)
                                #list_result.extend([[cell.value,coordinate0]])
                                #print(list_result)

                                #result_search=search(cell.value)
                                buf = function_search.search(driver, cell.value)
                                #print("\nCitilink:\n")
                                citilink_result=""
                                for i in buf:
                                    print(f"{i.get('name')} - Цена: {i.get('price')}\n")
                                    citilink_result+=i.get('name')+" Цена:"+i.get('price')+"\n"
                                print(citilink_result)

                                if citilink_result:
                                    result_search=str(citilink_result)
                                    write2_xlsx('Итоговый реестр ШАБЛОН_2.xlsx',name_sheet_write,name_write,name_col_write,result_search,coordinate_now)
                                    coordinate_now=int(coordinate_now)+1
                                    write_file_index(str(coordinate_now))

                                else:
                                    print("Ищем по резервному названию")
                                    yacheika=str(reserv_column)+str(cell.row)
                                    planB=ws[yacheika]
                                    print (yacheika)
                                    print(planB.value)
                                    buf = function_search.search(driver, planB.value)
                                    #print("\nCitilink:\n")
                                    citilink_result=""

                                    for i in buf:
                                        print(f"{i.get('name')} - Цена: {i.get('price')}\n")
                                        citilink_result+=i.get('name')+" Цена:"+i.get('price')+"\n"
                                    print(citilink_result)

                                    if citilink_result:
                                        result_search=str(citilink_result)
                                        write2_xlsx('Итоговый реестр ШАБЛОН_2.xlsx',name_sheet_write,name_write,name_col_write,result_search,coordinate_now)
                                        coordinate_now=int(coordinate_now)+1
                                        write_file_index(str(coordinate_now))
                                    else:
                                        result_search="Нет"
                                        write2_xlsx('Итоговый реестр ШАБЛОН_2.xlsx',name_sheet_write,name_write,name_col_write,result_search,coordinate_now)
                                        coordinate_now=int(coordinate_now)+1
                                        write_file_index(str(coordinate_now))



      write_file_index("") #очищаем файл с индексом
      write_file_index_nach("") #очищаем файл с начальным индексом
      print(f"Выполнен поиск по магазину {function_search}")
      if list_result:

            return list_result
      else:
            null="Ничего не считано, необходимо проверить входные данные"
            return null


      #print(check)
      #print(list_result)





#(путь к файлу, имя листа, буква основной колонки, имя столбца основного, данные для записи, номер ячейки)
def write2_xlsx(xlsx, sheet_name, column_number, name_of_cell,list_zapis,nomer2):
      check=False
      #xlsx='E:\\D disk\WorK\\bat source and compile\\Python\\priceZADA4a\\Итоговый реестр ШАБЛОН_2.xlsx'
      #sheet_name="Отчет"
      #column_number="h"
      #name_of_cell="Примечание"
      #list_zapis=['ergegdyyhnjhju','cccccccc','ddddddddd','aaaaaaaaa','dddddddd','aaaaaaaaaaa','eddvegeggherhe']

      wb = load_workbook(xlsx)
      ws = wb[sheet_name]
      column=ws[column_number]

      for cell in column:
            if cell.value==name_of_cell:
                  coordinate=cell.row
                  letter=cell.column_letter
                  print(letter, coordinate)
                  check=True
      nomer=int(coordinate)+1

      if check==True:
            #nomer2=read_file_index()
            yacheyka=letter+str(nomer2)
            print(yacheyka)
            if list_zapis=="Нет":
                 ws[yacheyka]=list_zapis
                 megre_cell =ws[yacheyka]
                 megre_cell.fill = PatternFill('solid', fgColor="ffa500")
                 megre_cell.font = Font(name='Times New Roman', size=11)
                 rd = ws.row_dimensions[int(nomer2)] # get dimension for row
                 rd.height=70

            else:
                  megre_cell =ws[yacheyka]
                  ws[yacheyka]=list_zapis
                  megre_cell.font = Font(name='Times New Roman', size=11)
                  rd = ws.row_dimensions[int(nomer2)] # get dimension for row
                  rd.height=70

      wb.save(xlsx)
      print(f"Выполнена запись в файл")


read2_xlsx('Итоговый реестр ШАБЛОН_2.xlsx',"Отчет","c","b","Наименование необходимых позиций",citilink,"Отчет","h","Примечание")
read2_xlsx('Итоговый реестр ШАБЛОН_2.xlsx',"Отчет","c","b","Наименование необходимых позиций",regard,"Отчет","n","Примечание")
read2_xlsx('Итоговый реестр ШАБЛОН_2.xlsx',"Отчет","c","b","Наименование необходимых позиций",dnsshop,"Отчет","t","Примечание")
"""
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
driver.stop()
input("\nНажми Enter для завершения...")

quit()
