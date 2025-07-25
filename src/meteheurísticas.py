# -*- coding: utf-8 -*-
"""meteheurísticas.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kuxboIsxYFLOrEQdOV3k7F7dBHY6_rmW
"""

import pandas as pd
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import copy
from operator import itemgetter
import math
import time
import matplotlib.pyplot as plt
from src.acciones import ejecuta_decoding, ejecuta_decoding_pacientes, asigna_recurso

# ------------------------------
# BLOQUE 1: Metaheurística colonia de hormigas POR ACTIVIDADES
# ------------------------------

# Funciones auxiliares

# Utilizar la solución inicial para ajustar las feromonas - ACO1
def ajustar_feromonas_iniciales_1(feromonas, solucion_inicial, calidad_inicial):
    feromonas[0][solucion_inicial[0]] += calidad_inicial
    for i in range(len(solucion_inicial) - 1):
        feromonas[solucion_inicial[i]][solucion_inicial[i+1]] += calidad_inicial  # Ajustar según la calidad de tu solución inicial
    return feromonas

# Utilizar la solución inicial para ajustar las feromonas - ACO2 y ACO3
def ajustar_feromonas_iniciales(feromonas, solucion_inicial, calidad_inicial):
    for i in range(len(solucion_inicial) - 1):
        # Los indices de las actividades son uno menos
        feromonas[solucion_inicial[i]-1][solucion_inicial[i+1]-1] += calidad_inicial
    return feromonas


# Función para generar la matriz de costos, teniendo en cuenta las restricciones
# Actividades : Actividad	| Paciente	| Prioridad	| TR	| Recursos_Necesarios	| Tiempo
# ACO1
def generar_matriz_costos_1(actividades, orden_actividades_por_paciente):
    num_actividades = len(actividades)
    matriz_costos = np.full((num_actividades + 1, num_actividades + 1), np.inf)  # Incluye nodo de inicio

    # Identificar las primeras actividades de cada paciente
    primeras_actividades = [actividades[0] for actividades in orden_actividades_por_paciente.values()]

    # Asignar costos desde el nodo de inicio a las primeras actividades
    for actividad in primeras_actividades:
        tiempo = actividades[actividad - 1][5]  # Tiempo de la actividad
        prioridad = actividades[actividad - 1][2]  # Prioridad del paciente de la actividad
        matriz_costos[0][actividad] = calcular_costo(tiempo, prioridad)

    # Asignar costos entre actividades normales
    for i in range(1, num_actividades + 1):
        for j in range(1, num_actividades + 1):
            if i != j:  # Asegurarse de que no se esté calculando el costo de una actividad a sí misma
                if es_transicion_valida(actividades[i - 1][:2], actividades[j - 1][:2], orden_actividades_por_paciente):
                    tiempo = actividades[j - 1][5]  # Tiempo de la actividad destino
                    prioridad = actividades[j - 1][2]  # Prioridad del paciente de la actividad destino
                    matriz_costos[i][j] = calcular_costo(tiempo, prioridad)

    return matriz_costos
# ACO2 y ACO3
def generar_matriz_costos(actividades,orden_actividades_por_paciente):
    num_actividades = len(actividades)
    matriz_costos = np.full((num_actividades, num_actividades), np.inf)

    # Asignar costos en base a tiempo de ocupación y prioridad del paciente
    for i in range(num_actividades):
        for j in range(num_actividades):
            if i != j:  # Asegurarse de que no se esté calculando el costo de una actividad a sí misma
                # Solo se consideran transiciones válidas
                if es_transicion_valida(actividades[i][:2], actividades[j][:2], orden_actividades_por_paciente):
                    tiempo = actividades[j][5]  # Tiempo de la actividad destino
                    prioridad = actividades[j][2]  # Prioridad del paciente de la actividad destino
                    matriz_costos[i][j] = calcular_costo(tiempo, prioridad)

    return matriz_costos

def es_transicion_valida(actividad_origen, actividad_destino, orden_actividades_por_paciente):
    paciente_origen = actividad_origen[1]
    paciente_destino = actividad_destino[1]
    actividad_origen_id = actividad_origen[0]
    actividad_destino_id = actividad_destino[0]

    # Validación intra-paciente
    if paciente_origen == paciente_destino:
        indice_origen = orden_actividades_por_paciente[paciente_origen].index(actividad_origen_id)
        indice_destino = orden_actividades_por_paciente[paciente_destino].index(actividad_destino_id)
        return indice_destino == indice_origen + 1 # Devuelve true solo si es justo la actividad que precede a la de origen

    # Validación inter-paciente
    else:
      return True

