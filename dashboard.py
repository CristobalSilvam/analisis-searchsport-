import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from pathlib import Path

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Analisis SearchSport",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CARGA Y TRANSFORMACIÓN DE DATOS
# ============================================================

@st.cache_data
def load_data():
    canchas_path = BASE_DIR / "canchas_searchsport.csv"
    reservas_path = BASE_DIR / "reservas_historicas_searchsport.csv"

    df_canchas = pd.read_csv(canchas_path)
    df_reservas = pd.read_csv(reservas_path)

    # Merge de ambas fuentes
    df = pd.merge(df_reservas, df_canchas, on="id_cancha", how="left")

    # Transformaciones de fecha
    df["fecha_hora"] = pd.to_datetime(df["fecha_hora"])
    df["mes_num"] = df["fecha_hora"].dt.month
    df["hora"] = df["fecha_hora"].dt.hour
    df["dia_semana"] = df["fecha_hora"].dt.weekday
    df["fin_de_semana"] = df["dia_semana"].apply(lambda x: 1 if x in [5, 6] else 0)

    nombres_meses = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }

    df["mes_nombre"] = df["mes_num"].map(nombres_meses)

    # Simulación de variable climática estacional
    df["condicion_clima"] = df["mes_num"].apply(
        lambda x: "Lluvia/Frio" if x in [5, 6, 7, 8] else "Despejado"
    )

    return df


df_base = load_data()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Filtros Globales")
st.sidebar.markdown("Usa estos filtros para segmentar todo el dashboard.")

comuna_filtro = st.sidebar.selectbox(
    "Filtrar por Comuna:",
    options=["Todas"] + sorted(list(df_base["comuna"].unique()))
)

deporte_filtro = st.sidebar.selectbox(
    "Filtrar por Deporte:",
    options=["Todos"] + sorted(list(df_base["deporte"].unique()))
)

clima_filtro = st.sidebar.radio(
    "Condición Climática:",
    options=["Ambas", "Despejado", "Lluvia/Frio"]
)

# Aplicar filtros al DataFrame
df_filtrado = df_base.copy()

if comuna_filtro != "Todas":
    df_filtrado = df_filtrado[df_filtrado["comuna"] == comuna_filtro]

if deporte_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["deporte"] == deporte_filtro]

if clima_filtro != "Ambas":
    df_filtrado = df_filtrado[df_filtrado["condicion_clima"] == clima_filtro]

# ============================================================
# INTERFAZ PRINCIPAL
# ============================================================

st.title("SearchSport - Analisis")

tab_ejecutiva, tab_operativa, tab_predictiva = st.tabs([
    "Vista Ejecutiva (Negocio)",
    "Vista Operativa (Canchas y Comunas)",
    "Predicción de Cancelación"
])

# ============================================================
# PESTAÑA 1: VISTA EJECUTIVA
# ============================================================

