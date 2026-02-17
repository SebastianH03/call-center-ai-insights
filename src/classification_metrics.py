#!/usr/bin/env python3
"""
Evaluador Simple de Precisión para Modelo GPT-4o en Clasificación de Sentimientos

Este script evalúa la precisión del modelo GPT-4o usando métricas estándar de clasificación.
Utiliza el dataset que ya tiene las comparaciones humano vs IA calculadas.

Métricas principales:
- Accuracy (Precisión Global)
- Precision, Recall, F1-Score
- Support (número de muestras por clase)

Referencias:
- Sokolova, M., & Lapalme, G. (2009). A systematic analysis of performance measures for classification tasks.
- Powers, D. M. (2011). Evaluation: from precision, recall and F-measure to ROC, informedness, markedness and correlation.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from typing import Dict, List, Tuple

class SimpleClassificationEvaluator:
    """
    Evaluador simple y directo para clasificación multiclase.
    """
    
    def __init__(self):
        self.results = {}
        self.data = None
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Carga los datos desde CSV."""
        try:
            self.data = pd.read_csv(file_path)
            print(f"Datos cargados: {len(self.data)} llamadas")
            return self.data
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def calculate_metrics(self, y_true: List[str], y_pred: List[str]) -> Dict:
        """
        Calcula métricas de clasificación estándar.
        
        Args:
            y_true: Etiquetas verdaderas (humano)
            y_pred: Predicciones (IA)
            
        Returns:
            Dict con métricas calculadas
        """

        y_true_clean = [str(val).lower().strip() for val in y_true if pd.notna(val)]
        y_pred_clean = [str(val).lower().strip() for val in y_pred if pd.notna(val)]
        

        accuracy = accuracy_score(y_true_clean, y_pred_clean)
        
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true_clean, y_pred_clean, average='macro', zero_division=0
        )
        
        unique_classes = sorted(list(set(y_true_clean + y_pred_clean)))
        precision_per_class, recall_per_class, f1_per_class, support_per_class = precision_recall_fscore_support(
            y_true_clean, y_pred_clean, labels=unique_classes, zero_division=0
        )
        
        exact_matches = sum(1 for i in range(len(y_true_clean)) if y_true_clean[i] == y_pred_clean[i])
        
        return {
            'accuracy': accuracy,
            'precision_macro': precision,
            'recall_macro': recall,
            'f1_macro': f1,
            'exact_matches': exact_matches,
            'total_samples': len(y_true_clean),
            'unique_classes': unique_classes,
            'precision_per_class': precision_per_class,
            'recall_per_class': recall_per_class,
            'f1_per_class': f1_per_class,
            'support_per_class': support_per_class
        }
    
    def evaluate_dimensions(self) -> Dict:
        """
        Evalúa las 4 dimensiones de clasificación.
        
        Returns:
            Dict con resultados por dimensión
        """
        if self.data is None:
            print("No hay datos. Use load_data() primero.")
            return {}
        
        # Definir las columnas para cada dimensión
        dimensions = {
            'Sentimiento General': ('Sentimiento_Humano', 'Sentimiento_IA'),
            'Emoción Candidato': ('Emocion_Candidato_Humano', 'Emocion_Candidato_IA'),
            'Emoción Agente': ('Emocion_Agente_Humano', 'Emocion_Agente_IA'),
            'Interés Candidato': ('Interes_Candidato_Humano', 'Interes_Candidato_IA')
        }
        
        results = {}
        
        print("\nEVALUACIÓN DE PRECISIÓN GPT-4o")
    
        for dim_name, (human_col, ai_col) in dimensions.items():
            print(f"\n{dim_name}")
            
            y_true = self.data[human_col].tolist()
            y_pred = self.data[ai_col].tolist()
            
            metrics = self.calculate_metrics(y_true, y_pred)
            results[dim_name] = metrics
            
            print(f"   Accuracy:    {metrics['accuracy']:.3f} ({metrics['accuracy']*100:.1f}%)")
            print(f"   Precision:   {metrics['precision_macro']:.3f}")
            print(f"   Recall:      {metrics['recall_macro']:.3f}")
            print(f"   F1-Score:    {metrics['f1_macro']:.3f}")
            print(f"   Coincidencias: {metrics['exact_matches']}/{metrics['total_samples']}")
            print(f"   Clases:      {len(metrics['unique_classes'])} categorías")
        
        self.results = results
        return results
    
    def create_summary_table(self) -> pd.DataFrame:
        """
        Crea tabla resumen con las métricas principales.
        
        Returns:
            DataFrame con resumen de métricas
        """
        if not self.results:
            return pd.DataFrame()
        
        summary_data = []
        
        for dim_name, metrics in self.results.items():
            summary_data.append({
                'Dimensión': dim_name,
                'N': metrics['total_samples'],
                'Accuracy': f"{metrics['accuracy']:.3f}",
                'Precision': f"{metrics['precision_macro']:.3f}",
                'Recall': f"{metrics['recall_macro']:.3f}",
                'F1-Score': f"{metrics['f1_macro']:.3f}",
                'Coincidencias': f"{metrics['exact_matches']}/{metrics['total_samples']}",
                'Categorías': len(metrics['unique_classes'])
            })

        accuracies = [float(row['Accuracy']) for row in summary_data]
        precisions = [float(row['Precision']) for row in summary_data]
        recalls = [float(row['Recall']) for row in summary_data]
        f1s = [float(row['F1-Score']) for row in summary_data]
        
        summary_data.append({
            'Dimensión': 'PROMEDIO',
            'N': summary_data[0]['N'],
            'Accuracy': f"{np.mean(accuracies):.3f}",
            'Precision': f"{np.mean(precisions):.3f}",
            'Recall': f"{np.mean(recalls):.3f}",
            'F1-Score': f"{np.mean(f1s):.3f}",
            'Coincidencias': '-',
            'Categorías': '-'
        })
        
        return pd.DataFrame(summary_data)
    
    def print_detailed_results(self):
        """
        Imprime resultados detallados por categoría.
        """
        if not self.results:
            print("❌ No hay resultados disponibles.")
            return
        
        print("\nRESULTADOS DETALLADOS POR CATEGORÍA")
     
        for dim_name, metrics in self.results.items():
            print(f"\n🔸 {dim_name.upper()}")
            print("-" * 40)
            
            print(f"{'Categoría':<15} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'Support':<8}")
            print("-" * 55)
            
            for i, class_name in enumerate(metrics['unique_classes']):
                precision = metrics['precision_per_class'][i]
                recall = metrics['recall_per_class'][i]
                f1 = metrics['f1_per_class'][i]
                support = metrics['support_per_class'][i]
                
                print(f"{class_name:<15} {precision:<10.3f} {recall:<10.3f} {f1:<10.3f} {support:<8}")
    
    def save_results(self, filename: str = 'evaluacion_gpt4o_simple.xlsx'):
        """
        Guarda resultados en Excel.
        
        Args:
            filename: Nombre del archivo de salida
        """
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:

                summary_df = self.create_summary_table()
                summary_df.to_excel(writer, sheet_name='Resumen', index=False)
                
                if self.data is not None:
                    self.data.to_excel(writer, sheet_name='Datos_Originales', index=False)
                
                for dim_name, metrics in self.results.items():
                    detail_data = []
                    detail_data.append(['Categoría', 'Precision', 'Recall', 'F1-Score', 'Support'])
                    
                    for i, class_name in enumerate(metrics['unique_classes']):
                        detail_data.append([
                            class_name,
                            f"{metrics['precision_per_class'][i]:.4f}",
                            f"{metrics['recall_per_class'][i]:.4f}",
                            f"{metrics['f1_per_class'][i]:.4f}",
                            str(metrics['support_per_class'][i])
                        ])
                    
                    detail_df = pd.DataFrame(detail_data[1:], columns=detail_data[0])
                    sheet_name = dim_name.replace(' ', '_')[:31]
                    detail_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"Resultados guardados en: {filename}")
            
        except Exception as e:
            print(f"Error guardando resultados: {e}")
    
    def generate_latex_table(self) -> str:
        """
        Genera tabla LaTeX para trabajo de grado.
        
        Returns:
            String con código LaTeX
        """
        if not self.results:
            return ""
        
        latex = """\\begin{table}[htbp]
            \\centering
            \\caption{Evaluación de Precisión del Modelo GPT-4o}
            \\label{tab:gpt4o_precision}
            \\begin{tabular}{|l|c|c|c|c|c|}
            \\hline
            \\textbf{Dimensión} & \\textbf{Accuracy} & \\textbf{Precision} & \\textbf{Recall} & \\textbf{F1-Score} & \\textbf{N} \\\\
            \\hline\n"""
        
        for dim_name, metrics in self.results.items():
            latex += f"{dim_name} & {metrics['accuracy']:.3f} & {metrics['precision_macro']:.3f} & "
            latex += f"{metrics['recall_macro']:.3f} & {metrics['f1_macro']:.3f} & {metrics['total_samples']} \\\\\n"
        
        accuracies = [m['accuracy'] for m in self.results.values()]
        precisions = [m['precision_macro'] for m in self.results.values()]
        recalls = [m['recall_macro'] for m in self.results.values()]
        f1s = [m['f1_macro'] for m in self.results.values()]
        
        latex += "\\hline\n"
        latex += f"\\textbf{{Promedio}} & {np.mean(accuracies):.3f} & {np.mean(precisions):.3f} & "
        latex += f"{np.mean(recalls):.3f} & {np.mean(f1s):.3f} & {list(self.results.values())[0]['total_samples']} \\\\\n"
        
        latex += """\\hline
            \\end{tabular}
            \\note{N = número de muestras evaluadas}
            \\end{table}"""
        
        return latex

