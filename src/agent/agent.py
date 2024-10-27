import os
import re
from datetime import datetime
import pandas as pd
from fpdf import FPDF
from langchain_ollama import ChatOllama

def extract_dates(prompt):
    """Extract start and end dates from the prompt in 'YYYY-MM-DD' format."""
    
    # Month mappings for Spanish and English
    month_mapping = {
        "primer": 1, "first": 1,
        "segundo": 2, "second": 2,
        "tercer": 3, "third": 3,
        "cuarto": 4, "fourth": 4,
        "quinto": 5, "fifth": 5,
        "sexto": 6, "sixth": 6,
        "séptimo": 7, "seventh": 7,
        "octavo": 8, "eighth": 8,
        "noveno": 9, "ninth": 9,
        "décimo": 10, "tenth": 10,
        "undécimo": 11, "eleventh": 11,
        "duodécimo": 12, "twelfth": 12,
    }

    # Check for ordinal months in the prompt
    for month_name, month_num in month_mapping.items():
        if month_name in prompt:
            year_match = re.search(r"\d{4}", prompt)
            if year_match:
                year = int(year_match.group())
                start_date = datetime(year=year, month=month_num, day=1)

                # Adjust the end date based on the month
                if month_num == 2:  # February
                    end_date = datetime(year=year, month=month_num, day=28)  # Assuming not a leap year
                elif month_num in [4, 6, 9, 11]:  # Months with 30 days
                    end_date = datetime(year=year, month=month_num, day=30)
                else:  # Months with 31 days
                    end_date = datetime(year=year, month=month_num, day=31)
                
                return start_date, end_date

    # Handle dates in YYYY-MM-DD format
    date_pattern = r"(\d{4}-\d{2}-\d{2})"
    dates = re.findall(date_pattern, prompt)
    if len(dates) == 2:
        start_date = datetime.strptime(dates[0], "%Y-%m-%d")
        end_date = datetime.strptime(dates[1], "%Y-%m-%d")
        return start_date, end_date

    return None, None

def create_pdf_report(client_id, start_date, end_date, report_content, output_folder="reports/"):
    """Crea un informe en PDF y lo guarda en la carpeta especificada."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Informe del Cliente {client_id}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Rango de fechas: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}", ln=True)
    pdf.multi_cell(0, 10, report_content)

    output_path = f"{output_folder}reporte_cliente_{client_id}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
    
    # Crear la carpeta de salida si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf.output(output_path)
    return output_path

def run_agent(df: pd.DataFrame, client_id: int, input: str) -> dict:
    """
    AI Agent que genera informes en PDF usando las funciones de Task 2 si hay datos válidos
    para el client_id y rango de fechas especificado en el prompt de entrada.

    Parámetros
    ----------
    df : pandas DataFrame
        DataFrame de los datos.
    client_id : int
        ID del cliente solicitante.
    input : str
        Input del cliente con el prompt de creación del informe.

    Returns
    -------
    variables_dict : dict
        Diccionario de variables:
            {
                "start_date": "YYYY-MM-DD",
                "end_date" : "YYYY-MM-DD",
                "client_id": int,
                "create_report" : bool
            }
    """
    # Configurar el modelo ChatOllama
    model = ChatOllama(model="llama3.2:1b", temperature=0)
    
    # Extraer fechas desde el input
    start_date, end_date = extract_dates(input)
    if not start_date or not end_date:
        raise ValueError("Fechas no válidas en el prompt.")
    
    # Filtrar datos del cliente y rango de fechas
    df_client = df[(df['client_id'] == client_id) &
                   (df['date'] >= start_date) &
                   (df['date'] <= end_date)]
    
    # Validar si existen datos para generar el informe
    create_report = not df_client.empty
    report_content = ""

    if create_report:
        # Generar contenido del informe con el modelo
        prompt = (
            f"Cliente {client_id} solicita un informe detallado sobre datos financieros y de transacciones "
            f"relevantes entre {start_date.strftime('%Y-%m-%d')} y {end_date.strftime('%Y-%m-%d')}. "
            "El informe debe incluir: \n"
            "- Resumen de ingresos y gastos.\n"
            "- Análisis de inversiones y pagos realizados.\n"
            "- Datos organizados por meses y totales anuales.\n"
            "- Visualizaciones de las tendencias en el tiempo.\n"
            "Asegúrate de usar todos los datos disponibles para proporcionar un resumen claro y relevante.")
        report_content = model.predict(prompt)

        # Crear y guardar el PDF
        pdf_path = create_pdf_report(client_id, start_date, end_date, report_content)
        print(f"Informe generado en: {pdf_path}")

    # Diccionario de salida
    variables_dict = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "client_id": client_id,
        "create_report": create_report  # Cambiar a False si no se generó el informe
    }
    
    return variables_dict


if __name__ == "__main__":
    ...
