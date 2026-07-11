# SearchSport Analytics

Proyecto de ciencia de datos orientado al análisis de reservas y cancelaciones en una plataforma de arriendo de canchas deportivas.

La solución integra un pipeline ETL, un dashboard interactivo, un modelo predictivo de cancelación y una API REST desplegable mediante Docker.

---

## Objetivo del proyecto

Analizar el comportamiento de reservas deportivas y estimar el riesgo de cancelación según variables operativas como deporte, comuna, horario, mes y condición climática.

El proyecto busca responder preguntas como:

- ¿Qué deportes concentran más ingresos y cancelaciones?
- ¿En qué comunas se producen más cancelaciones?
- ¿En qué horarios existe mayor demanda?
- ¿Cómo cambia el comportamiento entre días despejados y días de lluvia/frío?
- ¿Qué reservas presentan mayor probabilidad de cancelarse?

---

## Dataset

El proyecto utiliza un dataset sintético realista construido para simular la operación de SearchSport.

Archivos principales:

- `canchas_searchsport.csv`: catálogo de canchas deportivas.
- `reservas_historicas_searchsport.csv`: historial transaccional de reservas.

Características generales:

- 300 canchas deportivas.
- 4.000 reservas históricas.
- Deportes: Futbolito, Pádel, Futsal, Tenis y Básquetbol.
- Comunas de Santiago.
- Estados de reserva: Completada y Cancelada.
- Variable climática derivada: Despejado o Lluvia/Frio.

---

## Estructura del proyecto

```text
analisis-searchsport-
├── api/
│   ├── __init__.py
│   └── app.py
├── models/
│   ├── modelo_cancelaciones.py
│   └── modelo_cancelaciones.pkl
├── outputs/
│   ├── metricas_modelos.csv
│   ├── matriz_confusion.csv
│   └── reporte_mejor_modelo.txt
├── dashboard.py
├── datos.py
├── canchas_searchsport.csv
├── reservas_historicas_searchsport.csv
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── README.md
Componentes principales
1. Pipeline ETL

El pipeline realiza la carga, transformación y consolidación de datos provenientes de reservas históricas y catálogo de canchas.

Transformaciones principales:

Unión entre reservas y canchas mediante id_cancha.
Conversión de fechas.
Creación de variables temporales: mes, hora y día de semana.
Creación de variable climática.
Preparación de datos para visualización y modelamiento.
2. Dashboard interactivo

El dashboard fue desarrollado con Streamlit y permite analizar:

KPIs generales de reservas, cancelaciones e ingresos.
Reservas por horario.
Cancelaciones por comuna.
Evolución mensual de cancelaciones.
Comparación entre días despejados y días de lluvia/frío.
Filtros por comuna, deporte y condición climática.

Ejecución local:

streamlit run dashboard.py

URL local:

http://localhost:8501
3. Modelo predictivo

Se entrenó un modelo supervisado para predecir si una reserva será cancelada o completada.

Variable objetivo:

estado_reserva

Variables utilizadas:

deporte
comuna
condición climática
hora
mes
día de semana
fin de semana
precio por hora
monto pagado

El modelo final permite estimar la probabilidad de cancelación y clasificar el riesgo operativo como bajo, medio o alto.

Ejecución del entrenamiento:

python models/modelo_cancelaciones.py

Archivos generados:

outputs/metricas_modelos.csv
outputs/matriz_confusion.csv
outputs/reporte_mejor_modelo.txt
models/modelo_cancelaciones.pkl
4. API REST

La API fue desarrollada con FastAPI y expone endpoints para consultar métricas y realizar predicciones.

Ejecución local:

uvicorn api.app:app --reload --port 8000

Swagger:

http://localhost:8000/docs

Endpoints principales:

GET /health
GET /metricas
GET /matriz-confusion
POST /predict

Ejemplo de predicción:

{
  "deporte": "Padel",
  "comuna": "Maipu",
  "condicion_clima": "Lluvia/Frio",
  "hora": 20,
  "mes": 7,
  "dia_semana": 4,
  "fin_de_semana": 0,
  "precio_por_hora": 32000,
  "monto_pagado": 32000
}

Respuesta esperada:

{
  "prediccion": "Cancelada",
  "probabilidad_cancelacion": 0.7168,
  "riesgo_operativo": "Alto"
}
Instalación local

Crear entorno virtual:

python -m venv venv

Activar entorno en Windows:

venv\Scripts\activate

Instalar dependencias:

pip install -r requirements.txt
Ejecución con Docker

Construir y levantar servicios:

docker compose up --build

Servicios disponibles:

Dashboard: http://localhost:8501
API Swagger: http://localhost:8000/docs

Para detener los servicios:

docker compose down
Evidencias esperadas

Para la entrega se consideran las siguientes evidencias:

Dashboard funcionando en localhost:8501.
API documentada en localhost:8000/docs.
Endpoint /predict retornando predicción.
Contenedores ejecutándose mediante Docker Compose.
Archivos de métricas del modelo generados en /outputs.
Tecnologías utilizadas
Python
Pandas
Streamlit
Plotly
Scikit-learn
FastAPI
Uvicorn
Docker
Docker Compose
Conclusión

SearchSport Analytics permite transformar datos transaccionales en información accionable para la toma de decisiones. La solución permite analizar patrones de cancelación, identificar horarios y comunas críticas, visualizar indicadores operativos y estimar el riesgo de cancelación mediante un modelo predictivo.

Como mejora futura, el análisis podría evolucionar hacia un modelo predictivo más robusto, incorporando datos climáticos reales en tiempo real, historial de usuarios y variables adicionales del recinto deportivo.


---

## Ejecución en Windows

### Opción 1: Ejecutar con Docker

Requiere tener Docker Desktop abierto.

```powershell
git clone URL_DEL_REPOSITORIO
cd analisis-searchsport-
docker compose up --build

Abrir en el navegador:

Dashboard: http://localhost:8501
API Swagger: http://localhost:8000/docs

Para detener:

docker compose down

Si docker compose no funciona, verificar:

docker --version
docker compose version

### Opción 2: Ejecutar sin Docker en Windows

Recomendado usar Python 3.11 o 3.12.  
Si Python 3.13 da problemas instalando pandas, usar Docker o instalar Python 3.11.

Crear entorno virtual:

```powershell
python -m venv venv

Activar entorno:

venv\Scripts\activate

Actualizar instaladores:

python -m pip install --upgrade pip setuptools wheel

Instalar dependencias:

pip install -r requirements.txt

Si se queda pegado instalando pandas, usar esta alternativa:

pip install pandas streamlit plotly Faker scikit-learn joblib fastapi uvicorn pydantic requests

Ejecutar la API en una terminal:

python -m uvicorn api.app:app --reload --port 8000

Abrir:

http://localhost:8000/docs

Ejecutar el dashboard en otra terminal:

venv\Scripts\activate
python -m streamlit run dashboard.py

Abrir:

http://localhost:8501

---

## Mejor ajuste para tu `requirements.txt`

Para evitar ese problema en otros PC, si lo van a ejecutar sin Docker, conviene dejar el `requirements.txt` **sin versiones fijas**:

```txt
numpy
pandas
streamlit
plotly
Faker
scikit-learn
joblib
fastapi
uvicorn
pydantic
requests