import os
from searchSite import Driver, citilink, regard, dnsshop, ozon
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import column_index_from_string as columnIndex
from multiprocessing.pool import ThreadPool

def search(func, cells):
    """Поиск по списку ячеек с запросами из файла. Принимает функцию поиска и список ячеек."""
    driver = Driver(headless = False) # Инициализация вебдрайвера
    driver.start()
    result = []
    for cell in cells:
        res = [i for i in func(driver, cell.get('value'))] # Вызывов функции поиска с передачей вебдрайвера и текста поискового запроса. Результат собираем в список.
        result.append({'row': cell.get('row'), 'txt': cell.get('value'), 'res': res}) # Формируем словарь с номером строки ячейки, текстом запроса и результатом поиска.
    driver.stop()
    return result

def main():
    filePath = 'D:/MyProject/Итоговый реестр ШАБЛОН_2.xlsx'
    file = load_workbook(filePath) # Загружаем в память книгу xlsx
    sheet = file['Отчет'] # Открываем лист книги
    cells = list(filter(lambda x: x.data_type == 's', sheet['B'][6:])) # Выборка всех яцеек с запросами из столбца 'B' начиная с 6 строки
    searchQuery = []
    for cell in cells: # Бежим по столбцу необходимых позиций
        cellFootnote = sheet.cell(row = cell.row, column = columnIndex('C')) # Получаем ячейку примечание с текущей строки
        query = cellFootnote.value if cellFootnote.data_type == 's' else cell.value # Берем значение со столбца примечание, если не заполнено берем значение со столбца необходимых позиций
        searchQuery.append({'row': cell.row, 'value': query})
    pool = ThreadPool(processes=4) # Инициализация пула на 4 потока.
    processes = [
        {'column': 'H', 'proc': pool.apply_async(search, [citilink.search, searchQuery])}, # Славарь с указанием колонки для записи результата и ссылкой на поток поиска по сайту.
        {'column': 'N', 'proc': pool.apply_async(search, [dnsshop.search, searchQuery])},
        {'column': 'T', 'proc': pool.apply_async(search, [regard.search, searchQuery])},
    ]
    for proc in processes:
        for result_proc in proc.get('proc').get(): # Получаем результат выполнения потока
            result_txt="\n".join(map(lambda x: f"{x.get('name')} - Цена: {x.get('price')}", result_proc.get('res'))) # Формируем строку результата поска.
            wcell = sheet.cell(row = result_proc.get('row'), column = columnIndex(proc.get('column'))) # Получаем ячейку в книге для записи результата.
            wcell.font = Font(name='Times New Roman', size=11)
            sheet.row_dimensions[result_proc.get('row')].height = 70
            wcell.value = result_txt if result_txt else 'Нет' # Записываем результат в ячейку
    file.save(filePath)

if __name__ == '__main__':
    main()
