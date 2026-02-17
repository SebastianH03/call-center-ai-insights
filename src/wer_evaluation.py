#!/usr/bin/env python3
"""
Script para calcular el Word Error Rate (WER) entre transcripciones manuales y automáticas.

Basado en la métrica estándar para evaluación de sistemas ASR:
WER = (S + D + I) / N
Donde:
- S: Sustituciones
- D: Eliminaciones  
- I: Inserciones
- N: Número total de palabras en la referencia

Referencia: 
Morris, A., Maier, V., & Green, P. (2004). From WER and RIL to MER and WIL: 
improved evaluation measures for connected speech recognition. 
In Proceedings of ICSLP (Vol. 4, pp. 2765-2768).
"""

import re
import unicodedata
from typing import List, Tuple, Dict
import numpy as np

def normalizar_texto(texto: str) -> str:
    """
    Normaliza el texto eliminando puntuación, tildes y caracteres especiales.
    
    Args:
        texto: Texto a normalizar
        
    Returns:
        Texto normalizado en minúsculas sin puntuación
    """

    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')
    texto = re.sub(r'[^\w\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    
    return texto

def calcular_distancia_edicion(ref_words: List[str], hyp_words: List[str]) -> Tuple[int, int, int, np.ndarray]:
    """
    Calcula la distancia de edición (Levenshtein) entre dos secuencias de palabras.
    
    Args:
        ref_words: Lista de palabras de referencia (transcripción manual)
        hyp_words: Lista de palabras de hipótesis (transcripción automática)
        
    Returns:
        Tupla con (sustituciones, eliminaciones, inserciones, matriz_dp)
    """
    n = len(ref_words)
    m = len(hyp_words)
    
    dp = np.zeros((n + 1, m + 1), dtype=int)
    
    for i in range(n + 1):
        dp[i][0] = i  
    for j in range(m + 1):
        dp[0][j] = j 

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                dp[i][j] = dp[i-1][j-1]  
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],      # Eliminación
                    dp[i][j-1],      # Inserción
                    dp[i-1][j-1]     # Sustitución
                )
    
    i, j = n, m
    sustituciones = 0
    eliminaciones = 0
    inserciones = 0
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref_words[i-1] == hyp_words[j-1]:
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
            sustituciones += 1
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
            eliminaciones += 1
            i -= 1
        elif j > 0 and dp[i][j] == dp[i][j-1] + 1:
            inserciones += 1
            j -= 1
        else:
            break
    
    return sustituciones, eliminaciones, inserciones, dp

def calcular_wer(referencia: str, hipotesis: str) -> Dict[str, float]:
    """
    Calcula el WER entre una transcripción de referencia y una hipótesis.
    
    Args:
        referencia: Transcripción manual (ground truth)
        hipotesis: Transcripción automática
        
    Returns:
        Diccionario con métricas calculadas
    """

    ref_normalizada = normalizar_texto(referencia)
    hyp_normalizada = normalizar_texto(hipotesis)
    
    ref_words = ref_normalizada.split()
    hyp_words = hyp_normalizada.split()
    
    S, D, I, _ = calcular_distancia_edicion(ref_words, hyp_words)

    N = len(ref_words)
    
    if N == 0:
        wer = float('inf') if len(hyp_words) > 0 else 0.0
        accuracy = 0.0
    else:
        wer = (S + D + I) / N
        accuracy = max(0, 1 - wer)  # La precisión no puede ser negativa
    
    return {
        'wer': wer,
        'accuracy': accuracy,
        'sustituciones': S,
        'eliminaciones': D,
        'inserciones': I,
        'total_errores': S + D + I,
        'palabras_referencia': N,
        'palabras_hipotesis': len(hyp_words)
    }

def extraer_transcripciones(archivo: str) -> List[str]:
    """
    Extrae las transcripciones individuales de un archivo de texto.
    
    Args:
        archivo: Ruta al archivo de texto
        
    Returns:
        Lista de transcripciones
    """
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        transcripciones = [t.strip() for t in contenido.split('\n\n') if t.strip()]
        
        return transcripciones
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo}")
        return []
    except Exception as e:
        print(f"Error al leer el archivo {archivo}: {e}")
        return []

