import pandas as pd

# ruta del fitxer
file_path = "data/Datasets.xlsx"

# carregar fulls excel
ventas = pd.read_excel(file_path, sheet_name="Ventas")
productos = pd.read_excel(file_path, sheet_name="Productos")
clientes = pd.read_excel(file_path, sheet_name="Clientes")
potencial = pd.read_excel(file_path, sheet_name="Potencial")

ventas = ventas[ventas["Valores_H"] != 0]
ventas = ventas[ventas["Unidades"] != 0]
ventas = ventas.drop(columns=["Num.Fact"])



productos = productos.rename(columns={"Id.Prod": "Id. Producto"})

print(potencial.columns.tolist())

ventas_v2 = ventas.merge(    
    productos[
            ["Id. Producto", "Familia_H", "Categoria_H", "Bloque analítico"]
    ],
    on="Id. Producto",
    how="left"
)

ventas_v3 = ventas_v2.rename(columns={"Categoria_H": "Categoria Productos", "Id. Cliente": "Id.Cliente"})

ventas_v3 = ventas_v3.merge(
    potencial[["Id.Cliente", "Categoria Productos", "Potencial_H"]],
    on=["Id.Cliente", "Categoria Productos"],
    how="left"
)

print()

print("\nVentas merge")
print(ventas_v3.head())

print("\n Id = 26")
print(ventas_v3[ventas_v3["Id.Cliente"] == 26].sort_values("Fecha"))