# Calcular coste de ir a una actividad
def calcular_costo(tiempo, prioridad):
    base_cost = 10  # Costo base para cualquier transición
    costo = base_cost + tiempo - (6-prioridad)
    return costo

def seleccionar_proxima_actividad(alpha, beta, q0, actividades_por_añadir, actividades, feromonas, matriz_costos, orden_actividades_por_paciente, actividades_seleccionadas_por_hormiga):

    if not actividades_por_añadir:
        return None, actividades_por_añadir

    actividad_actual = actividades_seleccionadas_por_hormiga[-1]
    transiciones_validas = []

    for actividad_destino in actividades_por_añadir:
        # Verificar que todas las actividades previas del paciente asociado a esta actividad se hayan completado
        for a in actividades:
          if actividad_destino == a[0]:
            paciente_destino = a[1]
            break

        actividades_previas = orden_actividades_por_paciente[paciente_destino][:orden_actividades_por_paciente[paciente_destino].index(actividad_destino)]

        if all(actividad_previa in actividades_seleccionadas_por_hormiga for actividad_previa in actividades_previas):
          transiciones_validas.append(actividad_destino)

    if not transiciones_validas:  # Si no hay transiciones válidas
        return None, actividades_por_añadir

    # Decision de explotación vs exploración
    if random.random() < q0:
        # Explotación: elegir el mejor basado en feromonas y costo (heurística)
        mejor_costo = 0
        seleccionado = None

        for actividad_destino in transiciones_validas:
            tau = feromonas[int(actividad_actual)-1][int(actividad_destino)-1]  # Cantidad de feromona
            costo= matriz_costos[int(actividad_actual)-1][int(actividad_destino)-1] # Valor costo
            eta = 1 / costo if costo != float('inf') else 0  # Inversa del costo como heurística
            valor = (tau ** alpha) * (eta ** beta)
            if valor > mejor_costo:
                mejor_costo = valor
                seleccionado = actividad_destino

        actividades_por_añadir.remove(seleccionado)
        return seleccionado, actividades_por_añadir
    else:
        # Exploración: elegir basado en una distribución de probabilidades proporcional a feromonas y heurística
        probabilidades = []
        for actividad_destino in transiciones_validas:
            tau = feromonas[int(actividad_actual)-1][int(actividad_destino)-1]  # Cantidad de feromona
            costo= matriz_costos[int(actividad_actual)-1][int(actividad_destino)-1] # Valor costo
            eta = 1 / costo if costo != float('inf') else 0

            probabilidades.append((tau ** alpha) * (eta ** beta))

        # Normalizar las probabilidades
        suma_probabilidades = sum(probabilidades)
        if suma_probabilidades == 0:
            return None, actividades_por_añadir  # En caso de que todas las probabilidades sean 0

        probabilidades_normalizadas = [prob / suma_probabilidades for prob in probabilidades]
        seleccionado = np.random.choice(transiciones_validas, p=probabilidades_normalizadas)

        actividades_por_añadir.remove(seleccionado)

        return seleccionado, actividades_por_añadir

def generar_solucion_hormiga_1(best_sol_i, feromonas, matriz_costos,orden_actividades_por_paciente, actividades,alpha, beta, q0):

  actividades_seleccionadas_por_hormiga = [0]
  actividades_por_añadir = copy.copy(best_sol_i)

  # Mientras que la solución no esté completa
  while len(actividades_seleccionadas_por_hormiga) < len(best_sol_i)+1:
            prox_actividad, actividades_por_añadir = seleccionar_proxima_actividad(alpha, beta, q0,actividades_por_añadir, actividades, feromonas, matriz_costos, orden_actividades_por_paciente, actividades_seleccionadas_por_hormiga)
            actividades_seleccionadas_por_hormiga.append(prox_actividad)

  return actividades_seleccionadas_por_hormiga[1:]  # Omitir el nodo de inicio en el resultado final

