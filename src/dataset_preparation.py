import pandas as pd
import numpy as np
import os

def clean_text(text):
    """
    Limpia y normaliza texto para consistencia
    """
    if pd.isna(text) or text == "":
        return ""
    
    text = str(text).lower().strip()
    
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Estandarizar términos similares
    standardizations = {
        'desinteres': 'desinteres',
        'desinterés': 'desinteres',
        'interes': 'interes',
        'interés': 'interes',
        'indecision': 'indecision',
        'indecisión': 'indecision',
        'profesionalismo empatico': 'profesionalismo',
        'empatia': 'empatia',
        'empata': 'empatia'
    }
    
    return standardizations.get(text, text)

def transform_excel_to_dataset(excel_file):
    """
    Transforma el archivo Excel en un dataset estructurado para análisis
    """
    print(f"Leyendo archivo: {excel_file}")
    
    df = pd.read_excel(excel_file, header=1)
    
    # Renombrar columnas para claridad
    df.columns = [
        'Sentimiento_Humano', 'Emocion_Candidato_Humano', 
        'Emocion_Agente_Humano', 'Interes_Candidato_Humano',
        'Sentimiento_IA', 'Emocion_Candidato_IA', 
        'Emocion_Agente_IA', 'Interes_Candidato_IA'
    ]
    
    df['ID_Llamada'] = range(1, len(df) + 1)
    
    text_columns = [col for col in df.columns if col != 'ID_Llamada']
    for col in text_columns:
        df[col] = df[col].apply(clean_text)
    
    print(f"Datos procesados: {len(df)} llamadas")
    
    metrics = ['Sentimiento', 'Emocion_Candidato', 'Emocion_Agente', 'Interes_Candidato']
    
    long_data = []
    
    for _, row in df.iterrows():
        call_id = row['ID_Llamada']
        
        for metric in metrics:
            human_col = f'{metric}_Humano'
            ia_col = f'{metric}_IA'
            
            long_data.append({
                'ID_Llamada': call_id,
                'Metrica': metric,
                'Evaluador': 'Humano',
                'Valor': row[human_col]
            })
            
            long_data.append({
                'ID_Llamada': call_id,
                'Metrica': metric,
                'Evaluador': 'IA',
                'Valor': row[ia_col]
            })
    
    df_long = pd.DataFrame(long_data)
    df_wide = df.copy()
    
    for metric in metrics:
        human_col = f'{metric}_Humano'
        ia_col = f'{metric}_IA'
        match_col = f'{metric}_Match'
        df_wide[match_col] = (df_wide[human_col] == df_wide[ia_col]).astype(int)
    
    return df_wide, df_long

def generate_summary_stats(df_wide, df_long):
    """
    Genera estadísticas resumen del dataset
    """
    print("\n == RESUMEN DEL DATASET == ")
    print(f"Total de llamadas: {df_wide['ID_Llamada'].nunique()}")
    print(f"Total de evaluaciones: {len(df_long)}")
    
    metrics = ['Sentimiento', 'Emocion_Candidato', 'Emocion_Agente', 'Interes_Candidato']
    
    print("\n=== VALORES ÚNICOS POR MÉTRICA === ")
    for metric in metrics:
        metric_data = df_long[df_long['Metrica'] == metric]
        unique_values = sorted(metric_data['Valor'].unique())
        unique_values = [v for v in unique_values if v != ""]
        print(f"{metric}: {unique_values}")
    
    print("\n=== COINCIDENCIAS POR MÉTRICA === ")
    for metric in metrics:
        match_col = f'{metric}_Match'
        if match_col in df_wide.columns:
            matches = df_wide[match_col].sum()
            total = len(df_wide)
            percentage = (matches / total) * 100
            print(f"{metric}: {matches}/{total} ({percentage:.1f}%)")
    
    match_columns = [f'{metric}_Match' for metric in metrics]
    if all(col in df_wide.columns for col in match_columns):
        total_matches = df_wide[match_columns].sum().sum()
        total_evaluations = len(df_wide) * len(metrics)
        global_accuracy = (total_matches / total_evaluations) * 100
        print(f"\nPrecisión global: {total_matches}/{total_evaluations} ({global_accuracy:.1f}%)")

def save_datasets(df_wide, df_long, base_name="dataset_evaluacion_ia"):
    """
    Guarda los datasets en diferentes formatos
    """
    # Crear directorio si no existe
    output_dir = "datasets_procesados"
    os.makedirs(output_dir, exist_ok=True)
    
    wide_csv = os.path.join(output_dir, f"{base_name}_wide.csv")
    long_csv = os.path.join(output_dir, f"{base_name}_long.csv")
    wide_excel = os.path.join(output_dir, f"{base_name}_wide.xlsx")
    long_excel = os.path.join(output_dir, f"{base_name}_long.xlsx")
    
    df_wide.to_csv(wide_csv, index=False, encoding='utf-8')
    df_long.to_csv(long_csv, index=False, encoding='utf-8')
    df_wide.to_excel(wide_excel, index=False)
    df_long.to_excel(long_excel, index=False)
    
    print(f"\n=== ARCHIVOS GENERADOS === ")
    print(f"1. {wide_csv} - Formato ancho (original mejorado)")
    print(f"2. {long_csv} - Formato largo (para análisis estadístico)")
    print(f"3. {wide_excel} - Formato ancho en Excel")
    print(f"4. {long_excel} - Formato largo en Excel")
    
    return wide_csv, long_csv, wide_excel, long_excel

def main():
    """
    Función principal
    """
    excel_file = "ResultadosHumanosIA.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"Error: No se encontró el archivo {excel_file}")
        print("Asegúrate de que el archivo esté en el mismo directorio que este script.")
        return
    
    try:

        df_wide, df_long = transform_excel_to_dataset(excel_file)
        
        generate_summary_stats(df_wide, df_long)
        
        files = save_datasets(df_wide, df_long)
        
        print("\n=== DESCRIPCIÓN DE LOS FORMATOS === ")
        print("\nFormato ANCHO (wide):")
        print("- Una fila por llamada")
        print("- Columnas separadas para Humano e IA")
        print("- Incluye columnas de coincidencia (*_Match)")
        print("- Ideal para comparaciones directas")
        
        print("\nFormato LARGO (long):")
        print("- Una fila por evaluación (Humano/IA)")
        print("- Columna 'Evaluador' indica si es Humano o IA")
        print("- Ideal para análisis estadísticos y visualizaciones")
        print("- Compatible con bibliotecas como scikit-learn, seaborn")
        
        print("\nTransformación completada exitosamente!")
        
    except Exception as e:
        print(f"Error durante la transformación: {str(e)}")
        print("Verifica que el archivo Excel tenga el formato correcto.")

if __name__ == "__main__":
    main()