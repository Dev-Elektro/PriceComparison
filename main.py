import os
import logging
from searchSite import Driver, dnsshop, regard#, citilink, ozon
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import column_index_from_string as columnIndex
from multiprocessing.pool import ThreadPool

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding='utf-8')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def search(func, cells):
    """Поиск по списку ячеек с запросами из файла. Принимает функцию поиска и список ячеек."""
    driver = Driver(headless = False) # Инициализация вебдрайвера
    driver.start()
    buf = [] # Буфер для найденых результатов, что бы дублирующиеся запросы не искать повторно.
    result = []
    for cell in cells: # Перебераем ячейки
        log.debug(f"Запрос: {cell.get('value')}")
        fromBuf = list(filter(lambda x: x[0] == cell.get('value'), buf)) # Проверяем результат для запроса в буфере
        if not fromBuf:
            log.debug(f"Запрос с сайта")
            res = [i for i in func(driver, cell.get('value'))] # Вызывов функции поиска с передачей вебдрайвера и текста поискового запроса. Результат собираем в список.
            buf.append([cell.get('value'), res])
        else:
            log.debug(f"Найден в буфере")
            res = fromBuf[0][1]
        result.append({'row': cell.get('row'), 'txt': cell.get('value'), 'res': res}) # Формируем словарь с номером строки ячейки, текстом запроса и результатом поиска.
    driver.stop()
    return result

def main():
    filePath = 'D:/MyProject/reestr.xlsx'
    file = load_workbook(filePath) # Загружаем в память книгу xlsx
    sheet = file['Реестр'] # Открываем лист книги
    cells = list(filter(lambda x: x.data_type == 's', sheet['D'][6:])) # Выборка всех яцеек с запросами из столбца 'D' начиная с 6 строки
    searchQuery = []
    for cell in cells: # Бежим по столбцу необходимых позиций
        #if sheet.cell(row = cell.row, column = columnIndex('K')).data_type != 'n': continue
        cellFootnote = file['Запрос КП1'].cell(row = cell.row, column = columnIndex('H')) # Получаем ячейку примечание с текущей строки
        query = cellFootnote.value if cellFootnote.data_type == 's' else cell.value # Берем значение со столбца примечание, если не заполнено берем значение со столбца необходимых позиций
        searchQuery.append({'row': cell.row, 'value': query})
    pool = ThreadPool(processes=4) # Инициализация пула на 4 потока.
    processes = [
        #{'column': 'H', 'proc': pool.apply_async(search, [citilink.search, searchQuery])}, # Славарь с указанием колонки для записи результата и ссылкой на поток поиска по сайту.
        {'column': 'K', 'proc': pool.apply_async(search, [dnsshop.search, searchQuery])},
        {'column': 'L', 'proc': pool.apply_async(search, [regard.search, searchQuery])},
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
