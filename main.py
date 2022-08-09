from searchSite import Driver, citilink, dnsshop, ozon, regard


driver = Driver(headless = False)

s = input("Поиск: ")

driver.start()

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

driver.stop()
input("\nНажми Enter для завершения...")
quit()