def generar_solucion_hormiga(best_sol_i, feromonas, matriz_costos,orden_actividades_por_paciente, actividades, actividad_inicial,alpha, beta, q0):
  # Elegir una actividad de inicio en función del algoritmo
  actividades_seleccionadas_por_hormiga = []
  actividades_seleccionadas_por_hormiga.append(actividad_inicial)
  actividades_por_añadir = copy.copy(best_sol_i)
  actividades_por_añadir.remove(actividad_inicial)

  # Mientras que la solución no esté completa
  while len(actividades_seleccionadas_por_hormiga) < len(best_sol_i):
            prox_actividad, actividades_por_añadir = seleccionar_proxima_actividad(alpha, beta, q0,actividades_por_añadir, actividades, feromonas, matriz_costos, orden_actividades_por_paciente, actividades_seleccionadas_por_hormiga)
            actividades_seleccionadas_por_hormiga.append(prox_actividad)

  return actividades_seleccionadas_por_hormiga

# Actualización de feromonas
def actualizar_feromonas_1(matriz_feromonas, solucion_hormiga, calidad_solucion, evaporacion):
    # Evaporación de feromonas
    matriz_feromonas *= (1 - evaporacion)

    # Aumentamos feromona en el arco de inicio
    matriz_feromonas[0][solucion_hormiga[0]] += calidad_solucion

    for i in range(len(solucion_hormiga)-1):
            # Aumentar las feromonas basado en la calidad de la solución
            matriz_feromonas[solucion_hormiga[i]][solucion_hormiga[i+1]] += calidad_solucion

    return matriz_feromonas

def actualizar_feromonas(matriz_feromonas, soluciones_hormigas, calidad_soluciones, evaporacion):
    # Evaporación de feromonas
    matriz_feromonas *= (1 - evaporacion)

    for i in range(len(soluciones_hormigas)-1):
            # Aumentar las feromonas basado en la calidad de la solución
            matriz_feromonas[soluciones_hormigas[i]-1][soluciones_hormigas[i+1]-1] += calidad_soluciones

    return matriz_feromonas
def calcular_calidad_solucion(FO_decoding):
    if FO_decoding > 0:
        return 100 / FO_decoding
    else:
        return float('inf')  # En caso de que tiempo_total sea 0, lo cual es improbable en escenarios reales.

# ------------------------------
# ACO1
# ------------------------------
def algoritmo_aco1(tiempo_computacion,num_hormigas, parametros ,Q_0, FO_inicial, solucion_inicial, actividades, orden_actividades_por_paciente, df_pacientes, df_recursos_final, df_datos, array_pacientes, TR, R, CR):
    # Inicializar parametros
    num_actividades = len(actividades)  # Ajustar según tu caso

    alpha = parametros[0] # Influencia de la feromona
    beta = parametros [1] # Influencia de la información heurística
    evaporacion = parametros[2] # Tasa de evaporación de la feromona
    q0 = Q_0

    feromonas = np.ones((num_actividades+1, num_actividades+1))
    primeras_actividades = [actividades[0] for actividades in orden_actividades_por_paciente.values()]
    coste_inicial= calcular_calidad_solucion(FO_inicial)
    feromonas = ajustar_feromonas_iniciales_1(feromonas, solucion_inicial, coste_inicial)

    matriz_costo = generar_matriz_costos_1(actividades,orden_actividades_por_paciente)

    best_hormiga = [solucion_inicial]
    best_hormiga_calidad = [coste_inicial]
    best_hormiga_FO = [FO_inicial]
    best_sol_i = solucion_inicial

    # Crear un DataFrame vacío
    df = pd.DataFrame(columns=['Iteracion','FO','Algoritmo'])

    tiempo_inicial = time.time()
    best_value = float('inf')
    counter = 0
    iteracion = 0


    while (time.time() - tiempo_inicial) < tiempo_computacion:
        iteracion += 1

        soluciones_hormigas = []
        calidad_soluciones = []
        FO_soluciones = []
        tiempo_cero = time.time()

        # Generar soluciones para cada hormiga
        for hormiga in range(num_hormigas):

            solucion_hormiga = generar_solucion_hormiga_1(best_sol_i, feromonas, matriz_costo, orden_actividades_por_paciente, actividades,alpha, beta, q0)
            FO_hormiga, df_datos_unido, df_pacientes = ejecuta_decoding(solucion_hormiga, df_pacientes, df_recursos_final, df_datos,array_pacientes, TR, R, CR)  # Implementar evaluación de la solución. Calcular su FO
            soluciones_hormigas.append(solucion_hormiga)
            calidad_soluciones.append(calcular_calidad_solucion(FO_hormiga))
            FO_soluciones.append(FO_hormiga)

        indice_best_hormiga = FO_soluciones.index(min(FO_soluciones))
        # Guardamos la mejor solucion de esta vuelta
        best_hormiga.append(soluciones_hormigas[indice_best_hormiga])
        best_hormiga_calidad.append(calidad_soluciones[indice_best_hormiga])
        best_hormiga_FO.append(FO_soluciones[indice_best_hormiga])
        feromonas = actualizar_feromonas_1(feromonas, soluciones_hormigas[indice_best_hormiga], calidad_soluciones[indice_best_hormiga], evaporacion)

        best_sol_i = best_hormiga[best_hormiga_calidad.index(max(best_hormiga_calidad))] # Sirve solo en caso de lanzar ACO_3 (si no solo vale para saber las actividades que hay)
        # Agregar valores al DataFrame usando loc
        df.loc[len(df)] = [iteracion, FO_soluciones[indice_best_hormiga],'ACO1']

        # Contador de mejores soluciones
        for index, row in df.iterrows():
            current_value = row['FO']
            if current_value < best_value:
                best_value = current_value
                counter += 1


    best_sol = best_hormiga[best_hormiga_FO.index(min(best_hormiga_FO))]
    FO_best = min(best_hormiga_FO)
    return best_sol, df, FO_best,counter,df_datos_unido

