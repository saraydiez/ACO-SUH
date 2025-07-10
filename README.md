
# 🏥 Optimización del Flujo de Pacientes en Urgencias mediante Algoritmos de Colonia de Hormigas (ACO)

**Trabajo Fin de Máster – Máster en Ingeniería Industrial**  
**Autora**: Saray Díez Soler  
**Universidad de Sevilla** – ETSI – Dpto. Organización Industrial y Gestión de Empresas I  
**Año**: 2024

---

## 📘 Descripción del Proyecto

Este trabajo aborda la **optimización del flujo de pacientes en un Servicio de Urgencias Hospitalario (SUH)** mediante técnicas de investigación operativa y algoritmos bioinspirados.

El problema se modela como una **secuenciación de actividades bajo restricciones de recursos y prioridades clínicas**, donde se busca minimizar:

- El tiempo total de estancia en urgencias (**LOS**)
- El cumplimiento del tiempo óptimo de primera atención médica (**TEPCOF**)

Para resolver este problema complejo (NP-hard), se ha desarrollado desde cero una **metaheurística basada en Ant Colony Optimization (ACO)**, implementada en Python, y adaptada específicamente a las características de los SUHs.

---

## 🎯 Objetivos Específicos

- Modelar el flujo de pacientes según niveles de urgencia ESI y procesos clínicos (PU)
- Diseñar una heurística constructiva para generar soluciones iniciales válidas
- Implementar varias variantes del algoritmo ACO:
  - ACO por actividades (3 versiones)
  - ACO por pacientes (1 versión)
- Incorporar y comparar resultados **con y sin búsqueda local**
- Evaluar los resultados bajo distintos niveles de saturación y turnos (12h y 6h)

---

## 🗂️ Estructura del Proyecto

```
TFM/
├── main.py                  # Script principal de ejecución del modelo
├── config.py                # Parámetros generales del experimento
├── constantes.py            # Definición de estructuras del SUH y procesos
├── requirements.txt         # Librerías necesarias
│
└── src/                                   # Código modular
    ├── generador.py                       # Generación de pacientes, prioridades y datos
    ├── acciones.py                        # Funciones de cálculo de FO, saturación, etc.
    ├── metaheuristicas.py                 # Implementación de ACO sin búsquedA LOCAL
    ├── metaheuristicas_busquedalocal.py   # Implementación de ACO con búsquedA LOCAL
    ├── visualizaciones.py                 # Grafico de Gantt
    └── __init__.py
```

---

## ⚙️ Ejecución del Proyecto

1. Instala las dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecuta el script principal:

```bash
python main.py
```

3. El sistema generará:
   - Una instancia aleatoria de pacientes y recursos
   - Una solución inicial factible
   - Una solución optimizada con ACO
   - Un Gantt con la programación de actividades o pacientes
---

## 📌 Parámetros configurables (`config.py`)

- `nivel_saturacion`: porcentaje de ocupación (50, 75, 100)
- `q0`, `alpha`, `beta`, `evaporacion`: parámetros del ACO
- `num_hormigas`: numero de hormigas que se generan en cada iteración
- `modo_bl`: activar búsqueda local
- `aco_version`: elegir entre ACO1, ACO2, ACO3 o ACO4

---


## 💡 Contribuciones del Proyecto

- Aplicación original del algoritmo **ACO en problemas de programación hospitalaria**
- Representaciones alternativas (por pacientes vs. por actividades)
- Comparación rigurosa con y sin búsqueda local
- Generación automática de escenarios realistas
- Visualización clara e interpretable de resultados

---

## 🛠️ Requisitos Técnicos

- Python 3.10+
- Librerías:
  - `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`

Instalación rápida:

```bash
pip install -r requirements.txt
```

---

## 📜 Licencia

Este proyecto se ha desarrollado en el contexto académico del Máster en Ingeniería Industrial de la Universidad de Sevilla.  
Queda restringido a uso educativo e investigativo. Para otros usos, contactar con la autora.
