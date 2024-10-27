import pandas as pd
import os
import matplotlib.pyplot as plt
import json


def earnings_and_expenses(
    df: pd.DataFrame, client_id: int, start_date: str, end_date: str
) -> pd.DataFrame:
    """
    For the period defined in between start_date and end_date (both included), get the client data available and return
    a pandas DataFrame with the Earnings and Expenses total amount for the period range and user given. The expected columns are:
        - Earnings
        - Expenses
    The DataFrame should have the columns in this order ['Earnings', 'Expenses']. Round the amounts to 2 decimals.

    Create a Bar Plot with the Earnings and Expenses absolute values and save it as "reports/figures/earnings_and_expenses.png".

    Parameters
    ----------
    df : pandas DataFrame
       DataFrame of the data to be used for the agent.
    client_id : int
        Id of the client.
    start_date : str
        Start date for the date period. In the format "YYYY-MM-DD".
    end_date : str
        End date for the date period. In the format "YYYY-MM-DD".

    Returns
    -------
    Pandas Dataframe with the earnings and expenses rounded to 2 decimals.
    """
    df= df.copy()

    # Filter df by client_id and date period.
    df = df[(df["client_id"] == client_id) & (df["date"] >= start_date) & (df["date"] <= end_date)]

    # Convert amount to numeric.
    df['amount'] = df['amount'].str.replace('$', '', regex=False)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    # Create a column earnings if the amount is positive, otherwise expenses.
    df["Earnings"] = df["amount"].apply(lambda x: x if x > 0 else 0)
    df["Expenses"] = df["amount"].apply(lambda x: x if x < 0 else 0)

    # Round values to 2 decimals.
    df = df[["Earnings", "Expenses"]].round(2)

    # Calcula la suma de cada columna
    sums = df.sum()

    # Crear un DataFrame con los totales de ingresos y gastos.
    df = pd.DataFrame({
        "Earnings": sums["Earnings"],
        "Expenses": sums["Expenses"]
    }, index=[0])

    # Round values to 2 decimals.
    df = df[["Earnings", "Expenses"]].round(2)

    # Select Only Earnings and Expenses columns.
    df = df[["Earnings", "Expenses"]]

    # Create a bar plot with expenses absolute values for Expenses.
    plt.figure(figsize=(10, 6))
    plt.bar(df.columns, df.iloc[0].abs(), color=["green", "red"])
    plt.title("Earnings and Expenses")
    plt.ylabel("Amount")
    plt.xticks(rotation=0)
    plt.tight_layout()

    # Save the plot
    plt.savefig("reports/figures/earnings_and_expenses.png")

    return df


def expenses_summary(
    df: pd.DataFrame, client_id: int, start_date: str, end_date: str
) -> pd.DataFrame:
    """
    For the period defined in between start_date and end_date (both included), get the client data available and return
    a Pandas Data Frame with the Expenses by merchant category. The expected columns are:
        - Expenses Type --> (merchant category names)
        - Total Amount
        - Average
        - Max
        - Min
        - Num. Transactions
    The DataFrame should be sorted alphabetically by Expenses Type and values have to be rounded to 2 decimals. 
    Return the dataframe with the columns in the given order.
    The merchant category names can be found in data/raw/mcc_codes.json.

    Create a Bar Plot with the data in absolute values and save it as "reports/figures/expenses_summary.png".

    Parameters
    ----------
    df : pandas DataFrame
       DataFrame of the data to be used for the agent.
    client_id : int
        Id of the client.
    start_date : str
        Start date for the date period. In the format "YYYY-MM-DD".
    end_date : str
        End date for the date period. In the format "YYYY-MM-DD".

    Returns
    -------
    Pandas DataFrame with the Expenses by merchant category.
    """
    
    # Crear una copia del DataFrame para no modificar el original
    df = df.copy()

    # Cargar el mapping de códigos MCC
    with open('data/raw/mcc_codes.json', 'r') as f:
        mcc_codes = json.load(f)

    # Limpiar y convertir la columna amount
    df['amount'] = df['amount'].str.replace('$', '', regex=False)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    # Convertir las fechas a datetime
    df['date'] = pd.to_datetime(df['date'])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filtrar por cliente, rango de fechas y solo gastos (valores negativos)
    mask = (
        (df['client_id'] == client_id) & 
        (df['date'] >= start_date) & 
        (df['date'] <= end_date) &
        (df['amount'] < 0)
    )
    filtered_df = df[mask].copy()

    # Convertir los montos a valores absolutos para los cálculos
    # filtered_df['amount'] = filtered_df['amount'].abs()

   # Convert mcc codes to string.
    filtered_df['mcc'] = filtered_df['mcc'].astype(str)
    # Mapear los códigos MCC a nombres de categoría
    filtered_df['Expenses Type'] = filtered_df['mcc'].map(mcc_codes)

    # Aplicar agregaciones separadas para cada estadística
    sum_df = filtered_df.groupby('Expenses Type')['amount'].sum().round(2).rename("Total Amount")
    mean_df = filtered_df.groupby('Expenses Type')['amount'].mean().round(2).rename("Average")
    max_df = filtered_df.groupby('Expenses Type')['amount'].max().round(2).rename("Max")
    min_df = filtered_df.groupby('Expenses Type')['amount'].min().round(2).rename("Min")  

    # Convertir en absoluto sum_df, mean_df, max_df, min_df
    sum_df = sum_df.abs()
    mean_df = mean_df.abs()
    max_df = max_df.abs()
    min_df = min_df.abs()

    # Calcular el máximo y el mínimo utilizando el valor absoluto de 'amount'
    count_df = filtered_df.groupby('Expenses Type')['amount'].count().rename("Num. Transactions")

    # Unir todas las estadísticas en un solo DataFrame
    summary = pd.concat([sum_df, mean_df, max_df, min_df, count_df], axis=1).reset_index()

    # Ordenar alfabéticamente por Expenses Type
    summary = summary.sort_values('Expenses Type')
    
    # Crear el directorio si no existe
    os.makedirs('reports/figures', exist_ok=True)
    
    # Crear gráfico de barras
    plt.figure(figsize=(12, 6))
    plt.bar(summary['Expenses Type'], summary['Total Amount'])
    plt.xticks(rotation=45, ha='right')
    plt.title(f'Expenses Summary by Category for Client {client_id}\n{start_date.date()} to {end_date.date()}')
    plt.ylabel('Total Amount')
    plt.xlabel('Expenses Type')
    plt.tight_layout()
    
    # Guardar el gráfico
    plt.savefig('reports/figures/expenses_summary.png')
    
    return summary[['Expenses Type', 'Total Amount', 'Average', 'Max', 'Min', 'Num. Transactions']]


