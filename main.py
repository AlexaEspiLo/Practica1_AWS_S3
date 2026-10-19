
import boto3
import pandas as pd
import json
import io
from botocore.exceptions import ClientError, BotoCoreError

# 1. Configuración del cliente AWS S3
s3_client = boto3.client("s3", region_name="us-east-1")

BUCKET_NAME = "practica1-aws-alexa-2026python"



# 2. Función para descargar y perfilar archivos de S3
def cargar_y_perfilar_s3(file_key, is_json=False):
    print(f"\n{'=' * 60}")
    print(f"Procesando archivo: {file_key}")
    print("=" * 60)

    try:
        # Descargar directamente en memoria
        response = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=file_key
        )

        contenido = response["Body"].read()
        archivo_memoria = io.BytesIO(contenido)

        # Leer según el formato
        if is_json:
            datos = json.loads(
                archivo_memoria.read().decode("utf-8")
            )
            df = pd.json_normalize(datos)
        else:
            df = pd.read_csv(archivo_memoria)

        # Convertir columnas de fechas
        for columna in ["fecha", "timestamp"]:
            if columna in df.columns:
                originales = df[columna]
                fechas = pd.to_datetime(
                    originales, errors="coerce"
                )

                invalidas = (
                    originales.notna() & fechas.isna()
                ).sum()

                df[columna] = fechas

                if invalidas:
                    print(
                        f"Fechas inválidas en {columna}: "
                        f"{invalidas}"
                    )

        # Perfilamiento de datos
        print("\n1. DIMENSIONES DEL DATASET")
        print(f"Filas: {df.shape[0]}")
        print(f"Columnas: {df.shape[1]}")

        print("\n2. TIPOS DE DATOS")
        print(df.dtypes)

        print("\n3. VALORES NULOS")
        print(df.isnull().sum())

        print("\n4. ESTADÍSTICAS DESCRIPTIVAS")
        numericas = df.select_dtypes(include="number")

        if not numericas.empty:
            print(numericas.describe().T)
        else:
            print("No hay columnas numéricas.")

        print("\n5. PRIMEROS REGISTROS")
        print(df.head())

        print("\nArchivo procesado correctamente.")
        return df

    except ClientError as error:
        codigo = error.response["Error"]["Code"]
        print(f"Error de AWS S3: {codigo}")

    except (BotoCoreError, ValueError, UnicodeError) as error:
        print(f"Error de procesamiento: {error}")

    return None


# 3. Ejecución del programa
if __name__ == "__main__":

    df_transacciones = cargar_y_perfilar_s3(
        "raw/transacciones.csv"
    )

    df_logs = cargar_y_perfilar_s3(
        "raw/logs_m2m.json",
        is_json=True
    )

    print("\n=== PROCESAMIENTO FINALIZADO ===")