with tab_ejecutiva:
    if df_filtrado.empty:
        st.warning("No hay datos para la combinación de filtros seleccionada. Intenta con otros parámetros.")
    else:
        st.header("Resumen de Rentabilidad")

        ingresos_totales = df_filtrado[
            df_filtrado["estado_reserva"] == "Completada"
        ]["monto_pagado"].sum()

        ingresos_perdidos = df_filtrado[
            df_filtrado["estado_reserva"] == "Cancelada"
        ]["monto_pagado"].sum()

        tasa_cancelacion = (
            len(df_filtrado[df_filtrado["estado_reserva"] == "Cancelada"]) / len(df_filtrado)
        ) * 100 if len(df_filtrado) > 0 else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("Ingresos Generados (CLP)", f"${ingresos_totales:,.0f}")
        col2.metric(
            "Pérdidas por Cancelación",
            f"${ingresos_perdidos:,.0f}",
            delta="- Fuga de capital",
            delta_color="inverse"
        )
        col3.metric("Tasa de Cancelación Global", f"{tasa_cancelacion:.1f}%")

        st.divider()

        col_izq, col_der = st.columns(2)

        with col_izq:
            st.subheader("Ingresos vs Pérdidas por Deporte")

            df_agrupado = (
                df_filtrado
                .groupby(["deporte", "estado_reserva"])["monto_pagado"]
                .sum()
                .reset_index()
            )

            fig_ingresos = px.bar(
                df_agrupado,
                x="deporte",
                y="monto_pagado",
                color="estado_reserva",
                color_discrete_map={
                    "Completada": "#2ca02c",
                    "Cancelada": "#d62728"
                },
                barmode="group",
                labels={
                    "monto_pagado": "Monto (CLP)",
                    "deporte": "Deporte",
                    "estado_reserva": "Estado"
                }
            )

            st.plotly_chart(fig_ingresos, width="stretch")

        with col_der:
            st.subheader("Impacto del Clima en Pérdidas Monetarias")

            df_para_clima = df_base.copy()

            if comuna_filtro != "Todas":
                df_para_clima = df_para_clima[df_para_clima["comuna"] == comuna_filtro]

            if deporte_filtro != "Todos":
                df_para_clima = df_para_clima[df_para_clima["deporte"] == deporte_filtro]

            df_perdidas = (
                df_para_clima[df_para_clima["estado_reserva"] == "Cancelada"]
                .groupby("condicion_clima")["monto_pagado"]
                .sum()
                .reset_index()
            )

            fig_perdidas = px.pie(
                df_perdidas,
                values="monto_pagado",
                names="condicion_clima",
                hole=0.4,
                color="condicion_clima",
                color_discrete_map={
                    "Lluvia/Frio": "#1f77b4",
                    "Despejado": "#ff7f0e"
                }
            )

            st.plotly_chart(fig_perdidas, width="stretch")

# ============================================================
# PESTAÑA 2: VISTA OPERATIVA
# ============================================================

with tab_operativa:
    if df_filtrado.empty:
        st.warning("No hay datos para la combinación de filtros seleccionada. Intenta con otros parámetros.")
    else:
        st.header("Análisis de Cancelaciones y Demanda")

        col_izq2, col_der2 = st.columns(2)

        with col_izq2:
            st.subheader("Volumen de Reservas por Hora (Peak)")

            df_horas = (
                df_filtrado
                .groupby(["hora", "estado_reserva"])
                .size()
                .reset_index(name="cantidad")
            )

            fig_horas = px.area(
                df_horas,
                x="hora",
                y="cantidad",
                color="estado_reserva",
                labels={
                    "hora": "Hora del día",
                    "cantidad": "N° de Reservas",
                    "estado_reserva": "Estado"
                },
                color_discrete_map={
                    "Completada": "#2ca02c",
                    "Cancelada": "#d62728"
                }
            )

            st.plotly_chart(fig_horas, width="stretch")

        with col_der2:
            st.subheader("Foco de Problemas: Cancelaciones por Comuna")

            df_para_comunas = df_base.copy()

            if deporte_filtro != "Todos":
                df_para_comunas = df_para_comunas[df_para_comunas["deporte"] == deporte_filtro]

            if clima_filtro != "Ambas":
                df_para_comunas = df_para_comunas[
                    df_para_comunas["condicion_clima"] == clima_filtro
                ]

            df_comunas_canc = (
                df_para_comunas[df_para_comunas["estado_reserva"] == "Cancelada"]
                .groupby("comuna")
                .size()
                .reset_index(name="cancelaciones")
            )

            df_comunas_canc = df_comunas_canc.sort_values(
                by="cancelaciones",
                ascending=True
            )

            if comuna_filtro != "Todas":
                fila_comuna = df_comunas_canc[df_comunas_canc["comuna"] == comuna_filtro]
                df_resto = df_comunas_canc[df_comunas_canc["comuna"] != comuna_filtro]
                df_comunas_canc = pd.concat([df_resto, fila_comuna])

            fig_comunas = px.bar(
                df_comunas_canc,
                x="cancelaciones",
                y="comuna",
                orientation="h",
                labels={
                    "cancelaciones": "N° Cancelaciones",
                    "comuna": "Comuna"
                },
                color="cancelaciones",
                color_continuous_scale="Reds"
            )

            fig_comunas.update_yaxes(dtick=1)

            st.plotly_chart(fig_comunas, width="stretch")

        st.divider()

        st.subheader("Evolución Histórica de Cancelaciones (Mes a Mes)")

        df_mes = (
            df_filtrado[df_filtrado["estado_reserva"] == "Cancelada"]
            .groupby(["mes_num", "mes_nombre", "deporte"])
            .size()
            .reset_index(name="cancelaciones")
        )

        orden_meses = [
            "Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
        ]

        df_mes["mes_nombre"] = pd.Categorical(
            df_mes["mes_nombre"],
            categories=orden_meses,
            ordered=True
        )

        df_mes = df_mes.sort_values(["mes_nombre", "deporte"])

        fig_meses = px.line(
            df_mes,
            x="mes_nombre",
            y="cancelaciones",
            color="deporte",
            markers=True,
            labels={
                "mes_nombre": "Mes",
                "cancelaciones": "N° Cancelaciones",
                "deporte": "Deporte"
            },
            category_orders={"mes_nombre": orden_meses}
        )

        st.plotly_chart(fig_meses, width="stretch")