# ------------------------------
# ACO2
# ------------------------------

def algoritmo_aco2(tiempo_computacion,num_hormigas, parametros ,Q_0, FO_inicial, solucion_inicial, actividades, orden_actividades_por_paciente, df_pacientes, df_recursos_final, df_datos, array_pacientes,TR, R, CR):
    # Inicializar parametros
    num_actividades = len(actividades)  # Ajustar según tu caso

    alpha = parametros[0] # Influencia de la feromona
    beta = parametros [1] # Influencia de la información heurística
    evaporacion = parametros[2] # Tasa de evaporación de la feromona
    q0 = Q_0
    feromonas = np.ones((num_actividades, num_actividades))
    best_hormiga = []
    best_hormiga_calidad = []
    best_hormiga_FO = []
    # Crear un DataFrame vacío
    df = pd.DataFrame(columns=['Iteracion','FO','Algoritmo'])
    # Inicializar las feromonas según solución inicial
    coste_inicial= calcular_calidad_solucion(FO_inicial)
    feromonas = ajustar_feromonas_iniciales(feromonas, solucion_inicial, coste_inicial)
    matriz_costo = generar_matriz_costos(actividades,orden_actividades_por_paciente)
    best_hormiga.append(solucion_inicial)
    best_hormiga_calidad.append(coste_inicial)
    best_sol_i = solucion_inicial # ACO 2 Y 3
    tiempo_inicial = time.time()
    best_value = float('inf')
    counter = 0
    iteracion = 0


    while (time.time() - tiempo_inicial) < tiempo_computacion:
        iteracion += 1

        soluciones_hormigas = []
        calidad_soluciones = []
        FO_soluciones = []
        tiempo_cero = time.time()
        # Generar soluciones para cada hormiga
        for hormiga in range(num_hormigas):
            paciente_inicial = np.random.choice(range(1,len(orden_actividades_por_paciente)))
            actividad_inicial = orden_actividades_por_paciente[paciente_inicial][0] # ACO 2

            solucion_hormiga = generar_solucion_hormiga(best_sol_i, feromonas, matriz_costo, orden_actividades_por_paciente, actividades, actividad_inicial,alpha, beta, q0)
            FO_hormiga, df_datos_unido, df_pacientes = ejecuta_decoding(solucion_hormiga, df_pacientes, df_recursos_final, df_datos,array_pacientes, TR, R, CR)  # Implementar evaluación de la solución. Calcular su FO
            soluciones_hormigas.append(solucion_hormiga)
            calidad_soluciones.append(calcular_calidad_solucion(FO_hormiga))  # Implementar evaluación de la solución
            FO_soluciones.append(FO_hormiga)


        # Actualizar feromonas
        tiempo_fin = time.time()

        indice_best_hormiga = FO_soluciones.index(min(FO_soluciones))
        best_hormiga.append(soluciones_hormigas[indice_best_hormiga]) # Guardamos la mejor solucion de esta vuelta
        best_hormiga_calidad.append(calidad_soluciones[indice_best_hormiga])
        best_hormiga_FO.append(FO_soluciones[indice_best_hormiga])
        feromonas = actualizar_feromonas(feromonas, soluciones_hormigas[indice_best_hormiga], calidad_soluciones[indice_best_hormiga], evaporacion)

        best_sol_i = best_hormiga[best_hormiga_calidad.index(max(best_hormiga_calidad))] # Sirve solo en caso de lanzar ACO_3 (si no solo vale para saber las actividades que hay)
        # Agregar valores al DataFrame usando loc
        df.loc[len(df)] = [iteracion, FO_soluciones[indice_best_hormiga],'ACO2']

        # Contador de mejores soluciones
        for index, row in df.iterrows():
            current_value = row['FO']
            if current_value < best_value:
                best_value = current_value
                counter += 1


    best_sol = best_hormiga[best_hormiga_FO.index(min(best_hormiga_FO))]
    FO_best = min(best_hormiga_FO)
    return best_sol, df, FO_best,counter, df_datos_unido