def calcular_wer_total(archivo_manual: str, archivo_openai: str) -> Dict[str, float]:
    """
    Calcula el WER promedio y total entre dos archivos de transcripciones.
    
    Args:
        archivo_manual: Archivo con transcripciones manuales
        archivo_openai: Archivo con transcripciones de OpenAI
        
    Returns:
        Diccionario con resultados agregados
    """

    transcripciones_manual = extraer_transcripciones(archivo_manual)
    transcripciones_openai = extraer_transcripciones(archivo_openai)
    
    if len(transcripciones_manual) != len(transcripciones_openai):
        print(f"Advertencia: Número de transcripciones no coincide:")
        print(f"Manual: {len(transcripciones_manual)}, OpenAI: {len(transcripciones_openai)}")
        min_len = min(len(transcripciones_manual), len(transcripciones_openai))
        transcripciones_manual = transcripciones_manual[:min_len]
        transcripciones_openai = transcripciones_openai[:min_len]
    
    if not transcripciones_manual:
        print("Error: No se encontraron transcripciones válidas")
        return {}

    resultados_individuales = []
    S_total, D_total, I_total, N_total = 0, 0, 0, 0
    
    print(f"Procesando {len(transcripciones_manual)} transcripciones...\n")
    
    for i, (manual, openai) in enumerate(zip(transcripciones_manual, transcripciones_openai), 1):
        resultado = calcular_wer(manual, openai)
        resultados_individuales.append(resultado)
        
        S_total += resultado['sustituciones']
        D_total += resultado['eliminaciones']
        I_total += resultado['inserciones']
        N_total += resultado['palabras_referencia']
        
        print(f"Transcripción {i:2d}: WER = {resultado['wer']:.3f} ({resultado['accuracy']:.1%} precisión)")
        print(f"Errores: S={resultado['sustituciones']}, D={resultado['eliminaciones']}, I={resultado['inserciones']} ")
        print(f"Palabras: Ref={resultado['palabras_referencia']}, Hip={resultado['palabras_hipotesis']} ")
    
    wer_promedio = np.mean([r['wer'] for r in resultados_individuales])
    wer_total = (S_total + D_total + I_total) / N_total if N_total > 0 else float('inf')
    accuracy_promedio = np.mean([r['accuracy'] for r in resultados_individuales])
    accuracy_total = max(0, 1 - wer_total)
    
    return {
        'wer_promedio': wer_promedio,
        'wer_total': wer_total,
        'accuracy_promedio': accuracy_promedio,
        'accuracy_total': accuracy_total,
        'total_sustituciones': S_total,
        'total_eliminaciones': D_total,
        'total_inserciones': I_total,
        'total_errores': S_total + D_total + I_total,
        'total_palabras_referencia': N_total,
        'num_transcripciones': len(resultados_individuales),
        'resultados_individuales': resultados_individuales
    }

def mostrar_resultados(resultados: Dict[str, float]):
    """
    Muestra los resultados del análisis WER de forma formateada.
    """
    print("RESULTADOS DEL ANÁLISIS WER")
    print(f"Número de transcripciones analizadas: {resultados['num_transcripciones']}")
    print(f"Total de palabras en referencia: {resultados['total_palabras_referencia']}")
    print()
    print("MÉTRICAS TOTALES (recomendadas para reportar):")
    print(f"  WER Total:       {resultados['wer_total']:.3f} ({resultados['wer_total']*100:.1f}%)")
    print(f"  Precisión Total: {resultados['accuracy_total']:.3f} ({resultados['accuracy_total']*100:.1f}%)")
    print()
    print("MÉTRICAS PROMEDIO:")
    print(f"  WER Promedio:       {resultados['wer_promedio']:.3f} ({resultados['wer_promedio']*100:.1f}%)")
    print(f"  Precisión Promedio: {resultados['accuracy_promedio']:.3f} ({resultados['accuracy_promedio']*100:.1f}%)")
    print()
    print("DESGLOSE DE ERRORES:")
    print(f"  Sustituciones: {resultados['total_sustituciones']}")
    print(f"  Eliminaciones: {resultados['total_eliminaciones']}")
    print(f"  Inserciones:   {resultados['total_inserciones']}")
    print(f"  Total errores: {resultados['total_errores']}")
    print()
    print("FÓRMULA APLICADA:")
    print(f"  WER = (S + D + I) / N ")
    print(f"  WER = ({resultados['total_sustituciones']} + {resultados['total_eliminaciones']} + {resultados['total_inserciones']}) / {resultados['total_palabras_referencia']}")
    print(f"  WER = {resultados['total_errores']} / {resultados['total_palabras_referencia']} = {resultados['wer_total']:.3f}")

if __name__ == "__main__":
    # Rutas de los archivos
    archivo_manual = "transcripcionManual.txt"
    archivo_openai = "transcripcionOpenAI.txt"
    
    print("Calculando WER entre transcripciones manuales y de OpenAI...")
    print("=" * 60)
    
    # Calcular WER
    resultados = calcular_wer_total(archivo_manual, archivo_openai)
    
    if resultados:
        mostrar_resultados(resultados)
        
        # Guardar resultados en archivo
        with open("resultados_wer.txt", "w", encoding="utf-8") as f:
            f.write("RESULTADOS DEL ANÁLISIS WER\n")
            f.write("=" * 60 + "\n")
            f.write(f"WER Total: {resultados['wer_total']:.3f} ({resultados['wer_total']*100:.1f}%)\n")
            f.write(f"Precisión Total: {resultados['accuracy_total']:.3f} ({resultados['accuracy_total']*100:.1f}%)\n")
            f.write(f"Total de errores: {resultados['total_errores']}\n")
            f.write(f"Total de palabras: {resultados['total_palabras_referencia']}\n")
        
        print(f"\nResultados guardados en 'resultados_wer.txt'")
    else:
        print("No se pudieron procesar las transcripciones.")