# ============================================================
# PESTAÑA 3: MODELO PREDICTIVO
# ============================================================

with tab_predictiva:
    st.header("Predicción de Riesgo de Cancelación")

    st.markdown(
        """
        Esta vista permite simular una reserva y estimar su probabilidad de cancelación.
        La predicción se obtiene consultando la API REST del modelo predictivo.
        """
    )

    st.divider()

    st.subheader("Simulación de reserva")

    meses = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
    ]

    dias_semana = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo")
    ]

    horas_disponibles = list(range(9, 23))

    with st.form("form_prediccion_cancelacion"):
        col1_pred, col2_pred, col3_pred = st.columns(3)

        with col1_pred:
            st.markdown("**Datos deportivos**")

            deporte_pred = st.selectbox(
                "Deporte",
                options=sorted(df_base["deporte"].unique()),
                key="pred_deporte"
            )

            comuna_pred = st.selectbox(
                "Comuna",
                options=sorted(df_base["comuna"].unique()),
                key="pred_comuna"
            )

            clima_pred = st.selectbox(
                "Condición climática",
                options=["Despejado", "Lluvia/Frio"],
                key="pred_clima"
            )

        with col2_pred:
            st.markdown("**Datos temporales**")

            hora_pred = st.selectbox(
                "Hora de la reserva",
                options=horas_disponibles,
                format_func=lambda h: f"{h:02d}:00 hrs",
                index=11,
                key="pred_hora"
            )

            mes_pred = st.selectbox(
                "Mes",
                options=meses,
                format_func=lambda x: x[1],
                index=6,
                key="pred_mes"
            )[0]

            dia_semana_pred = st.selectbox(
                "Día de la semana",
                options=dias_semana,
                format_func=lambda x: x[1],
                index=4,
                key="pred_dia"
            )[0]

        with col3_pred:
            st.markdown("**Datos económicos**")

            fin_de_semana_pred = 1 if dia_semana_pred in [5, 6] else 0

            precio_sugerido_raw = df_base[
                df_base["deporte"] == deporte_pred
            ]["precio_por_hora"].median()

            precio_sugerido = int(round(precio_sugerido_raw / 1000) * 1000)

            valor_reserva = st.number_input(
                "Valor de la reserva (CLP)",
                min_value=1000,
                value=precio_sugerido,
                step=1000,
                key="pred_valor_reserva"
            )

            st.caption(
                "Este valor representa el monto económico asociado a la reserva. "
                "Internamente se utiliza como precio base y valor transaccional para el modelo."
            )

            st.metric(
                "Tipo de día",
                "Fin de semana" if fin_de_semana_pred == 1 else "Día hábil"
            )

        calcular = st.form_submit_button("Calcular riesgo de cancelación")

    if calcular:
        payload = {
            "deporte": deporte_pred,
            "comuna": comuna_pred,
            "condicion_clima": clima_pred,
            "hora": hora_pred,
            "mes": mes_pred,
            "dia_semana": dia_semana_pred,
            "fin_de_semana": fin_de_semana_pred,
            "precio_por_hora": valor_reserva,
            "monto_pagado": valor_reserva
        }

        try:
            api_url = "http://api-searchsport:8000/predict"

            try:
                response = requests.post(api_url, json=payload, timeout=10)
            except requests.exceptions.RequestException:
                api_url = "http://localhost:8000/predict"
                response = requests.post(api_url, json=payload, timeout=10)

            response.raise_for_status()
            resultado_api = response.json()

            prediccion = resultado_api.get("prediccion", "No disponible")
            probabilidad = resultado_api.get("probabilidad_cancelacion", None)
            riesgo = resultado_api.get("riesgo_operativo", "No disponible")

            if riesgo == "Alto":
                color_riesgo = "#d62728"
                recomendacion = (
                    "Aplicar gestión preventiva: confirmar la reserva con anticipación, "
                    "ofrecer alternativa indoor, cambio de horario o reforzar política de abono."
                )
            elif riesgo == "Medio":
                color_riesgo = "#ff9800"
                recomendacion = (
                    "Enviar recordatorio preventivo y monitorear la reserva antes del horario peak."
                )
            else:
                color_riesgo = "#2ca02c"
                recomendacion = (
                    "Mantener flujo normal. La reserva presenta bajo riesgo operativo."
                )

            st.divider()
            st.subheader("Resultado de la predicción")

            col_res1, col_res2, col_res3 = st.columns(3)

            col_res1.metric("Predicción", prediccion)

            col_res2.metric(
                "Probabilidad de cancelación",
                f"{probabilidad * 100:.1f}%" if probabilidad is not None else "No disponible"
            )

            col_res3.metric("Riesgo operativo", riesgo)

            if probabilidad is not None:
                st.progress(int(probabilidad * 100))

            st.markdown(
                f"""
                <div style="
                    padding: 20px;
                    border-radius: 12px;
                    background-color: rgba(255,255,255,0.05);
                    border-left: 7px solid {color_riesgo};
                    margin-top: 16px;
                    margin-bottom: 22px;
                ">
                    <h4 style="margin-bottom: 8px;">Lectura operativa</h4>
                    <p style="font-size: 16px;">
                        La reserva evaluada presenta un riesgo
                        <b style="color:{color_riesgo};">{riesgo}</b>
                        de cancelación.
                    </p>
                    <p style="font-size: 15px;">
                        <b>Recomendación:</b> {recomendacion}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_info1, col_info2, col_info3, col_info4 = st.columns(4)

            nombre_mes = dict(meses).get(mes_pred, str(mes_pred))

            col_info1.metric("Clima", clima_pred)
            col_info2.metric("Horario", f"{hora_pred:02d}:00 hrs")
            col_info3.metric("Mes", nombre_mes)
            col_info4.metric(
                "Horario peak",
                "Sí" if hora_pred in [18, 19, 20, 21] else "No"
            )

            with st.expander("Ver variables enviadas al modelo"):
                st.json(payload)

            with st.expander("Ver respuesta completa de la API"):
                st.json(resultado_api)

        except Exception as e:
            st.error("No se pudo consultar la API predictiva.")
            st.info(
                "Verifica que el servicio de API esté corriendo y que Swagger funcione en http://localhost:8000/docs"
            )
            st.exception(e)