# 📡 Smart Demand Signals — Inibsa Hackathon

Motor estadístico predictivo de demanda comercial con arquitectura desacoplada FastAPI + Streamlit.

---

## ¿Qué es este proyecto?

**Smart Demand Signals** es una herramienta de inteligencia comercial diseñada para detectar automáticamente señales de riesgo y oportunidad en la cartera de clientes de Inibsa. A partir del historial transaccional de cada cliente, el motor estadístico identifica patrones anómalos —clientes que han dejado de comprar, que compran menos de lo habitual, o que están en una ventana de captura frente a la competencia— y los prioriza con un score de riesgo accionable.

El sistema se compone de dos servicios independientes:

- **Backend (FastAPI)** — pipeline de datos + motor estadístico + API REST.
- **Frontend (Streamlit)** — interfaz corporativa que consume el backend y permite al equipo comercial registrar feedback en tiempo real.

---

## Estructura del proyecto

```
kernel_panic/
├── Smart_Demand_Signals/
│   ├── main.py                 # Backend FastAPI (motor estadístico + API REST)
│   ├── app.py                  # Frontend Streamlit (UI corporativa)
│   ├── visual_components.py    # Dashboard de analítica avanzada (Plotly)
│   ├── clean_data.py           # Script auxiliar de preparación del CSV
│   ├── requirements.txt        # Dependencias del proyecto
│   └── data/
│       └── database_clean.csv  # Dataset transaccional de ejemplo
└── readme.md
```

---

## Arquitectura

```
┌─────────────────────┐        HTTP (REST)        ┌──────────────────────────┐
│  Streamlit Frontend │ ──────────────────────────▶│   FastAPI Backend        │
│  app.py             │                            │   main.py                │
│  :8501              │ ◀─────────────────────────  │   :8000                  │
│                     │      JSON (alerts)          │                          │
│  visual_components  │                            │  Pipeline:               │
│  .py                │                            │  1. Ingestión CSV        │
└─────────────────────┘                            │  2. Feature Engineering  │
                                                   │  3. Motor Estadístico    │
                                                   │  4. Scoring (Log + P98)  │
                                                   │  5. Feedback Memory      │
                                                   └──────────────────────────┘
```

---

## Cómo funciona el motor estadístico

### 1. Ingestión y limpieza de datos
El backend acepta el CSV vía `POST /upload` y lo normaliza: renombra columnas, convierte tipos numéricos (coma → punto), parsea fechas y descarta filas inválidas.

### 2. Feature Engineering
Para cada par Cliente / Familia de producto se calculan:
- **Average_Monthly_Spend** — gasto mensual promedio.
- **Loyalty_Factor** — `Loyal` si el gasto supera el 85% del potencial del cliente, `Promiscuous` en caso contrario.
- **Days_Between** — días entre compras consecutivas.

### 3. Detección de alertas
El motor aplica reglas diferenciadas según el bloque analítico del producto:

| Bloque | Condición | Tipo de alerta |
|---|---|---|
| **Commodities** + Promiscuous | Sin compra > 365 días | Riesgo — Fugado >1 año |
| **Commodities** + Promiscuous | Días desde última compra ≥ media | Oportunidad — Ventana de Captura |
| **Technical** | Sin compra > 365 días | Riesgo — Fugado >1 año |
| **Technical** | Retraso > días esperados + 1.5σ | Riesgo — Retraso anómalo en tiempo |
| **Technical** | Última cantidad < media − 1σ | Riesgo — Caída drástica de volumen |

Los días esperados para productos técnicos se ajustan al volumen de la última compra (`expected_days = mean_days × last_qty / mean_qty`).

### 4. Scoring robusto
El score se calcula en tres pasos para evitar que clientes con alto valor económico distorsionen el ranking:

1. **Score bruto** — `Avg_Transaction_Value × (1 + Days_Delayed / Mean_Days) × Context_Multiplier`
2. **Cap P98** — se recortan outliers al percentil 98.
3. **Log-scaling + normalización** — `log1p(score)` normalizado al rango [1, 100].

**Multiplicadores de contexto:**
- Fugado >1 año → ×1.5
- Ventana de Captura → ×1.2
- Caída de Volumen → ×1.1
- Retraso anómalo → ×1.0

Solo se devuelven al frontend alertas con **score ≥ 20**.

### 5. Feedback en tiempo real
El equipo comercial puede marcar cada alerta como:
- `✅ Venta Recuperada` → penaliza el score un 50%.
- `❌ Falso Positivo` → penaliza el score un 90%.

El backend guarda este feedback en memoria y lo aplica en cada nueva llamada a `/upload`, recalibrando la prioridad sin necesidad de reentrenar ningún modelo.

---

## Requisitos previos

- Python **3.9 o superior**
- pip actualizado

```bash
python --version   # Debe ser 3.9+
pip install --upgrade pip
```

---

## Instalación

