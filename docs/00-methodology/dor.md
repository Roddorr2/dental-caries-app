# Definition of Ready (DoR) — Criterios de Preparación

**Sistema:** Sistema de Apoyo al Diagnóstico Odontológico (CDSS)  
**Versión:** 1.0.0  
**Objetivo:** Garantizar que ninguna tarea o Historia de Usuario ingrese al Sprint Backlog sin la información y precondiciones necesarias, previniendo ambigüedades y alucinaciones en el desarrollo humano o asistido por IA.

---

## 1. DoR General (Historias de Software / Plataforma)

Toda Historia de Usuario o tarea de ingeniería de software debe cumplir con la siguiente lista de verificación antes de ser estimada o iniciada:

- [ ] **Título y Formato Estándar:** Redactada en formato estándar (*"Como [rol clínico/técnico], quiero [acción], para [beneficio]"*).
- [ ] **Criterios de Aceptación (AC) en Gherkin:** Mínimo 2 escenarios definidos con sintaxis `Dado que / Cuando / Entonces / Y` (ver [`acceptance-criteria.md`](./acceptance-criteria.md)).
- [ ] **Bounded Context Identificado:** Se especifica el contexto delimitado afectado (`Pacientes`, `Estudios`, `Diagnosticos` o `Modelos`).
- [ ] **Contratos de Entrada y Salida (API / DTO):** Esquemas Pydantic / OpenAPI documentados con tipos y validaciones de campo.
- [ ] **Dependencias Técnicas Resueltas:** Modelos ORM, migraciones de base de datos o librerías externas ya disponibles en el entorno.
- [ ] **Sin Bloqueos Arquitectónicos:** Cumple con la Arquitectura Hexagonal (el dominio no importa infraestructura ni frameworks).

---

## 2. DoR Específica: Tareas de Machine Learning / Inferencia

Aplica a cualquier tarea que involucre ingestión, entrenamiento, calibración o integración de modelos de IA:

- [ ] **Dataset Etiquetado y Congelado:**
  - Imágenes etiquetadas en formato compatible (ej. YOLO `[clase, x_center, y_center, width, height]`).
  - Separación estricta de particiones (*Train / Val / Test*) **por paciente**, garantizando cero fuga de datos (*patient data leakage*).
- [ ] **Métricas Clínicas de Aceptación Predefinidas:**
  - Umbral mínimo obligatorio: $F1\text{-Score} \ge 0.85$.
  - Umbral de confianza operativo calibrado ($\tau^*$) para el compromiso sensibilidad vs. especificidad.
- [ ] **Firma de Puerto de Dominio:** El modelo a integrar debe implementar la interfaz `IDetectorPatologias` definida en el dominio:
  ```python
  def detectar(self, imagen_bytes: bytes) -> list[HallazgoDetectado]: ...
  ```
- [ ] **Restricciones de Hardware y Desempeño:**
  - Presupuesto de tiempo de inferencia definido: $\le 300\text{ ms}$ (GPU) o $\le 1500\text{ ms}$ (CPU).
  - Formato del artefacto especificado (`.pt` PyTorch u `.onnx`).

---

## 3. DoR Específica: Flujo Clínico & Experiencia de Usuario (UI/UX)

Aplica a vistas, componentes y flujos interactivos de la estación clínica:

- [ ] **Mental Model Clínico Validado:**
  - La interfaz oculta la complejidad algorítmica al odontólogo (prohibido exponer selectores de modelos experimentales en el flujo de consulta).
  - Terminología médica y taxonómica normalizada (Nomenclatura FDI, OMS CPO-D/ceo-d).
- [ ] **Diseño Responsivo Definido:**
  - Especificación clara para escritorio ($\ge 1024\text{ px}$) y dispositivo móvil/tablet de sillón dental ($360\text{ px} - 390\text{ px}$).
- [ ] **Accesibilidad (a11y):**
  - Contraste visual definido conforme a WCAG 2.1 Nivel AA ($\ge 4.5:1$).
  - Mapeo de estados clínicos claros (Pendiente, En Análisis, Completado, Error).
- [ ] **Tratamiento de Estados Asíncronos:** Diseñados los estados de carga (*skeletons/loaders*), estados vacíos (*empty states*) y manejo de errores clínicos amigables.

---

## 4. Antipatrones de Entrada (Lo que RECHAZA la DoR)

> [!CAUTION]
> Una tarea es **inmediatamente devuelta al backlog** si presenta:
> 1. Criterios de aceptación vagos como *"El modelo debe funcionar bien"* o *"La pantalla debe verse intuitiva"*.
> 2. Requerimientos de UI que pidan al clínico elegir qué red neuronal utilizar para el paciente.
> 3. Tareas que requieran modificar entidades de dominio para resolver requerimientos de librerías externas o bases de datos.

