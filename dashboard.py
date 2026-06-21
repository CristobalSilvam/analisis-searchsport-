import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(page_title="Analisis SearchSport", layout="wide", initial_sidebar_state="expanded")

# CARGA Y TRANSFORMACIÓN DE DATOS 
@st.cache_data 
def load_data():
    df_canchas = pd.read_csv('canchas_searchsport.csv')
    df_reservas = pd.read_csv('reservas_historicas_searchsport.csv')
    
    # Merge de ambas fuentes
    df = pd.merge(df_reservas, df_canchas, on='id_cancha', how='left')
    
    # Transformaciones de fecha
    df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
    df['mes_num'] = df['fecha_hora'].dt.month
    df['hora'] = df['fecha_hora'].dt.hour
    
    nombres_meses = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 
                     7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
    df['mes_nombre'] = df['mes_num'].map(nombres_meses)
    
    # Simular la ingesta de la API del Clima
    df['condicion_clima'] = df['mes_num'].apply(lambda x: 'Lluvia/Frio' if x in [5, 6, 7, 8] else 'Despejado')
    
    return df

df_base = load_data()

#  BARRA LATERAL PARA FILTROS GLOBALES 
st.sidebar.title("Filtros Globales")
st.sidebar.markdown("Usa estos filtros para segmentar todo el dashboard.")

# Filtros dinámicos
comuna_filtro = st.sidebar.selectbox("Filtrar por Comuna:", options=['Todas'] + sorted(list(df_base['comuna'].unique())))
deporte_filtro = st.sidebar.selectbox("Filtrar por Deporte:", options=['Todos'] + sorted(list(df_base['deporte'].unique())))
clima_filtro = st.sidebar.radio("Condición Climática:", options=['Ambas', 'Despejado', 'Lluvia/Frio'])

# Aplicar filtros al DataFrame
df_filtrado = df_base.copy()
if comuna_filtro != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['comuna'] == comuna_filtro]
if deporte_filtro != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['deporte'] == deporte_filtro]
if clima_filtro != 'Ambas':
    df_filtrado = df_filtrado[df_filtrado['condicion_clima'] == clima_filtro]

# DISEÑO DE LA INTERFAZ PRINCIPAL 
st.title("SearchSport - Analisis")

# Validar que existan datos con los filtros aplicados
if df_filtrado.empty:
    st.warning("No hay datos para la combinación de filtros seleccionada. Intenta con otros parámetros.")