Instala todas las dependencias desde el fichero `requirements.txt`:

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install fastapi uvicorn python-multipart pandas numpy streamlit requests plotly
```

| Paquete | Para qué sirve |
|---|---|
| `fastapi` | Framework del backend REST |
| `uvicorn` | Servidor ASGI para correr FastAPI |
| `python-multipart` | Necesario para recibir archivos en FastAPI |
| `pandas` | Procesamiento de datos en el backend |
| `numpy` | Cálculos estadísticos (Log-scaling, P98) |
| `streamlit` | Framework del frontend |
| `requests` | Llamadas HTTP del frontend al backend |
| `plotly` | Gráficos interactivos en el dashboard |

> **Recomendado:** usa un entorno virtual para aislar las dependencias.
>
> ```bash
> python -m venv venv
> source venv/bin/activate      # Linux / macOS
> venv\Scripts\activate         # Windows
> pip install -r requirements.txt
> ```

---

## Ejecución

Necesitas **dos terminales abiertas** dentro de la carpeta `Smart_Demand_Signals/`.

### Terminal 1 — Backend (FastAPI)

```bash
uvicorn main:app --reload --port 8000
```

Verifica que esté corriendo visitando: [http://localhost:8000/health](http://localhost:8000/health)

Respuesta esperada:
```json
{"status": "ok", "memory_entries": 0}
```

La documentación interactiva de la API queda disponible en: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Terminal 2 — Frontend (Streamlit)

```bash
streamlit run app.py
```

Se abrirá automáticamente en el navegador: [http://localhost:8501](http://localhost:8501)

---

## Uso

1. Abre [http://localhost:8501](http://localhost:8501) en tu navegador.
2. En la barra lateral, sube el archivo `database_clean.csv` (o cualquier CSV con el formato correcto).
3. Ajusta la **fecha simulada** — el motor evaluará el estado de la cartera a esa fecha.
4. Usa el **filtro de riesgo mínimo** (slider) para ocultar alertas de baja prioridad.
5. Filtra por **Bloque Analítico** (`Commodities` / `Technical` / `Todos`) si es necesario.
6. Revisa las alertas en el **Panel de Intervención Comercial** y usa la columna **Feedback** para registrar:
   - `✅ Venta Recuperada` — el comercial ha recuperado la venta; penaliza el score un 50%.
   - `❌ Falso Positivo` — alerta incorrecta; penaliza el score un 90%.
7. El sistema recalibra automáticamente al hacer clic en cualquier acción.
8. Para resetear toda la memoria de feedback, pulsa **🗑️ Limpiar Feedback** en el sidebar.
9. Explora el **Advanced Commercial Intelligence** dashboard al final de la página para ver gráficos interactivos: distribución de riesgo, top clientes, histograma de inactividad y scatter de riesgo vs. retraso.

---

## Formato del CSV de entrada

El CSV debe usar **separador `;`** y **encoding `latin1`**. Columnas esperadas:

| Columna original | Descripción |
|---|---|
| `Id.Cliente` | Identificador único del cliente |
| `Fecha` | Fecha de la transacción (`DD/MM/YYYY` o similar) |
| `Familia_H` | Familia de producto |
| `Unidades` | Unidades compradas (decimal con coma) |
| `Valores_H` | Valor económico de la transacción (decimal con coma) |
| `Potencial_H` | Potencial de compra del cliente (puede estar vacío) |
| `Bloque analítico` | `Productos Técnicos` o `Commodities` |

---

## Endpoints del backend

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/upload` | Procesa el CSV + fecha simulada y devuelve alertas (score ≥ 20) |
| `POST` | `/feedback` | Registra la acción comercial de un par Cliente / Familia |
| `POST` | `/clear_feedback` | Borra toda la memoria de feedback |
| `GET` | `/health` | Comprueba que el servidor está activo |

### Ejemplo — llamada a `/upload`

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@data/database_clean.csv" \
  -F "sim_date=2025-12-31"
```

### Ejemplo — llamada a `/feedback`

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"Client_ID": "123", "Product_Family": "IMPLANTES", "Action": "✅ Venta Recuperada"}'
```

---

## Solución de problemas

**El frontend muestra "No se pudo conectar con el backend"**
→ Asegúrate de que el backend está corriendo en la Terminal 1 antes de abrir el frontend.

**Error al instalar dependencias en macOS con Apple Silicon**
```bash
pip install --no-binary :all: numpy pandas
```

**El puerto 8000 ya está en uso**
```bash
uvicorn main:app --reload --port 8001
# Y actualiza BACKEND_URL en app.py a http://localhost:8001
```

**El puerto 8501 ya está en uso**
```bash
streamlit run app.py --server.port 8502
```

**El CSV no se carga correctamente**
→ Verifica que el separador sea `;` y el encoding sea `latin1`. Puedes usar `clean_data.py` como referencia para preparar tu dataset desde el Excel original.

---

## Preparación del dataset (opcional)

Si partes del archivo Excel original (`Datasets.xlsx`), el script `clean_data.py` realiza el merge entre las hojas `Ventas`, `Productos`, `Clientes` y `Potencial` para generar el CSV de entrada. Edita la variable `file_path` con la ruta a tu Excel y ejecútalo:

```bash
python clean_data.py
```