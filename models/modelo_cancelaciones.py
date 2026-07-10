from pathlib import Path
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_CANCHAS = BASE_DIR / "canchas_searchsport.csv"
DATA_RESERVAS = BASE_DIR / "reservas_historicas_searchsport.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)


def cargar_y_preparar_datos() -> pd.DataFrame:
    """Carga reservas y canchas, las cruza y crea variables para el modelo."""
    df_canchas = pd.read_csv(DATA_CANCHAS)
    df_reservas = pd.read_csv(DATA_RESERVAS)

    df = pd.merge(df_reservas, df_canchas, on="id_cancha", how="left")

    # Validaciones básicas
    if df["deporte"].isna().any():
        raise ValueError("Existen reservas sin cancha asociada. Revisar id_cancha.")

    df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], errors="coerce")
    if df["fecha_hora"].isna().any():
        raise ValueError("Existen fechas inválidas en fecha_hora.")

    df["mes"] = df["fecha_hora"].dt.month
    df["hora"] = df["fecha_hora"].dt.hour
    df["dia_semana"] = df["fecha_hora"].dt.dayofweek
    df["fin_de_semana"] = df["dia_semana"].isin([5, 6]).astype(int)

    # Variable climática derivada para simular clima adverso de invierno
    df["condicion_clima"] = df["mes"].apply(
        lambda mes: "Lluvia/Frio" if mes in [5, 6, 7, 8] else "Despejado"
    )

    # Variable objetivo: 1 = cancelada, 0 = completada
    df["cancelada"] = (df["estado_reserva"] == "Cancelada").astype(int)

    return df


def entrenar_modelos(df: pd.DataFrame):
    features = [
        "deporte",
        "comuna",
        "condicion_clima",
        "hora",
        "mes",
        "dia_semana",
        "fin_de_semana",
        "precio_por_hora",
        "monto_pagado",
    ]
    target = "cancelada"

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=82, stratify=y
    )

    columnas_categoricas = ["deporte", "comuna", "condicion_clima"]
    columnas_numericas = ["hora", "mes", "dia_semana", "fin_de_semana", "precio_por_hora", "monto_pagado"]

    preprocesador = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), columnas_categoricas),
            ("num", StandardScaler(), columnas_numericas),
        ]
    )

    modelos = {
        "Regresion_Logistica": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Arbol_Decision": DecisionTreeClassifier(random_state=82, max_depth=8, class_weight="balanced"),
        "Random_Forest": RandomForestClassifier(n_estimators=200, random_state=82, max_depth=10, class_weight="balanced"),
        "Gradient_Boosting": GradientBoostingClassifier(random_state=82),
    }

    resultados = []
    mejores = {}

    for nombre, modelo in modelos.items():
        pipeline = Pipeline(steps=[
            ("preprocesador", preprocesador),
            ("modelo", modelo),
        ])

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        metricas = {
            "modelo": nombre,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1_score": f1_score(y_test, y_pred, zero_division=0),
        }
        resultados.append(metricas)
        mejores[nombre] = {"pipeline": pipeline, "y_pred": y_pred}

    df_metricas = pd.DataFrame(resultados).sort_values(by="f1_score", ascending=False)
    mejor_nombre = df_metricas.iloc[0]["modelo"]
    mejor_pipeline = mejores[mejor_nombre]["pipeline"]
    mejor_pred = mejores[mejor_nombre]["y_pred"]

    return df_metricas, mejor_nombre, mejor_pipeline, y_test, mejor_pred


def main():
    df = cargar_y_preparar_datos()
    df_metricas, mejor_nombre, mejor_pipeline, y_test, mejor_pred = entrenar_modelos(df)

    metricas_path = OUTPUT_DIR / "metricas_modelos.csv"
    reporte_path = OUTPUT_DIR / "reporte_mejor_modelo.txt"
    matriz_path = OUTPUT_DIR / "matriz_confusion.csv"
    modelo_path = MODEL_DIR / "modelo_cancelaciones.pkl"

    df_metricas.to_csv(metricas_path, index=False)
    joblib.dump(mejor_pipeline, modelo_path)

    matriz = confusion_matrix(y_test, mejor_pred)
    pd.DataFrame(
        matriz,
        index=["Real_Completada", "Real_Cancelada"],
        columns=["Pred_Completada", "Pred_Cancelada"],
    ).to_csv(matriz_path)

    with open(reporte_path, "w", encoding="utf-8") as f:
        f.write(f"Mejor modelo: {mejor_nombre}\n\n")
        f.write("Métricas comparativas:\n")
        f.write(df_metricas.to_string(index=False))
        f.write("\n\nReporte de clasificación del mejor modelo:\n")
        f.write(classification_report(y_test, mejor_pred, target_names=["Completada", "Cancelada"]))

    print("Modelo entrenado correctamente.")
    print(f"Mejor modelo: {mejor_nombre}")
    print("\nMétricas:")
    print(df_metricas)
    print(f"\nArchivos generados:")
    print(f"- {metricas_path}")
    print(f"- {reporte_path}")
    print(f"- {matriz_path}")
    print(f"- {modelo_path}")


if __name__ == "__main__":
    main()