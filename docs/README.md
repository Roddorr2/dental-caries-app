# Índice General de Documentación Técnica y Clínica (CDSS)

**Sistema:** Sistema de Apoyo al Diagnóstico Odontológico para Detección de Caries en Fotografía Intraoral  
**Estándar Regulatorio:** SaMD (*Software as a Medical Device*) / IEC 62304 / ISO 13485  
**Versión:** 1.0.0  

---

## Estructura del Repositorio de Documentación

| Directorio | Documento | Contenido Principal |
| :--- | :--- | :--- |
| **[`00-methodology/`](./00-methodology/)** | [`methodology.md`](./00-methodology/methodology.md) | Marco híbrido Scrum + CRISP-DM (Dual-Track), Milestones M1-M5 y roles. |
| | [`dor.md`](./00-methodology/dor.md) | **Definition of Ready:** Criterios para que una tarea ingrese al Sprint. |
| | [`dod.md`](./00-methodology/dod.md) | **Definition of Done:** Pirámide de calidad de 4 niveles para producción. |
| | [`acceptance-criteria.md`](./00-methodology/acceptance-criteria.md) | Estándar BDD/Gherkin y 5 invariantes clínicas/técnicas no negociables. |
| **[`01-requirements/`](./01-requirements/)** | [`user-stories.md`](./01-requirements/user-stories.md) | Historias de usuario clínicas (US-01 a US-06) con escenarios Gherkin. |
| **[`02-architecture/`](./02-architecture/)** | [`architecture.md`](./02-architecture/architecture.md) | Arquitectura Hexagonal / Limpia, Bounded Contexts DDD y CQRS. |
| **[`03-api/`](./03-api/)** | [`openapi.yaml`](./03-api/openapi.yaml) | Especificación OpenAPI 3.1.0 de endpoints REST y contratos de datos. |
| **[`04-testing/`](./04-testing/)** | [`test-cases.md`](./04-testing/test-cases.md) | Matriz integral de casos de prueba (ISO 29119, Pytest, Playwright, a11y). |
| **[`05-devops/`](./05-devops/)** | [`pipeline-github-actions.md`](./05-devops/pipeline-github-actions.md) | Pipeline CI/CD de GitHub Actions, Docker containers, secretos y despliegue. |