def main():
    """
    Función principal para ejecutar la evaluación simple.
    """
    print("EVALUADOR SIMPLE DE PRECISIÓN - GPT-4o")
    print("Análisis de Sentimientos y Emociones")
    
    evaluator = SimpleClassificationEvaluator()
    
    data = evaluator.load_data('datasets_procesados/dataset_evaluacion_ia_wide.csv')
    if data is None:
        return
    
    print(f"\nVista previa de los datos:")
    print(data[['Sentimiento_Humano', 'Sentimiento_IA', 'Emocion_Candidato_Humano', 'Emocion_Candidato_IA']].head())
    
    results = evaluator.evaluate_dimensions()
    
    if not results:
        return
    
    print(f"\nTABLA RESUMEN")
    summary_table = evaluator.create_summary_table()
    print(summary_table.to_string(index=False))
    
    evaluator.print_detailed_results()
    
    avg_accuracy = np.mean([r['accuracy'] for r in results.values()])
    avg_f1 = np.mean([r['f1_macro'] for r in results.values()])
    
    print(f"\nINTERPRETACIÓN")
    print(f"Precisión promedio: {avg_accuracy:.1%}")
    print(f"F1-Score promedio: {avg_f1:.3f}")
    
    if avg_accuracy >= 0.8:
        interpretation = "Excelente"
    elif avg_accuracy >= 0.7:
        interpretation = "Buena"
    elif avg_accuracy >= 0.6:
        interpretation = "Aceptable"
    else:
        interpretation = "Necesita mejora"
    
    print(f"Evaluación general: {interpretation}")
    
    evaluator.save_results()
    
    latex_code = evaluator.generate_latex_table()
    with open('tabla_precision_gpt4o.tex', 'w', encoding='utf-8') as f:
        f.write(latex_code)
    
    print(f"\nARCHIVOS GENERADOS:")
    print(f"evaluacion_gpt4o_simple.xlsx")
    print(f"tabla_precision_gpt4o.tex")
    
    print(f"\nREFERENCIA PARA CITAR:")
    print("Sokolova, M., & Lapalme, G. (2009). A systematic analysis of")
    print("performance measures for classification tasks. Information")
    print("Processing & Management, 45(4), 427-437.")
    
    return evaluator

if __name__ == "__main__":
    evaluator = main()