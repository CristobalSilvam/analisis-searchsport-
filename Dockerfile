# Usamos una imagen oficial de Python ligera para optimizar el contenedor
FROM python:3.10-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos primero para aprovechar el caché de Docker
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código y los archivos CSV
COPY . .

# Exponemos el puerto que utiliza Streamlit
EXPOSE 8501

# Comando por defecto al levantar el contenedor
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]