# ------------------------------
# ACO3
# ------------------------------
def algoritmo_aco3(tiempo_computacion, num_hormigas, parametros ,Q_0, FO_inicial, solucion_inicial, actividades, orden_actividades_por_paciente, df_pacientes, df_recursos_final, df_datos, array_pacientes, TR, R, CR):
    # Inicializar parametros
    num_actividades = len(actividades)  # Ajustar según tu caso

    alpha = parametros[0] # Influencia de la feromona
    beta = parametros [1] # Influencia de la información heurística
    evaporacion = parametros[2] # Tasa de evaporación de la feromona
    q0 = Q_0
    feromonas = np.ones((num_actividades, num_actividades))
    best_hormiga = []
    best_hormiga_calidad = []
    best_hormiga_FO = []
    # Crear un DataFrame vacío
    df = pd.DataFrame(columns=['Iteracion','FO','Algoritmo'])
    # Inicializar las feromonas según solución inicial
    coste_inicial= calcular_calidad_solucion(FO_inicial)
    feromonas = ajustar_feromonas_iniciales(feromonas, solucion_inicial, coste_inicial)
    matriz_costo = generar_matriz_costos(actividades,orden_actividades_por_paciente)
    best_hormiga.append(solucion_inicial)
    best_hormiga_calidad.append(coste_inicial)
    best_sol_i = solucion_inicial # ACO 2 Y 3
    tiempo_inicial = time.time()
    best_value = float('inf')
    counter = 0
    iteracion = 0


    while (time.time() - tiempo_inicial) < tiempo_computacion:
        iteracion += 1

        soluciones_hormigas = []
        calidad_soluciones = []
        FO_soluciones = []
        tiempo_cero = time.time()
        # Generar soluciones para cada hormiga
        for hormiga in range(num_hormigas):
            actividad_inicial = best_sol_i[0] # ACO 3


            solucion_hormiga = generar_solucion_hormiga(best_sol_i, feromonas, matriz_costo, orden_actividades_por_paciente, actividades, actividad_inicial,alpha, beta, q0)
            FO_hormiga, df_datos_unido, df_pacientes = ejecuta_decoding(solucion_hormiga, df_pacientes, df_recursos_final, df_datos,array_pacientes, TR, R, CR)  # Implementar evaluación de la solución. Calcular su FO
            soluciones_hormigas.append(solucion_hormiga)
            calidad_soluciones.append(calcular_calidad_solucion(FO_hormiga))  # Implementar evaluación de la solución
            FO_soluciones.append(FO_hormiga)
            #print(calcular_calidad_solucion(FO_hormiga))

        # Actualizar feromonas
        tiempo_fin = time.time()
        #indice_best_hormiga = calidad_soluciones.index(max(calidad_soluciones))
        indice_best_hormiga = FO_soluciones.index(min(FO_soluciones))
        best_hormiga.append(soluciones_hormigas[indice_best_hormiga]) # Guardamos la mejor solucion de esta vuelta
        best_hormiga_calidad.append(calidad_soluciones[indice_best_hormiga])
        best_hormiga_FO.append(FO_soluciones[indice_best_hormiga])
        feromonas = actualizar_feromonas(feromonas, soluciones_hormigas[indice_best_hormiga], calidad_soluciones[indice_best_hormiga], evaporacion)

        best_sol_i = best_hormiga[best_hormiga_calidad.index(max(best_hormiga_calidad))] # Sirve solo en caso de lanzar ACO_3 (si no solo vale para saber las actividades que hay)
        # Agregar valores al DataFrame usando loc
        df.loc[len(df)] = [iteracion, FO_soluciones[indice_best_hormiga],'ACO3']

        # Contador de mejores soluciones
        for index, row in df.iterrows():
            current_value = row['FO']
            if current_value < best_value:
                best_value = current_value
                counter += 1


    best_sol = best_hormiga[best_hormiga_FO.index(min(best_hormiga_FO))]
    FO_best = min(best_hormiga_FO)
    return best_sol, df, FO_best, counter,df_datos_unido

