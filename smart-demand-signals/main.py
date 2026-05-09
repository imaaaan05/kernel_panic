import pandas as pd

# ruta del fitxer
file_path = "data/Datasets.xlsx"

# carregar fulls excel
ventas = pd.read_excel(file_path, sheet_name="Ventas")
productos = pd.read_excel(file_path, sheet_name="Productos")
clientes = pd.read_excel(file_path, sheet_name="Clientes")
potencial = pd.read_excel(file_path, sheet_name="Potencial")

# mostrar dades
print("VENTAS")
print(ventas.head())

print("\nPRODUCTOS")
print(productos.head())

print("\nCLIENTES")
print(clientes.head())

print("\nPOTENCIAL")
print(potencial.head())

print("\nCOLUMNES VENTAS")
print(ventas.columns)

print("\nCOLUMNES PRODUCTOS")
print(productos.columns)

print("\nCOLUMNES CLIENTES")
print(clientes.columns)

print("\nCOLUMNES POTENCIAL")
print(potencial.columns)