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

print("\nVentas merge")
print(ventas.head())

print("\nVentas merge")
print(productos.head())

productos = productos.rename(columns={
    "Id.Prod": "Id. Producto"
})

ventas_v2 = ventas.merge(    
    productos[
        ["Id. Producto", "Familia_H"]
    ],
    on="Id. Producto",
    how="left"
    )


print("\nVentas merge")
print(ventas_v2.head())

print("\n Id = 26")
print(ventas_v2[ventas_v2["Id. Cliente"] == 26].sort_values("Fecha"))