def cash_flow_summary(
    df: pd.DataFrame, client_id: int, start_date: str, end_date: str
) -> pd.DataFrame:
    """
    For the period defined by start_date and end_date (both inclusive), retrieve the available client data and return a Pandas DataFrame containing cash flow information.

    If the period exceeds 60 days, group the data by month, using the end of each month for the date. If the period is 60 days or shorter, group the data by week.

        The expected columns are:
            - Date --> the date for the period. YYYY-MM if period larger than 60 days, YYYY-MM-DD otherwise.
            - Inflows --> the sum of the earnings (positive amounts)
            - Outflows --> the sum of the expenses (absolute values of the negative amounts)
            - Net Cash Flow --> Inflows - Outflows
            - % Savings --> Percentage of Net Cash Flow / Inflows

        The DataFrame should be sorted by ascending date and values rounded to 2 decimals. The columns should be in the given order.

        Parameters
        ----------
        df : pandas DataFrame
           DataFrame  of the data to be used for the agent.
        client_id : int
            Id of the client.
        start_date : str
            Start date for the date period. In the format "YYYY-MM-DD".
        end_date : str
            End date for the date period. In the format "YYYY-MM-DD".


        Returns
        -------
        Pandas Dataframe with the cash flow summary.

    """

    # Copiar DataFrame para evitar modificar el original
    df = df.copy()
    
    # Convertir la columna de fecha a datetime, forzando errores a NaT (valores no convertibles)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    # Convertir los argumentos de fecha a datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df['amount'] = df['amount'].str.replace('$', '', regex=False)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # Filtrar datos por cliente, rango de fechas, y eliminar filas con NaT en 'date'
    mask = (
        (df['client_id'] == client_id) & 
        (df['date'] >= start_date) & 
        (df['date'] <= end_date)
    )
    filtered_df = df[mask].dropna(subset=['date']).copy()
    
    # Determinar si el periodo es mayor a 60 días
    period_days = (end_date - start_date).days
    if period_days > 60:
            # Group by month
            filtered_df['date'] = filtered_df['date'].dt.strftime('%Y-%m')
    else:
            # Group by week (end of week)
            filtered_df['date'] = filtered_df['date'].dt.strftime('%Y-%m-%d')
            filtered_df['date'] = pd.to_datetime(filtered_df['date']).dt.to_period('W').dt.end_time.dt.strftime('%Y-%m-%d')
    
    
    # Calcular inflows, outflows y net cash flow
    summary = filtered_df.groupby('date').apply(lambda x: pd.Series({
        'Inflows': x.loc[x['amount'] >= 0, 'amount'].sum(),
        'Outflows': x.loc[x['amount'] < 0, 'amount'].abs().sum()
    })).fillna(0)
    
    # Calcular Net Cash Flow y % Savings
    summary['Net Cash Flow'] = summary['Inflows'] - summary['Outflows']
    summary['% Savings'] = (summary['Net Cash Flow'] / summary['Inflows']).fillna(0) * 100
    
    # Redondear los valores a 2 decimales
    summary = summary.round(2)
    
    # Asegurarse de que las columnas están en el orden especificado
    summary = summary.reset_index()[['date', 'Inflows', 'Outflows', 'Net Cash Flow', '% Savings']]

    # Rename date column to Date.
    summary = summary.rename(columns={'date': 'Date'})
    
    # Ordenar por fecha ascendente
    summary = summary.sort_values(by='Date')
    
    return summary


if __name__ == "__main__":
    ...
