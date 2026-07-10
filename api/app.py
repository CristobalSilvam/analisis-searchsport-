from pathlib import Path
from typing import Dict, Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "modelo_cancelaciones.pkl"
METRICS_PATH = BASE_DIR / "outputs" / "metricas_modelos.csv"
CONFUSION_PATH = BASE_DIR / "outputs" / "matriz_confusion.csv"

app = FastAPI(
    title="SearchSport Analytics API",
    description="API para consultar métricas del modelo y predecir riesgo de cancelación de reservas.",
    version="1.0.0",
)

modelo = None


class ReservaInput(BaseModel):
    deporte: str = Field(..., example="Padel")
    comuna: str = Field(..., example="Maipu")
    condicion_clima: str = Field(..., example="Lluvia/Frio")
    hora: int = Field(..., ge=0, le=23, example=20)
    mes: int = Field(..., ge=1, le=12, example=7)
    dia_semana: int = Field(..., ge=0, le=6, example=4)
    fin_de_semana: int = Field(..., ge=0, le=1, example=0)
    precio_por_hora: int = Field(..., gt=0, example=32000)
    monto_pagado: int = Field(..., ge=0, example=32000)


def cargar_modelo():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "No existe el modelo entrenado. Ejecuta primero: python models/modelo_cancelaciones.py"
        )
    return joblib.load(MODEL_PATH)


@app.on_event("startup")
def startup_event():
    global modelo
    modelo = cargar_modelo()


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "servicio": "SearchSport Analytics API",
        "modelo_cargado": modelo is not None,
    }


@app.get("/metricas")
def obtener_metricas() -> Dict[str, Any]:
    if not METRICS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="No se encontraron métricas. Ejecuta primero el entrenamiento del modelo.",
        )

    metricas = pd.read_csv(METRICS_PATH)
    return {
        "total_modelos_evaluados": len(metricas),
        "mejor_modelo": metricas.iloc[0].to_dict(),
        "metricas": metricas.to_dict(orient="records"),
    }


@app.get("/matriz-confusion")
def obtener_matriz_confusion() -> Dict[str, Any]:
    if not CONFUSION_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="No se encontró matriz de confusión. Ejecuta primero el entrenamiento del modelo.",
        )

    matriz = pd.read_csv(CONFUSION_PATH, index_col=0)
    return {
        "matriz_confusion": matriz.to_dict(),
        "interpretacion": "Filas = clase real, columnas = clase predicha.",
    }


@app.post("/predict")
def predecir_cancelacion(reserva: ReservaInput) -> Dict[str, Any]:
    if modelo is None:
        raise HTTPException(status_code=500, detail="Modelo no cargado.")

    input_df = pd.DataFrame([reserva.dict()])
    prediccion = int(modelo.predict(input_df)[0])

    probabilidad_cancelacion = None
    if hasattr(modelo, "predict_proba"):
        probabilidad_cancelacion = float(modelo.predict_proba(input_df)[0][1])

    riesgo = "Alto" if probabilidad_cancelacion is not None and probabilidad_cancelacion >= 0.60 else \
             "Medio" if probabilidad_cancelacion is not None and probabilidad_cancelacion >= 0.35 else \
             "Bajo"

    return {
        "prediccion": "Cancelada" if prediccion == 1 else "Completada",
        "probabilidad_cancelacion": round(probabilidad_cancelacion, 4) if probabilidad_cancelacion is not None else None,
        "riesgo_operativo": riesgo,
        "variables_utilizadas": reserva.dict(),
    }