else:
    # Pestañas para diferenciar audiencias
    tab_ejecutiva, tab_operativa = st.tabs(["Vista Ejecutiva (Negocio)", "Vista Operativa (Canchas y Comunas)"])

    # PESTAÑA 1: VISTA EJECUTIVA
    with tab_ejecutiva:
        st.header("Resumen de Rentabilidad")
        
        # Cálculos de KPIs basados en los datos FILTRADOS
        ingresos_totales = df_filtrado[df_filtrado['estado_reserva'] == 'Completada']['monto_pagado'].sum()
        ingresos_perdidos = df_filtrado[df_filtrado['estado_reserva'] == 'Cancelada']['monto_pagado'].sum()
        tasa_cancelacion = (len(df_filtrado[df_filtrado['estado_reserva'] == 'Cancelada']) / len(df_filtrado)) * 100 if len(df_filtrado) > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Ingresos Generados (CLP)", f"${ingresos_totales:,.0f}")
        col2.metric("Pérdidas por Cancelación", f"${ingresos_perdidos:,.0f}", delta="- Fuga de capital", delta_color="inverse")
        col3.metric("Tasa de Cancelación Global", f"{tasa_cancelacion:.1f}%")

        st.divider()

        col_izq, col_der = st.columns(2)
        
        with col_izq:
            st.subheader("Ingresos vs Pérdidas por Deporte")
            # Gráfico de barras apiladas para ver qué deporte genera más plata pero también pierde más
            df_agrupado = df_filtrado.groupby(['deporte', 'estado_reserva'])['monto_pagado'].sum().reset_index()
            fig_ingresos = px.bar(df_agrupado, x='deporte', y='monto_pagado', color='estado_reserva',
                                  color_discrete_map={'Completada': '#2ca02c', 'Cancelada': '#d62728'},
                                  barmode='group', labels={'monto_pagado': 'Monto (CLP)', 'deporte': 'Deporte'})
            st.plotly_chart(fig_ingresos, use_container_width=True)

        with col_der:
            st.subheader("Impacto del Clima en Pérdidas Monetarias")
            
            # DataFrame que ignora el filtro de clima, pero mantien los de comuna y deporte para no perder el contexto.
            df_para_clima = df_base.copy()
            if comuna_filtro != 'Todas':
                df_para_clima = df_para_clima[df_para_clima['comuna'] == comuna_filtro]
            if deporte_filtro != 'Todos':
                df_para_clima = df_para_clima[df_para_clima['deporte'] == deporte_filtro]
            
            # Calcular las pérdidas con este nuevo DataFrame
            df_perdidas = df_para_clima[df_para_clima['estado_reserva'] == 'Cancelada'].groupby('condicion_clima')['monto_pagado'].sum().reset_index()
            
            # Dibujar el gráfico de anillo
            fig_perdidas = px.pie(df_perdidas, values='monto_pagado', names='condicion_clima', hole=0.4, 
                                  color='condicion_clima', color_discrete_map={'Lluvia/Frio': '#1f77b4', 'Despejado': '#ff7f0e'})
            st.plotly_chart(fig_perdidas, use_container_width=True)

    # PESTAÑA 2: VISTA OPERATIVA
    with tab_operativa:
        st.header("Análisis de Cancelaciones y Demanda")
        
        col_izq2, col_der2 = st.columns(2)

        with col_izq2:
            st.subheader("Volumen de Reservas por Hora (Peak)")
            df_horas = df_filtrado.groupby(['hora', 'estado_reserva']).size().reset_index(name='cantidad')
            fig_horas = px.area(df_horas, x='hora', y='cantidad', color='estado_reserva',
                                labels={'hora': 'Hora del día', 'cantidad': 'N° de Reservas'},
                                color_discrete_map={'Completada': '#2ca02c', 'Cancelada': '#d62728'})
            st.plotly_chart(fig_horas, use_container_width=True)

        with col_der2:
            st.subheader("Foco de Problemas: Cancelaciones por Comuna")
            
            # DataFrame específico para este gráfico que ignora el filtro de comuna, pero mantiene aplicados los filtros de deporte y clima si es que existen.
            df_para_comunas = df_base.copy()
            if deporte_filtro != 'Todos':
                df_para_comunas = df_para_comunas[df_para_comunas['deporte'] == deporte_filtro]
            if clima_filtro != 'Ambas':
                df_para_comunas = df_para_comunas[df_para_comunas['condicion_clima'] == clima_filtro]

            # Agrupar las cancelaciones con este nuevo DataFrame
            df_comunas_canc = df_para_comunas[df_para_comunas['estado_reserva'] == 'Cancelada'].groupby('comuna').size().reset_index(name='cancelaciones')
            
            # Ordenar normalmente (de menor a mayor para que las peores queden arriba)
            df_comunas_canc = df_comunas_canc.sort_values(by='cancelaciones', ascending=True)

            # Si hay una comuna seleccionada en el filtro, la movemos a la cima
            if comuna_filtro != 'Todas':
                # Extraemos la fila de la comuna seleccionada
                fila_comuna = df_comunas_canc[df_comunas_canc['comuna'] == comuna_filtro]
                # Dejamos el resto de las comunas en otro DataFrame
                df_resto = df_comunas_canc[df_comunas_canc['comuna'] != comuna_filtro]
                # Unimos ambos, forzando a que la seleccionada quede al final (que en Plotly 'h' es arriba)
                df_comunas_canc = pd.concat([df_resto, fila_comuna])

            # Dibujar el gráfico
            fig_comunas = px.bar(df_comunas_canc, x='cancelaciones', y='comuna', orientation='h',
                                 labels={'cancelaciones': 'N° Cancelaciones', 'comuna': 'Comuna'},
                                 color='cancelaciones', color_continuous_scale='Reds')
            
            fig_comunas.update_yaxes(dtick=1)

            st.plotly_chart(fig_comunas, use_container_width=True)

        st.divider()
        
        # Gráfico a lo ancho completo inferior
        st.subheader("Evolución Histórica de Cancelaciones (Mes a Mes)")
        df_mes = df_filtrado[df_filtrado['estado_reserva'] == 'Cancelada'].groupby(['mes_num', 'mes_nombre', 'deporte']).size().reset_index(name='cancelaciones')
        fig_meses = px.line(df_mes, x='mes_nombre', y='cancelaciones', color='deporte', markers=True,
                           labels={'mes_nombre': 'Mes', 'cancelaciones': 'N° Cancelaciones'})
        st.plotly_chart(fig_meses, use_container_width=True)