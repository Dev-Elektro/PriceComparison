from loguru import logger as log
from openpyxl import load_workbook
from openpyxl.styles import Font
from openpyxl.utils import column_index_from_string as columnIndex
from searchengine import SearchPool, QueryItem, runSearchBySite, Driver
from searchengine.presetsite import dnsshop, regard  # , citilink


def printLog(name: str, totalCount: int, currentPos: int):
    log.info(f"{name} {totalCount}\\{currentPos}")


def main():
    filePath = 'D:/MyProject/reestr.xlsx'
    file = load_workbook(filePath)  # Загружаем в память книгу xlsx
    sheet = file['Реестр']  # Открываем лист книги
    cells = list(filter(lambda x: x.data_type == 's',
                        sheet['D'][6:]))  # Выборка всех ячеек с запросами из столбца 'D' начиная с 6 строки
    searchQuery = []
    for cell in cells:  # Бежим по столбцу необходимых позиций
        if sheet.cell(row=cell.row, column=columnIndex('K')).data_type != 'n':
            continue
        cellFootnote = file['Запрос КП1'].cell(row=cell.row,
                                               column=columnIndex('H'))  # Получаем ячейку примечание с текущей строки
        query = cellFootnote.value if cellFootnote.data_type == 's' else cell.value  # Берем значение со столбца примечание, если не заполнено берем значение со столбца необходимых позиций
        searchQuery.append(QueryItem(rowNum=cell.row, value=query))
    searchPool = SearchPool(processes=4, headless=False)
    searchPool.addTask('DNS-shop', dnsshop, searchQuery, 'Реестр', 'K')
    searchPool.addTask('Regard', regard, searchQuery, 'Реестр', 'L')
    searchPool.setCallback(printLog)
    for searchPoolItem in searchPool:
        log.info(f"Search finish: {searchPoolItem.name} - write to column: {searchPoolItem.columnName}")
        for resultItem in searchPoolItem.result:  # Получаем результат выполнения поиска по сайту
            result_txt = "\n".join(map(lambda x: f"{x.name} - Цена: {x.price}",
                                       resultItem.listProduct))  # Формируем строку результата поска.
            wcell = sheet.cell(row=resultItem.rowNum, column=columnIndex(
                searchPoolItem.columnName))  # Получаем ячейку в книге для записи результата.
            wcell.font = Font(name='Times New Roman', size=11)
            sheet.row_dimensions[resultItem.rowNum].height = 70
            wcell.value = result_txt if result_txt else 'Нет'  # Записываем результат в ячейку
    file.save(filePath)


def writeFile(site_name, sheet_name, column_name, result_item):
    filePath = 'D:/MyProject/reestr.xlsx'
    file = load_workbook(filePath)  # Загружаем в память книгу xlsx
    log.info(f"Запись в файла для сайта: {site_name}, книга: {sheet_name}, колонка: {column_name}")
    sheet = file[sheet_name]  # Открываем лист книги
    result_txt = "\n".join(map(lambda x: f"{x.name} - Цена: {x.price}", result_item.listProduct))  # Формируем строку результата поска.
    wcell = sheet.cell(row=result_item.rowNum, column=columnIndex(column_name))  # Получаем ячейку в книге для записи результата.
    wcell.font = Font(name='Times New Roman', size=11)
    sheet.row_dimensions[result_item.rowNum].height = 70
    wcell.value = result_txt if result_txt else 'Нет'  # Записываем результат в ячейку
    file.save(filePath)
    log.info(f"Файл сохранен.")


def main2():
    filePath = 'D:/MyProject/reestr.xlsx'
    file = load_workbook(filePath)  # Загружаем в память книгу xlsx
    sheet = file['Реестр']  # Открываем лист книги
    cells = list(filter(lambda x: x.data_type == 's',
                        sheet['D'][6:]))  # Выборка всех ячеек с запросами из столбца 'D' начиная с 6 строки
    searchQuery = []
    for cell in cells:  # Бежим по столбцу необходимых позиций
        if sheet.cell(row=cell.row, column=columnIndex('K')).data_type != 'n':
            continue
        cellFootnote = file['Запрос КП1'].cell(row=cell.row,
                                               column=columnIndex('H'))  # Получаем ячейку примечание с текущей строки
        query = cellFootnote.value if cellFootnote.data_type == 's' else cell.value  # Берем значение со столбца примечание, если не заполнено берем значение со столбца необходимых позиций
        searchQuery.append(QueryItem(rowNum=cell.row, value=query))
    searchPool = SearchPool(processes=4, headless=False)
    searchPool.setCallback(printLog)
    searchPool.setWriteFile(writeFile)
    searchPool.addTask('DNS-shop', dnsshop, searchQuery, 'Реестр', 'K')
    searchPool.addTask('Regard', regard, searchQuery, 'Реестр', 'L')
    file.close()
    searchPool.wait()


if __name__ == '__main__':
    main2()
