# Especificación de Requerimientos Funcionales (RF)

**Sistema:** Sistema de Apoyo al Diagnóstico Odontológico para Detección de Caries en Fotografía Intraoral (CDSS)  
**Módulo:** Backend Core (FastAPI / DDD / CQRS) & Inferencia Machine Learning  
**Versión:** 1.0.0  
**Fecha:** 2026-09-29  

---

## 1. Introducción y Contexto del Dominio
El presente documento describe los requerimientos funcionales del sistema de apoyo al diagnóstico odontológico (*Clinical Decision Support System* - CDSS), enfocado en la detección automatizada de caries coronal mediante fotografías intraorales directas de luz visible. Los requerimientos aseguran la trazabilidad clínica, la integridad de los datos de salud y el cumplimiento del flujo de trabajo odontológico profesional.

---

## 2. Matriz de Requerimientos Funcionales

| ID | Nombre del Requerimiento | Prioridad (MoSCoW) | Capa Arquitectónica |
| :--- | :--- | :--- | :--- |
| **RF-01** | Ingesta y Validación de Fotografías Intraorales | Must Have | API / Application / Domain |
| **RF-02** | Deduplicación e Integridad mediante Hash Criptográfico SHA-256 | Must Have | Domain / Infrastructure |
| **RF-03** | Orquestación Asíncrona de Inferencia con Redes Neuronales YOLOv8 | Must Have | Application / Infrastructure / ML |
| **RF-04** | Detección Multiclase y Mapeo Anatómico de Hallazgos Clínicos | Must Have | Domain / ML Adapter |
| **RF-05** | Gestión del Ciclo de Vida del Diagnóstico Asistido | Must Have | Domain (Aggregate Root) |
| **RF-06** | Validación, Rechazo y Firma Odontológica Colegiada | Must Have | Domain / Application |
| **RF-07** | Pista de Auditoría Clínica Inmutable (*Append-Only*) | Must Have | Infrastructure / Database |
| **RF-08** | Registro de Modelos de IA y Trazabilidad Algorítmica | Should Have | Domain / Application |

---

## 3. Especificación Detallada de Requerimientos

### RF-01: Ingesta y Validación de Fotografías Intraorales
* **Descripción:** El sistema debe permitir la carga e ingesta de imágenes intraorales asociadas a un estudio clínico de un paciente registrado.
* **Entradas:** Archivo binario de imagen, identificador del estudio (`estudio_id`), tipo de vista (`tipo_vista_enum`: `OCLUSAL_MANDIBULAR`, `OCLUSAL_MAXILAR`, `FRONTAL_VESTIBULAR`, `LATERAL_DERECHA`, `LATERAL_IZQUIERDA`).
* **Reglas de Negocio:**
  - El sistema **solo aceptará** formatos de imagen fotográfica digital en luz visible: `JPG`, `JPEG` o `PNG`.
  - El sistema **rechazará estrictamente** formatos radiológicos o médicos complejos como `DICOM` (`.dcm`), devolviendo error `422 Unprocessable Entity`.
  - Las dimensiones mínimas aceptadas son de $640 \times 640$ píxeles.
* **Salida:** Registro de la entidad `ImagenIntraoral` con identificador único UUID, persistida en disco y base de datos con estado de procesamiento `PENDIENTE`.

### RF-02: Deduplicación e Integridad mediante Hash Criptográfico SHA-256
* **Descripción:** El sistema debe garantizar que ninguna imagen duplicada ingrese al historial clínico ni sature los recursos de almacenamiento e inferencia.
* **Proceso:**
  - Al recibir los bytes de la imagen, el sistema calculará de forma determinista el hash digest mediante el algoritmo SHA-256:
    $$\text{Hash} = \text{SHA-256}(\text{bytes})$$
  - Se consulta la tabla `imagenes_intraorales` buscando coincidencias con `hash_sha256`.
* **Reglas de Negocio:**
  - Si el hash ya existe en la base de datos, el sistema abortará la operación y retornará un código `409 Conflict`, evitando la redundancia de almacenamiento y asegurando la integridad pericial del registro médico.

### RF-03: Orquestación Asíncrona de Inferencia con Redes Neuronales YOLOv8
* **Descripción:** El análisis visual con inteligencia artificial debe ejecutarse de forma no bloqueante mediante un worker de fondo (*BackgroundTasks* / Celery).
* **Flujo Operativo:**
  1. El cliente invoca `POST /api/v1/diagnosticos/analizar`.
  2. El sistema crea una entidad `InferenciaIA` en estado `PENDIENTE` y asocia el `modelo_ml_id` en producción.
  3. El endpoint responde de inmediato con código `202 Accepted` retornando el `inferencia_id` y `estudio_id`.
  4. El worker asíncrono toma la tarea, actualiza el estado a `EN_PROCESO`, pasa la ruta física de la imagen al adaptador `YOLOv8Detector` y cronometra el tiempo exacto en milisegundos (`tiempo_ms`).
  5. Al finalizar con éxito, el estado se actualiza a `COMPLETADO`. Si ocurre una excepción de memoria o formato corrupto, transiciona a `FALLIDO` y almacena el stack trace en `error_mensaje`.

