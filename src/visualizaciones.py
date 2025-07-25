# -*- coding: utf-8 -*-
"""visualizaciones.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12ZPCYnh4Bcqh5st5k_5yVAtyUgFul-1M
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

def representa_GANTT(df_datos_unido):
  df_expanded = df_datos_unido.explode('Recurso_asignado')
  # Obtener la fecha actual
  fecha_actual = datetime.now()

  # Convertir los tiempos de inicio y fin en formato datetime para Plotly
  df_expanded['Inicio'] =  fecha_actual + pd.to_timedelta(df_expanded['Tiempo_inicio'], unit='m')
  df_expanded['Fin'] =  fecha_actual + pd.to_timedelta(df_expanded['Tiempo_FIN'], unit='m')


  # Generar colores aleatorios para los pacientes
  unique_patients = df_expanded['Paciente'].unique()
  colors = {patient: f'#{random.randint(0, 0xFFFFFF):06x}' for patient in unique_patients}

  # Crear una nueva columna 'Leyenda' para el color de la leyenda
  df_expanded['Leyenda'] = df_expanded['Paciente'].apply(lambda x: f'Paciente {x}')


  # Generar el diagrama de Gantt
  fig = px.timeline(df_expanded, x_start='Inicio', x_end='Fin', y='Recurso_asignado', text='Actividad', color='Leyenda', color_discrete_map={f'Paciente {k}': v for k, v in colors.items()},
                    title='Diagrama de Gantt')

  # Actualizar el layout para mostrar el eje X con la fecha y hora
  #fig.update_layout(xaxis=dict(tickformat='%Y-%m-%d %H:%M'))

  # Mostrar el diagrama
  fig.show()
  return