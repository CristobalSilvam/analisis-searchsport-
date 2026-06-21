import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta


# Fijamos una semilla
random.seed(82)
Faker.seed(82)

# Inicializamos Faker con configuración local de Chile
fake = Faker('es_CL')

print("Generando datos para SearchSport...")

#Catálogo de Canchas / Recintos (Simulación de Base de Datos SQL)
deportes_config = {
    'Futbolito': {'precio_min': 28000, 'precio_max': 42000},
    'Futsal': {'precio_min': 12000, 'precio_max': 22000},
    'Pádel': {'precio_min': 22000, 'precio_max': 45000},
    'Tenis': {'precio_min': 15000, 'precio_max': 28000},
    'Básquetbol': {'precio_min': 12000, 'precio_max': 22000}
}

# Comunas de Santiago para georreferenciar el problema
comunas_santiago = ['Cerrillos', 'Cerro Navia', 'Conchalí', 'El Bosque', 'Estación Central',
'Huechuraba', 'Independencia', 'La Cisterna', 'La Florida', 'La Granja',
'La Pintana', 'La Reina', 'Las Condes', 'Lo Barnechea', 'Lo Espejo',
'Lo Prado', 'Macul', 'Maipú', 'Ñuñoa', 'Pedro Aguirre Cerda',
'Peñalolén', 'Providencia', 'Pudahuel', 'Quilicura', 'Quinta Normal',
'Recoleta', 'Renca', 'San Joaquín', 'San Miguel', 'San Ramón',
'Santiago', 'Vitacura']

canchas = []

# Definimos el orden de los deportes y sus probabilidades (pesos)
lista_deportes = ['Futbolito', 'Pádel', 'Futsal', 'Básquetbol', 'Tenis']
# Pesos: Futbolito(40%), Pádel(25%), Futsal(20%), Basket(10%), Tenis(5%)
pesos_deportes = [40, 25, 20, 10, 5] 

for i in range(1, 301): #total de canchas en la plataforma
    # Usamos random.choices con los pesos definidos para forzar la distribución
    deporte = random.choices(lista_deportes, weights=pesos_deportes)[0]
    config = deportes_config[deporte]
    
    canchas.append({
        'id_cancha': i,
        'nombre_recinto': f"Complejo Deportivo {fake.first_name()} {random.randint(1,5)}",
        'deporte': deporte,
        'comuna': random.choice(comunas_santiago),
        'precio_por_hora': random.randint(config['precio_min'], config['precio_max'])
    })

df_canchas = pd.DataFrame(canchas)
df_canchas.to_csv('canchas_searchsport.csv', index=False)
print("Catálogo de canchas generado: 'canchas_searchsport.csv' (300 recintos)")


# Historial de Reservas (El archivo CSV de transacciones)
reservas = []
# Simularemos un año completo de transacciones (2025)
fecha_inicio = datetime(2025, 1, 1)

for i in range(1, 4001): # 4,000 reservas anuales
    # Fecha aleatoria durante el año
    dias_random = random.randint(0, 364)
    
    # Horarios con mayor ponderación en la tarde/noche (horas peak de arriendo)
    hora = random.choices([9, 11, 14, 16, 18, 19, 20, 21, 22], weights=[1, 1, 1, 2, 4, 5, 5, 4, 2])[0]
    minuto = random.choice([0, 30])
    fecha_reserva = fecha_inicio + timedelta(days=dias_random, hours=hora, minutes=minuto)
    
    cancha_seleccionada = random.choice(canchas)
    
    # --- LÓGICA DE NEGOCIO PARA EFECTO CLIMA ---
    # mayo, junio, julio, agosto concentran las lluvias.
    # Forzaremos que en esos meses la tasa de cancelación suba.
    mes = fecha_reserva.month
    if mes in [5, 6, 7, 8]:
        # 40% de probabilidad de cancelación en invierno (simulando días de lluvia)
        estado = random.choices(['Completada', 'Cancelada'], weights=[60, 40])[0]
    else:
        # 12% de probabilidad de cancelación el resto del año
        estado = random.choices(['Completada', 'Cancelada'], weights=[88, 12])[0]
    
    reservas.append({
        'id_reserva': i,
        'fecha_hora': fecha_reserva.strftime('%Y-%m-%d %H:%M:%S'),
        'id_cancha': cancha_seleccionada['id_cancha'],
        'cliente': fake.name(),
        'estado_reserva': estado,
        'monto_pagado': cancha_seleccionada['precio_por_hora']
    })

df_reservas = pd.DataFrame(reservas)
# Ordenamos cronológicamente para que el archivo simule un log real de auditoría
df_reservas = df_reservas.sort_values(by='fecha_hora')
df_reservas.to_csv('reservas_historicas_searchsport.csv', index=False)
print("Historial de transacciones generado: 'reservas_historicas_searchsport.csv' (4000 registros)")
print("\n¡Todo listo! Tienes la data estructurada para justificar tu pipeline ETL.")