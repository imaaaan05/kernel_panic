# 📡 Smart Demand Signals — Inibsa Hackathon

Motor estadístico predictivo de demanda comercial con arquitectura desacoplada FastAPI + Streamlit.

---

## Estructura del proyecto

```
smart-demand-signals/
├── main.py              # Backend FastAPI (motor estadístico + API REST)
├── app.py               # Frontend Streamlit (UI corporativa)
├── database_clean.csv   # Dataset transaccional (subir desde la UI)
└── README.md
```

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

Instala todas las dependencias con un solo comando:

```bash
pip install fastapi uvicorn python-multipart pandas numpy streamlit requests
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

> **Recomendado:** usa un entorno virtual para aislar las dependencias.
>
> ```bash
> python -m venv venv
> source venv/bin/activate      # Linux / macOS
> venv\Scripts\activate         # Windows
> pip install fastapi uvicorn python-multipart pandas numpy streamlit requests
> ```

---

## Ejecución

Necesitas **dos terminales abiertas** en la misma carpeta del proyecto.

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
2. En la barra lateral, sube el archivo `database_clean.csv`.
3. Ajusta la **fecha simulada** y el **filtro de riesgo mínimo** según necesites.
4. El motor estadístico se ejecuta en el backend y devuelve las alertas accionables.
5. Usa la columna **Feedback** en la tabla para marcar:
   - `✅ Venta Recuperada` — penaliza el score un 50 %
   - `❌ Falso Positivo` — penaliza el score un 90 %
6. El sistema recalibra automáticamente en tiempo real.
7. Para resetear toda la memoria de feedback, pulsa **🗑️ Limpiar Feedback** en el sidebar.

---

## Endpoints del backend

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/upload` | Procesa el CSV + fecha simulada y devuelve alertas (score ≥ 20) |
| `POST` | `/feedback` | Registra la acción comercial de un par Cliente / Familia |
| `POST` | `/clear_feedback` | Borra toda la memoria de feedback |
| `GET` | `/health` | Comprueba que el servidor está activo |

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