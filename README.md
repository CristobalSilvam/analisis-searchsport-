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

## Ejecución en otro computador / laboratorio

### Opción recomendada: ejecutar con Docker

Esta opción levanta automáticamente el dashboard de Streamlit y la API de FastAPI.

### 1. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
cd analisis-searchsport-
2. Verificar que Docker esté instalado
docker --version
docker compose version

Si ambos comandos responden correctamente, ejecutar:

docker compose up --build
3. Abrir la aplicación

Dashboard:

http://localhost:8501

API / Swagger:

http://localhost:8000/docs
4. Detener los servicios
docker compose down
Alternativa si Docker presenta problemas

En algunos laboratorios Docker puede no estar instalado, no estar abierto o no tener permisos suficientes. En ese caso, se puede ejecutar el proyecto localmente con Python.

1. Crear entorno virtual
python -m venv venv
2. Activar entorno virtual

En Windows:

venv\Scripts\activate

En Mac/Linux:

source venv/bin/activate
3. Instalar dependencias
pip install -r requirements.txt
4. Ejecutar la API

Abrir una terminal y ejecutar:

python -m uvicorn api.app:app --reload --port 8000

Luego abrir:

http://localhost:8000/docs
5. Ejecutar el dashboard

Abrir otra terminal, activar nuevamente el entorno virtual y ejecutar:

python -m streamlit run dashboard.py

Luego abrir:

http://localhost:8501
Solución de problemas frecuentes
Docker no reconoce el comando docker-compose

Usar el comando nuevo:

docker compose up --build

En vez de:

docker-compose up --build
El dashboard demora en cargar

Esperar entre 20 y 40 segundos. Streamlit puede tardar la primera vez mientras carga dependencias y datos.

Probar también:

http://127.0.0.1:8501
La predicción no funciona en el dashboard

Verificar primero que la API esté activa:

http://localhost:8000/docs

También se puede probar el endpoint:

POST /predict

Si la API no está corriendo, levantarla con:

python -m uvicorn api.app:app --reload --port 8000

o con Docker:

docker compose up --build
El dashboard se cae en Docker o aparece exited with code 139

Este error puede ocurrir por incompatibilidad de librerías o watcher de Streamlit en Docker/WSL.

Revisar que el docker-compose.yml tenga desactivado el file watcher:

command: >
  streamlit run dashboard.py
  --server.address=0.0.0.0
  --server.port=8501
  --server.headless=true
  --server.fileWatcherType=none
  --browser.gatherUsageStats=false

Si el problema continúa, usar la alternativa local:

python -m streamlit run dashboard.py

y dejar la API corriendo en otra terminal.

El modelo no responde o falta el archivo .pkl

Ejecutar nuevamente el entrenamiento:

python models/modelo_cancelaciones.py

Esto debería generar:

models/modelo_cancelaciones.pkl
outputs/metricas_modelos.csv
outputs/matriz_confusion.csv
outputs/reporte_mejor_modelo.txt

Luego reiniciar la API y el dashboard.

Archivos importantes que deben estar en el repositorio

Para que el proyecto funcione en otro computador, deben estar incluidos:

canchas_searchsport.csv
reservas_historicas_searchsport.csv
models/modelo_cancelaciones.pkl
outputs/metricas_modelos.csv
outputs/matriz_confusion.csv
outputs/reporte_mejor_modelo.txt
api/app.py
dashboard.py
requirements.txt
Dockerfile
docker-compose.yml
README.md

No se deben excluir del repositorio los archivos .csv, .pkl, models/ ni outputs/.

Verificación rápida antes de presentar

Ejecutar:

docker compose up --build

Confirmar que funcionen:

Dashboard: http://localhost:8501
API Swagger: http://localhost:8000/docs

En el dashboard, revisar que existan las tres pestañas:

Vista Ejecutiva (Negocio)
Vista Operativa (Canchas y Comunas)
Predicción de Cancelación

En Swagger, revisar que existan los endpoints:

GET /health
GET /metricas
GET /matriz-confusion
POST /predict