### RF-04: Detección Multiclase y Mapeo Anatómico de Hallazgos Clínicos
* **Descripción:** El modelo de IA debe discriminar entre lesiones de dentición permanente y decidua, traduciendo las salidas probabilísticas al modelo de dominio clínico.
* **Reglas de Negocio:**
  - **Clase 0 (`caries_permanente`):** Piezas de dentición definitiva (índice CPO-D).
  - **Clase 1 (`caries_decidua`):** Piezas de dentición primaria (índice ceo-d).
  - Cada detección sobre el umbral de confianza calibrado ($\tau^*$) genera una entidad de dominio `Hallazgo`:
    - Coordenadas de la caja delimitadora normalizadas relativas a la imagen: $x_1, y_1, \text{width}, \text{height} \in [0.0, 1.0]$.
    - Severidad clínica estimada:
      - Confianza $\ge 0.80 \implies \text{SEVERA}$
      - Confianza entre $0.55$ y $0.79 \implies \text{MODERADA}$
      - Confianza $< 0.55 \implies \text{LEVE}$
    - Cuadrante y número de diente (notación FDI internacional 11-48 para permanentes, 51-85 para deciduos) cuando sea identificable.

### RF-05: Gestión del Ciclo de Vida del Diagnóstico Asistido
* **Descripción:** Todo diagnóstico generado por el sistema es preliminar y debe ser gestionado bajo una máquina de estados finita.
* **Diagrama de Transición de Estados:**
  ```text
  [Inferencia Completada] ──> SUGERIDO_IA ──> EN_REVISION ──┬──> VALIDADO (Aprobado)
                                                            └──> RECHAZADO (Descartado)
  ```
* **Reglas de Negocio:**
  - Un diagnóstico en estado `SUGERIDO_IA` no tiene validez legal ni terapéutica; sirve exclusivamente como sugerencia visual en pantalla.
  - La transición a `VALIDADO` o `RECHAZADO` es irreversible una vez firmada.

### RF-06: Validación, Rechazo y Firma Odontológica Colegiada
* **Descripción:** El odontólogo tratante debe tener el control final sobre las predicciones de la IA antes de que formen parte de la ficha clínica del paciente.
* **Reglas de Negocio:**
  - Para validar o rechazar un diagnóstico, el odontólogo debe estar registrado en la tabla `odontologos` con estado `autorizado_validar = True` y número de colegiatura profesional vigente.
  - **Aprobación:** Permite incorporar observaciones clínicas adicionales (`notas_validacion`) y registra `fecha_validacion` en UTC.
  - **Rechazo:** Exige obligatoriamente la justificación del descarte (`motivo_rechazo`), indicando si se debió a falso positivo, mala iluminación, artefacto de imagen o discrepancia diagnóstica.

### RF-07: Pista de Auditoría Clínica Inmutable (*Append-Only*)
* **Descripción:** Cada cambio de estado en los diagnósticos y estudios debe registrarse en tablas de auditoría dedicadas para garantizar la trazabilidad forense exigida en salud.
* **Reglas de Negocio:**
  - Las tablas `auditoria_diagnosticos` y `auditoria_estudios` operan bajo el patrón estricto de **solo inserción (*append-only*)**.
  - Quedan terminantemente prohibidas las operaciones de `UPDATE` o `DELETE` sobre estas tablas a nivel de base de datos.
  - Cada entrada guarda: `id`, `diagnostico_id`, `odontologo_id`, `estado_anterior`, `estado_nuevo`, `notas` y `created_at` (timestamp con zona horaria).

### RF-08: Registro de Modelos de IA y Trazabilidad Algorítmica
* **Descripción:** El sistema debe registrar en el catálogo `modelos_ml` cada iteración o versión de los pesos neuronales utilizados en producción.
* **Reglas de Negocio:**
  - Todo diagnóstico persistido debe referenciar mediante clave foránea obligatoria (`modelo_ml_id`) el modelo exacto que generó los hallazgos.
  - Se deben persistir las métricas de validación del modelo: $F1\text{-Score}$, $Precision$, $Recall$, versión de arquitectura (ej. `YOLOv8n`) y estado `aprobado_produccion = True`.
  - El sistema no permitirá realizar inferencias con modelos cuyo flag `aprobado_produccion` esté en `False`.
