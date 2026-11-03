# Scripts Históricos / Legacy (Archivo del Prototipo)

Este directorio contiene scripts de desarrollo preliminar y exploraciones metodológicas de etapas tempranas del proyecto que **no forman parte del benchmark científico final** reportado en el manuscrito para *Acta Montanistica Slovaca* (2026):

1. **Modelado HMM de Trayectorias Temporales (`train_hmm_baumwelch.py`, `evaluate_hmm_k_selection.py`, etc.):** Exploraciones preliminares de agrupamiento secuencial. Descartadas del manuscrito formal, el cual establece explícitamente que el dataset público consiste en observaciones independientes y no en trayectorias continuas correlacionadas.
2. **Entrenamientos Previos (`train_model.py`, `train_all_models.py`, `train_cv.py`):** Pipelines preliminares de agosto/septiembre superados por el protocolo simétrico riguroso (`fair_eval.py` y `run_multiseed_evaluation.py`).
3. **Generadores Preliminares (`generate_synthetic_data.py`):** Predecesor del generador oficial publicado (`download_and_process_public_dataset.py`).
4. **Pruebas de Hipótesis Previas (`statistical_tests.py`):** Versión previa consolidada en `fair_eval.py` con remuestreo bootstrap pareado ($B=1\,000$) y prueba exacta de McNemar con corrección Holm.

> Para reproducir los resultados publicados en el artículo, utilice exclusivamente los scripts ubicados en la raíz de `backend/scripts/`.