# ------------------------------
# BLOQUE 2: Metaheurística colonia de hormigas POR PACIENTES
# ------------------------------

# FUNCIONES AUXILIARES (diferentes a las definidas)


# Función para generar la matriz de costos - EN ESTE CASO NO HAY RESTRICCIONES DE PRECEDENCIA
# actividades : Actividad	| Paciente	| Prioridad	| TR	| Recursos_Necesarios	| Tiempo
def generar_matriz_costos_pacietes(df_pacientes):
    n_pacientes = len(df_pacientes)  # Número de pacientes
    matriz_costos = np.full((n_pacientes, n_pacientes), np.inf)  # Inicializa la matriz de costos

    # Calcula el costo de transición de cada paciente a todos los demás
    for i in range(n_pacientes):
        for j in range(n_pacientes):
            if i != j:  # Asegura que no se calcule el costo de un paciente a sí mismo
                prioridad_j = df_pacientes.at[j,'Prioridad']
                visto_j = df_pacientes.at[j, 'visto']
                # Calcula el costo según la prioridad y si ha sido visto
                costo = (1 / (6 - prioridad_j)) * (1 - 0.2 * visto_j)
                matriz_costos[i][j] = costo

    return matriz_costos


# Selección de el proximo paciente
def seleccionar_proximo_paciente(pacientes_seleccionados_por_hormiga, matriz_feromonas, matriz_costos, alpha, beta, q0):
    ultimo_paciente = pacientes_seleccionados_por_hormiga[-1]
    candidatos = [i for i in range(len(matriz_costos)) if i not in pacientes_seleccionados_por_hormiga]
    probabilidades = []

    if random.random() < q0:  # Explotación: selecciona el mejor candidato con alta probabilidad q0
        mejor_costo = 0
        seleccionado = None
        for candidato in candidatos:
            # Considera la inversa del costo por la cantidad de feromona para encontrar el 'mejor' camino
            tau = matriz_feromonas[ultimo_paciente][candidato]  # Intensidad de la feromona
            costo = matriz_costos[ultimo_paciente][candidato]
            eta = 1 / costo if costo != float('inf') else 0  # Inversa del costo como heurística
            # Utilizamos un producto de feromonas y heurística, buscando el máximo
            valor = (tau ** alpha) * (eta ** beta)

            if valor > mejor_costo:
                mejor_costo = valor
                seleccionado = candidato

    else:  # Exploración: selecciona un candidato basado en una distribución de probabilidad
      for candidato in candidatos:
        tau = matriz_feromonas[ultimo_paciente][candidato]
        eta = 1/matriz_costos[ultimo_paciente][candidato]
        probabilidades.append((tau ** alpha) * (eta ** beta))

      suma_probabilidades = sum(probabilidades)
      probabilidades_normalizadas = [p/suma_probabilidades for p in probabilidades]
      # Selecciona un candidato de manera aleatoria ponderada por las probabilidades normalizadas
      seleccionado = random.choices(candidatos, weights=probabilidades_normalizadas, k=1)[0]

    return seleccionado

