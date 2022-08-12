import os
from searchSite import Driver, citilink, regard, dnsshop, ozon
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import column_index_from_string as columnIndex
from multiprocessing.pool import ThreadPool

def search(func, cells):
    driver = Driver(headless = False)
    driver.start()
    result = []
    for cell in cells:
        res = [i for i in func(driver, cell.value)]
        result.append({'row': cell.row, 'txt': cell.value, 'res': res})
    driver.stop()
    return result

def main():
    filePath = 'D:/MyProject/Итоговый реестр ШАБЛОН_2.xlsx'
    file = load_workbook(filePath)
    sheet = file['Отчет']
    cells = list(filter(lambda x: not x.value is None, sheet['C'][6:]))
    pool = ThreadPool(processes=4)
    processes = [
        {'column': 'H', 'proc': pool.apply_async(search, [citilink.search, cells])},
        {'column': 'N', 'proc': pool.apply_async(search, [dnsshop.search, cells])},
        {'column': 'T', 'proc': pool.apply_async(search, [regard.search, cells])},
    ]
    for proc in processes:
        for result_proc in proc.get('proc').get():
            result_txt="\n".join(map(lambda x: f"{x.get('name')} - Цена: {x.get('price')}", result_proc.get('res')))
            wcell = sheet.cell(row = result_proc.get('row'), column = columnIndex(proc.get('column')))
            wcell.font = Font(name='Times New Roman', size=11)
            sheet.row_dimensions[result_proc.get('row')].height = 70
            wcell.value = result_txt if result_txt else 'Нет'
    file.save(filePath)

if __name__ == '__main__':
    main()