# Actualización de feromonas
def actualizar_feromonas_pacientes(matriz_feromonas, solucion, calidad, tasa_evaporacion):

    # Evaporación de feromonas
      # Evaporación de feromonas
    for i in range(len(matriz_feromonas)):
      for j in range(len(matriz_feromonas)):
        matriz_feromonas[i][j] *= (1 - tasa_evaporacion)

    # Refuerzo de feromonas para cada solución encontrada por las hormigas
    #for solucion, calidad in zip(soluciones, calidad_soluciones):
    for i in range(len(solucion)-1):
            # Aumentar las feromonas basado en la calidad de la solución
           matriz_feromonas[solucion[i]-1][solucion[i+1]-1] += calidad

    return matriz_feromonas

# ------------------------------
# ACO4
# ------------------------------


def algoritmo_aco_pacientes(FO_inicial,solucion_inicial, num_hormigas, df_pacientes ,df_recursos_final, df_datos, alpha, beta, ro, q0, TR, R, CR):
    num_pacientes = len(df_pacientes)

    # Inicialización de la matriz de feromonas
    matriz_feromonas = [[1 for _ in range(num_pacientes)] for _ in range(num_pacientes)]

    # Inicializamos feromonas según la solución inicial
    calidad_inicial = calcular_calidad_solucion(FO_inicial)
    feromonas = ajustar_feromonas_iniciales(matriz_feromonas, solucion_inicial, calidad_inicial)
    matriz_costos = generar_matriz_costos_pacietes(df_pacientes)  # Suponiendo que ya tienes una lista 'pacientes' definida

    mejor_solucion = []
    mejor_solucion_calidad = []
    mejor_solucion_FO = []
    tiempo_inicial = time.time()
    # Crear un DataFrame vacío
    df = pd.DataFrame(columns=['Iteracion','FO'])
    iteracion = 0

    while (time.time() - tiempo_inicial) < 42.1875:
        soluciones = []  # Lista para almacenar las soluciones de esta iteración
        calidad_soluciones = []
        FO_soluciones = []
        iteracion += 1
        for n in range(num_hormigas):
            pacientes_seleccionados_por_hormiga = [random.randint(0, num_pacientes-1)]  # Inicia con un paciente aleatorio

            while len(pacientes_seleccionados_por_hormiga) < num_pacientes:
                proximo_paciente = seleccionar_proximo_paciente(pacientes_seleccionados_por_hormiga, matriz_feromonas, matriz_costos, alpha, beta, q0) #pacientes_seleccionados_por_hormiga, matriz_feromonas, matriz_costos, alpha, beta, q0
                pacientes_seleccionados_por_hormiga.append(proximo_paciente)

            # Calcula el costo de la solución encontrada (en función de la FO)
            pacientes_seleccionados_por_hormiga = [x + 1 for x in pacientes_seleccionados_por_hormiga]
            FO_hormiga, df_pacientes, df_datos_unido = ejecuta_decoding_pacientes(df_datos ,df_pacientes, pacientes_seleccionados_por_hormiga, df_recursos_final, TR, R, CR)  # Implementar evaluación de la solución. Calcular su FO
            soluciones.append(pacientes_seleccionados_por_hormiga)
            calidad_soluciones.append(calcular_calidad_solucion(FO_hormiga))  # Implementar evaluación de la solución
            FO_soluciones.append(FO_hormiga)


        # Opcional: Imprimir el mejor camino y su costo de la iteración
        #indice_mejor_hormiga = calidad_soluciones.index(max(calidad_soluciones))
        indice_mejor_hormiga = FO_soluciones.index(min(FO_soluciones))
        mejor_solucion.append(soluciones[indice_mejor_hormiga])
        mejor_solucion_calidad.append(calidad_soluciones[indice_mejor_hormiga])
        mejor_solucion_FO.append(FO_soluciones[indice_mejor_hormiga])
        df.loc[len(df)] = [iteracion, FO_soluciones[indice_mejor_hormiga]]

         # Actualiza la matriz de feromonas con la mejor solucion encontrada
        matriz_feromonas = actualizar_feromonas_pacientes(matriz_feromonas, soluciones[indice_mejor_hormiga], calidad_soluciones[indice_mejor_hormiga],ro)

    # Devuelve el mejor camino y su costo después de todas las iteraciones
    #mejor_solucion_global = mejor_solucion[mejor_solucion_calidad.index(max(mejor_solucion_calidad))]
    mejor_solucion_global = mejor_solucion[mejor_solucion_FO.index(min(mejor_solucion_FO))]
    mejor_FO = min(mejor_solucion_FO)
    return mejor_solucion_global , df, mejor_FO , df_datos_unido