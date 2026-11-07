"""
seed.py
=======
Script de Seeding de Datos Clínicos para Desarrollo Local.

Características:
- 100% Idempotente: puede ejecutarse infinitas veces sin duplicar registros ni violar PK/Unique constraints.
- Identificadores Deterministas: genera UUIDs basados en namespaces para trazabilidad estable.
- Soporte para flag --reset: limpia datos previos de prueba y vuelve a poblar.
- Datos Clínicos Realistas y Completos:
  * Odontólogos Colegiados (COP) autorizados y residentes
  * Modelos de Inteligencia Artificial (YOLOv8, SVM, Random Forest, MobileNet)
  * Pacientes con DNIs peruanos válidos de 8 dígitos y datos demográficos reales
  * Estudios imagenológicos con diferentes tipos de examen (Oclusal, Serie Completa, Frontal)
  * Imágenes intraorales con fotos clínicas macro de alta definición y hashes SHA-256
  * Inferencias técnicas registradas con GPUs y tiempos de procesamiento
  * Diagnósticos con estados clínicos reales: SUGERIDO_IA (cola de revisión), VALIDADO (firmado por odontólogo) y RECHAZADO (falsos positivos documentados)
  * Hallazgos con notación dental internacional FDI, severidades y Bounding Boxes calibrados
  * Modelos de Lectura CQRS sincronizados: rm_cola_revision, rm_estadisticas_modelo, rm_historial_paciente
  * Trazabilidad completa con registros de auditoría (auditoria_diagnosticos y auditoria_estudios)

Uso:
    python scripts/seed.py          # Idempotente (inserta o actualiza)
    python scripts/seed.py --reset  # Limpia datos previos y siembra de cero
"""

import argparse
import logging
import sys
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

# Asegurar import de la app backend
sys.path.insert(0, ".")

from app.infrastructure.database.connection import SessionLocal
import app.infrastructure.database.models as models
from app.infrastructure.database.models import (
    AuditoriaDiagnosticoORM,
    AuditoriaEstudioORM,
    DiagnosticoORM,
    EstudioORM,
    HallazgoORM,
    ImagenIntraoralORM,
    InferenciaIAORM,
    ModeloMLORM,
    OdontologoORM,
    PacienteORM,
    RMColaRevisionORM,
    RMEstadisticasModeloORM,
    RMHistorialPacienteORM,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("dental_seeder")

# Namespace determinista para generar UUIDs consistentes
SEED_NAMESPACE = uuid.UUID("3f82a174-8b65-4f32-9cb1-e87f5492bc30")

def gen_uuid(category: str, key: str) -> uuid.UUID:
    """Genera un UUID v5 determinista basado en categoría y clave única."""
    return uuid.uuid5(SEED_NAMESPACE, f"{category}:{key}")

NOW = datetime.now(timezone.utc)

def limpiar_base_de_datos(db: Session) -> None:
    """Elimina datos de prueba en orden topológico seguro de claves foráneas."""
    logger.info("Limpiando datos existentes en tablas clínicas y read models...")
    tablas = [
        "auditoria_diagnosticos",
        "auditoria_estudios",
        "rm_cola_revision",
        "rm_estadisticas_modelo",
        "rm_historial_paciente",
        "hallazgos",
        "diagnosticos",
        "inferencias_ia",
        "imagenes_intraorales",
        "estudios_imagenologicos",
        "modelos_ml",
        "odontologos",
        "pacientes",
    ]
    for tabla in tablas:
        db.execute(text(f"TRUNCATE TABLE {tabla} CASCADE;"))
    db.commit()
    logger.info("Base de datos limpia y lista para sembrado.")


def seed_odontologos(db: Session) -> dict[str, models.OdontologoORM]:
    """Siembra odontólogos colegiados."""
    logger.info("Sembrando Odontólogos Colegiados...")
    odontologos_data = [
        {
            "key": "mendoza",
            "colegiatura": "48291",
            "nombres": "Carlos Enrique",
            "apellidos": "Mendoza Alva",
            "autorizado": True,
        },
        {
            "key": "vega",
            "colegiatura": "39182",
            "nombres": "Patricia Elena",
            "apellidos": "Vega Morales",
            "autorizado": True,
        },
        {
            "key": "salazar",
            "colegiatura": "51204",
            "nombres": "Andrés Fernando",
            "apellidos": "Salazar Benavides",
            "autorizado": True,
        },
        {
            "key": "ramos",
            "colegiatura": "62019",
            "nombres": "Lucía Beatriz",
            "apellidos": "Ramos Chávez",
            "autorizado": False,  # Odontóloga residente/pasante
        },
    ]

    result = {}
    for data in odontologos_data:
        oid = gen_uuid("odontologo", data["colegiatura"])
        obj = db.query(models.OdontologoORM).filter_by(id=oid).first()
        if not obj:
            obj = models.OdontologoORM(
                id=oid,
                nombres=data["nombres"],
                apellidos=data["apellidos"],
                numero_colegiatura=data["colegiatura"],
                autorizado_validar=data["autorizado"],
                created_at=NOW - timedelta(days=120),
            )
            db.add(obj)
        else:
            obj.nombres = data["nombres"]
            obj.apellidos = data["apellidos"]
            obj.numero_colegiatura = data["colegiatura"]
            obj.autorizado_validar = data["autorizado"]
        result[data["key"]] = obj

    db.commit()
    logger.info("  %d odontólogos listos.", len(result))
    return result


def seed_modelos_ml(db: Session) -> dict[str, models.ModeloMLORM]:
    """Siembra modelos de Deep Learning y Machine Learning."""
    logger.info("Sembrando Modelos ML/DL...")
    modelos_data = [
        {
            "key": "yolo_v8n",
            "nombre": "YOLOv8n-DentalCaries",
            "version": "1.2.0",
            "tipo": "YOLO",
            "f1_score": 0.924,
            "precision_score": 0.941,
            "recall_score": 0.908,
            "ruta_archivo": "models/production/yolov8n_dental_caries_v1.2.0.pt",
            "aprobado_produccion": True,
            "created_at": NOW - timedelta(days=90),
        },
        {
            "key": "yolo_v8s",
            "nombre": "YOLOv8s-DentalCaries-HiRes",
            "version": "2.0.1",
            "tipo": "YOLO",
            "f1_score": 0.948,
            "precision_score": 0.957,
            "recall_score": 0.939,
            "ruta_archivo": "models/staging/yolov8s_dental_caries_v2.0.1.pt",
            "aprobado_produccion": False,
            "created_at": NOW - timedelta(days=20),
        },
        {
            "key": "svm_hog",
            "nombre": "SVM-DentalClassifier-HOG",
            "version": "0.9.4",
            "tipo": "SVM",
            "f1_score": 0.812,
            "precision_score": 0.835,
            "recall_score": 0.791,
            "ruta_archivo": "models/baseline/svm_hog_texture_v0.9.4.joblib",
            "aprobado_produccion": False,
            "created_at": NOW - timedelta(days=150),
        },
        {
            "key": "rf_texture",
            "nombre": "RandomForest-Dental-Texture",
            "version": "1.0.0",
            "tipo": "RANDOM_FOREST",
            "f1_score": 0.837,
            "precision_score": 0.849,
            "recall_score": 0.826,
            "ruta_archivo": "models/baseline/rf_lbp_texture_v1.0.0.joblib",
            "aprobado_produccion": False,
            "created_at": NOW - timedelta(days=140),
        },
        {
            "key": "mobilenet_v3",
            "nombre": "MobileNetV3-Intraoral-Screening",
            "version": "1.1.0",
            "tipo": "MOBILENET",
            "f1_score": 0.865,
            "precision_score": 0.880,
            "recall_score": 0.851,
            "ruta_archivo": "models/mobile/mobilenetv3_intraoral_v1.1.0.onnx",
            "aprobado_produccion": False,
            "created_at": NOW - timedelta(days=60),
        },
    ]

    result = {}
    for data in modelos_data:
        mid = gen_uuid("modelo", f"{data['nombre']}:{data['version']}")
        obj = db.query(models.ModeloMLORM).filter_by(id=mid).first()
        if not obj:
            obj = models.ModeloMLORM(
                id=mid,
                nombre=data["nombre"],
                version=data["version"],
                tipo=data["tipo"],
                f1_score=data["f1_score"],
                precision_score=data["precision_score"],
                recall_score=data["recall_score"],
                ruta_archivo=data["ruta_archivo"],
                aprobado_produccion=data["aprobado_produccion"],
                created_at=data["created_at"],
            )
            db.add(obj)
        else:
            obj.f1_score = data["f1_score"]
            obj.precision_score = data["precision_score"]
            obj.recall_score = data["recall_score"]
            obj.aprobado_produccion = data["aprobado_produccion"]
        result[data["key"]] = obj

    db.commit()
    logger.info("  %d modelos ML listos.", len(result))
    return result


def seed_pacientes(db: Session) -> dict[str, models.PacienteORM]:
    """Siembra pacientes peruanos con datos realistas."""
    logger.info("Sembrando Pacientes...")
    pacientes_data = [
        {
            "key": "mariana",
            "dni": "45892134",
            "nombres": "Mariana",
            "apellidos": "Paredes Castro",
            "fecha_nacimiento": datetime(1998, 7, 22, tzinfo=timezone.utc),
            "sexo": "FEMENINO",
            "telefono": "971234567",
            "email": "mparedes.castro@outlook.com",
            "estado": "ACTIVO",
        },
        {
            "key": "diego",
            "dni": "76543210",
            "nombres": "Diego Alonso",
            "apellidos": "Morales Vega",
            "fecha_nacimiento": datetime(2005, 8, 18, tzinfo=timezone.utc),
            "sexo": "MASCULINO",
            "telefono": "947192834",
            "email": "diego.morales@unmsm.edu.pe",
            "estado": "ACTIVO",
        },
        {
            "key": "roberto",
            "dni": "10293847",
            "nombres": "Roberto Carlos",
            "apellidos": "Gómez Farfán",
            "fecha_nacimiento": datetime(1981, 11, 9, tzinfo=timezone.utc),
            "sexo": "MASCULINO",
            "telefono": "993847561",
            "email": "roberto.gomez@clinica.pe",
            "estado": "ACTIVO",
        },
        {
            "key": "guillermo",
            "dni": "75415745",
            "nombres": "Guillermo",
            "apellidos": "Sánchez Ruiz",
            "fecha_nacimiento": datetime(1994, 3, 15, tzinfo=timezone.utc),
            "sexo": "MASCULINO",
            "telefono": "984512340",
            "email": "guillermo.sanchez@gmail.com",
            "estado": "ACTIVO",
        },
        {
            "key": "elena",
            "dni": "08927163",
            "nombres": "Elena Beatriz",
            "apellidos": "Torres Silva",
            "fecha_nacimiento": datetime(1968, 1, 25, tzinfo=timezone.utc),
            "sexo": "FEMENINO",
            "telefono": "981273645",
            "email": "elena.torres@empresa.com",
            "estado": "ACTIVO",
        },
        {
            "key": "valeria",
            "dni": "72109845",
            "nombres": "Valeria Sofía",
            "apellidos": "Espinoza Vidal",
            "fecha_nacimiento": datetime(2002, 5, 30, tzinfo=timezone.utc),
            "sexo": "FEMENINO",
            "telefono": "954128930",
            "email": "valeria.espinoza@pucp.edu.pe",
            "estado": "ACTIVO",
        },
        {
            "key": "carmen",
            "dni": "29485716",
            "nombres": "Carmen Rosa",
            "apellidos": "Delgado Nuñez",
            "fecha_nacimiento": datetime(1962, 12, 4, tzinfo=timezone.utc),
            "sexo": "FEMENINO",
            "telefono": "918273645",
            "email": "carmen.delgado@yahoo.es",
            "estado": "ACTIVO",
        },
        {
            "key": "jorge",
            "dni": "41928374",
            "nombres": "Jorge Luis",
            "apellidos": "Huamán Quispe",
            "fecha_nacimiento": datetime(1985, 9, 14, tzinfo=timezone.utc),
            "sexo": "MASCULINO",
            "telefono": "962384719",
            "email": "jhuaman.q@gmail.com",
            "estado": "ACTIVO",
        },
    ]

    result = {}
    for data in pacientes_data:
        pid = gen_uuid("paciente", data["dni"])
        obj = db.query(models.PacienteORM).filter_by(id=pid).first()
        if not obj:
            obj = models.PacienteORM(
                id=pid,
                dni=data["dni"],
                nombres=data["nombres"],
                apellidos=data["apellidos"],
                fecha_nacimiento=data["fecha_nacimiento"],
                sexo=data["sexo"],
                telefono=data["telefono"],
                email=data["email"],
                estado=data["estado"],
                created_at=NOW - timedelta(days=60),
                updated_at=NOW - timedelta(days=1),
            )
            db.add(obj)
        else:
            obj.nombres = data["nombres"]
            obj.apellidos = data["apellidos"]
            obj.fecha_nacimiento = data["fecha_nacimiento"]
            obj.sexo = data["sexo"]
            obj.telefono = data["telefono"]
            obj.email = data["email"]
            obj.estado = data["estado"]
        result[data["key"]] = obj

    db.commit()
    logger.info("  %d pacientes listos.", len(result))
    return result


def seed_estudios_e_imagenes(
    db: Session, pacientes: dict[str, models.PacienteORM]
) -> tuple[dict[str, models.EstudioORM], dict[str, models.ImagenIntraoralORM]]:
    """Siembra estudios imagenológicos e imágenes intraorales con fotos reales."""
    logger.info("Sembrando Estudios e Imágenes Intraorales...")

    # Mapeo de casos clínicos
    estudios_specs = [
        {
            "key": "estudio_mariana",
            "paciente_key": "mariana",
            "tipo_examen": "OCLUSAL_MANDIBULAR",
            "estado": "PROCESADO",
            "img_vista": "OCLUSAL_MANDIBULAR",
            "img_formato": "JPG",
            "img_ruta": "/samples/sample_case_1.jpg",
            "img_hash": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
            "nitidez": 0.94,
            "iluminacion": 0.88,
        },
        {
            "key": "estudio_diego",
            "paciente_key": "diego",
            "tipo_examen": "OCLUSAL_MAXILAR",
            "estado": "PROCESADO",
            "img_vista": "OCLUSAL_MAXILAR",
            "img_formato": "JPG",
            "img_ruta": "/samples/sample_case_2.jpg",
            "img_hash": "b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef010",
            "nitidez": 0.92,
            "iluminacion": 0.91,
        },
        {
            "key": "estudio_roberto",
            "paciente_key": "roberto",
            "tipo_examen": "OCLUSAL_MAXILAR",
            "estado": "PROCESADO",
            "img_vista": "OCLUSAL_MAXILAR",
            "img_formato": "JPG",
            "img_ruta": "/samples/sample_case_2.jpg",
            "img_hash": "c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef01200",
            "nitidez": 0.89,
            "iluminacion": 0.84,
        },
        {
            "key": "estudio_guillermo",
            "paciente_key": "guillermo",
            "tipo_examen": "OCLUSAL_MANDIBULAR",
            "estado": "PROCESADO",
            "img_vista": "OCLUSAL_MANDIBULAR",
            "img_formato": "JPG",
            "img_ruta": "/samples/sample_case_1.jpg",
            "img_hash": "d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0123000",
            "nitidez": 0.95,
            "iluminacion": 0.92,
        },
        {
            "key": "estudio_elena",
            "paciente_key": "elena",
            "tipo_examen": "SERIE_COMPLETA",
            "estado": "PROCESADO",
            "img_vista": "OCLUSAL_MAXILAR",
            "img_formato": "JPG",
            "img_ruta": "/samples/sample_case_2.jpg",
            "img_hash": "e5f67890123456789abcdef0123456789abcdef0123456789abcdef012340000",
            "nitidez": 0.91,
            "iluminacion": 0.87,
        },
        {
            "key": "estudio_valeria",
            "paciente_key": "valeria",
            "tipo_examen": "OCLUSAL_MANDIBULAR",
            "estado": "PROCESADO",
            "img_vista": "OCLUSAL_MANDIBULAR",
            "img_formato": "JPG",
            "img_ruta": "/samples/sample_case_1.jpg",
            "img_hash": "f67890123456789abcdef0123456789abcdef0123456789abcdef01234500000",
            "nitidez": 0.93,
            "iluminacion": 0.90,
        },
        {
            "key": "estudio_carmen",
            "paciente_key": "carmen",
            "tipo_examen": "FRONTAL_VESTIBULAR",
            "estado": "PROCESADO",
            "img_vista": "FRONTAL_VESTIBULAR",
            "img_formato": "JPG",
            "img_ruta": "/samples/sample_case_3.jpg",
            "img_hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "nitidez": 0.96,
            "iluminacion": 0.94,
        },
        {
            "key": "estudio_jorge",
            "paciente_key": "jorge",
            "tipo_examen": "LATERAL_DERECHA",
            "estado": "PENDIENTE",
            "img_vista": None,  # Aún sin imágenes cargadas
        },
    ]

    estudios_res = {}
    imagenes_res = {}

    for spec in estudios_specs:
        paciente = pacientes[spec["paciente_key"]]
        eid = gen_uuid("estudio", f"{paciente.dni}:{spec['tipo_examen']}")
        
        estudio_obj = db.query(models.EstudioORM).filter_by(id=eid).first()
        if not estudio_obj:
            estudio_obj = models.EstudioORM(
                id=eid,
                paciente_id=paciente.id,
                tipo_examen=spec["tipo_examen"],
                estado_procesamiento=spec["estado"],
                created_at=NOW - timedelta(days=14),
                updated_at=NOW - timedelta(days=2),
            )
            db.add(estudio_obj)
        else:
            estudio_obj.estado_procesamiento = spec["estado"]
        estudios_res[spec["key"]] = estudio_obj

        # Imagen asociada si aplica
        if spec.get("img_vista"):
            iid = gen_uuid("imagen", spec["img_hash"])
            img_obj = db.query(models.ImagenIntraoralORM).filter_by(id=iid).first()
            if not img_obj:
                img_obj = models.ImagenIntraoralORM(
                    id=iid,
                    estudio_id=eid,
                    tipo_vista=spec["img_vista"],
                    formato=spec["img_formato"],
                    ruta_almacenamiento=spec["img_ruta"],
                    hash_sha256=spec["img_hash"],
                    nitidez=spec["nitidez"],
                    iluminacion=spec["iluminacion"],
                    calidad_suficiente=True,
                    created_at=NOW - timedelta(days=14),
                )
                db.add(img_obj)
            else:
                img_obj.ruta_almacenamiento = spec["img_ruta"]
                img_obj.nitidez = spec["nitidez"]
                img_obj.iluminacion = spec["iluminacion"]
            imagenes_res[spec["key"]] = img_obj

    db.commit()
    logger.info("  %d estudios y %d imágenes listos.", len(estudios_res), len(imagenes_res))
    return estudios_res, imagenes_res


def seed_casos_clinicos(
    db: Session,
    pacientes: dict[str, models.PacienteORM],
    odontologos: dict[str, models.OdontologoORM],
    modelos: dict[str, models.ModeloMLORM],
    estudios: dict[str, models.EstudioORM],
    imagenes: dict[str, models.ImagenIntraoralORM],
) -> None:
    """
    Siembra el ciclo completo: Inferencia IA -> Diagnóstico -> Hallazgos FDI -> Auditoría -> CQRS Read Models.
    """
    logger.info("Sembrando Diagnósticos Clínicos, Hallazgos y Modelos CQRS...")
    modelo_prod = modelos["yolo_v8n"]

    casos = [
        # CASO 1: Pendiente en Cola de Revisión - Confianza ALTA (0.92)
        {
            "key": "caso_mariana",
            "paciente": pacientes["mariana"],
            "estudio": estudios["estudio_mariana"],
            "imagen": imagenes["estudio_mariana"],
            "estado": "SUGERIDO_IA",
            "confianza": 0.92,
            "categoria": "ALTA",
            "segunda_opinion": False,
            "odontologo": None,
            "notas": None,
            "motivo_rechazo": None,
            "fecha_gen": NOW - timedelta(hours=3),
            "fecha_val": None,
            "hallazgos": [
                {
                    "diente": 46,
                    "cuadrante": 4,
                    "patologia": "CARIES",
                    "severidad": "MODERADA",
                    "confianza": 0.94,
                    "bbox_x": 0.38,
                    "bbox_y": 0.34,
                    "bbox_w": 0.22,
                    "bbox_h": 0.28,
                    "desc": "Lesión cavitada oclusal con desmineralización activa en esmalte y dentina superficial.",
                },
                {
                    "diente": 45,
                    "cuadrante": 4,
                    "patologia": "CARIES",
                    "severidad": "LEVE",
                    "confianza": 0.89,
                    "bbox_x": 0.62,
                    "bbox_y": 0.30,
                    "bbox_w": 0.18,
                    "bbox_h": 0.22,
                    "desc": "Lesión cariosa incipiente en fosa oclusodistal sin cavitación franca.",
                },
            ],
        },
        # CASO 2: Pendiente en Cola de Revisión - Confianza MEDIA (0.82)
        {
            "key": "caso_diego",
            "paciente": pacientes["diego"],
            "estudio": estudios["estudio_diego"],
            "imagen": imagenes["estudio_diego"],
            "estado": "SUGERIDO_IA",
            "confianza": 0.82,
            "categoria": "MEDIA",
            "segunda_opinion": False,
            "odontologo": None,
            "notas": None,
            "motivo_rechazo": None,
            "fecha_gen": NOW - timedelta(hours=6),
            "fecha_val": None,
            "hallazgos": [
                {
                    "diente": 16,
                    "cuadrante": 1,
                    "patologia": "CARIES",
                    "severidad": "MODERADA",
                    "confianza": 0.82,
                    "bbox_x": 0.39,
                    "bbox_y": 0.32,
                    "bbox_w": 0.21,
                    "bbox_h": 0.25,
                    "desc": "Caries cavitada en fosa central oclusal de primer molar superior derecho.",
                },
            ],
        },
        # CASO 3: Pendiente en Cola de Revisión - Confianza BAJA / Requiere 2da Opinión (0.65)
        {
            "key": "caso_roberto",
            "paciente": pacientes["roberto"],
            "estudio": estudios["estudio_roberto"],
            "imagen": imagenes["estudio_roberto"],
            "estado": "SUGERIDO_IA",
            "confianza": 0.65,
            "categoria": "BAJA",
            "segunda_opinion": True,
            "odontologo": None,
            "notas": None,
            "motivo_rechazo": None,
            "fecha_gen": NOW - timedelta(hours=1),
            "fecha_val": None,
            "hallazgos": [
                {
                    "diente": 26,
                    "cuadrante": 2,
                    "patologia": "CARIES",
                    "severidad": "LEVE",
                    "confianza": 0.65,
                    "bbox_x": 0.44,
                    "bbox_y": 0.35,
                    "bbox_w": 0.19,
                    "bbox_h": 0.22,
                    "desc": "Sospecha de caries ocluso-palatina vs tinción amelodentinaria profunda. Requiere inspección táctil.",
                },
            ],
        },
        # CASO 4: Validado Clínicamente por Odontólogo Colegiado
        {
            "key": "caso_guillermo",
            "paciente": pacientes["guillermo"],
            "estudio": estudios["estudio_guillermo"],
            "imagen": imagenes["estudio_guillermo"],
            "estado": "VALIDADO",
            "confianza": 0.94,
            "categoria": "ALTA",
            "segunda_opinion": False,
            "odontologo": odontologos["mendoza"],
            "notas": "Diagnóstico confirmado. Se confirma lesión cariosa activa cavitada en pieza 46. Se programa restauración directa con resina fotopolimerizable técnica estratificada bajo aislamiento absoluto.",
            "motivo_rechazo": None,
            "fecha_gen": NOW - timedelta(days=2),
            "fecha_val": NOW - timedelta(days=2, hours=-1),
            "hallazgos": [
                {
                    "diente": 46,
                    "cuadrante": 4,
                    "patologia": "CARIES",
                    "severidad": "MODERADA",
                    "confianza": 0.94,
                    "bbox_x": 0.38,
                    "bbox_y": 0.34,
                    "bbox_w": 0.22,
                    "bbox_h": 0.28,
                    "desc": "Caries cavitada en esmalte y dentina superficial cara oclusal.",
                },
            ],
        },
        # CASO 5: Validado Clínicamente por Dra. Patricia Vega
        {
            "key": "caso_elena",
            "paciente": pacientes["elena"],
            "estudio": estudios["estudio_elena"],
            "imagen": imagenes["estudio_elena"],
            "estado": "VALIDADO",
            "confianza": 0.90,
            "categoria": "ALTA",
            "segunda_opinion": False,
            "odontologo": odontologos["vega"],
            "notas": "Validado en consulta. Caries severa pieza 16 con proximidad al cuerno pulpar mesial. Se solicitó radiografía periapical complementaria y prueba de vitalidad pulpar.",
            "motivo_rechazo": None,
            "fecha_gen": NOW - timedelta(days=5),
            "fecha_val": NOW - timedelta(days=5, hours=-2),
            "hallazgos": [
                {
                    "diente": 16,
                    "cuadrante": 1,
                    "patologia": "CARIES",
                    "severidad": "SEVERA",
                    "confianza": 0.91,
                    "bbox_x": 0.40,
                    "bbox_y": 0.32,
                    "bbox_w": 0.22,
                    "bbox_h": 0.27,
                    "desc": "Caries oclusal profunda cavitada con compromiso dentinario extenso.",
                },
            ],
        },
        # CASO 6: Rechazado Clínicamente (Falso Positivo)
        {
            "key": "caso_valeria",
            "paciente": pacientes["valeria"],
            "estudio": estudios["estudio_valeria"],
            "imagen": imagenes["estudio_valeria"],
            "estado": "RECHAZADO",
            "confianza": 0.68,
            "categoria": "BAJA",
            "segunda_opinion": True,
            "odontologo": odontologos["mendoza"],
            "notas": None,
            "motivo_rechazo": "Falso positivo descartado en examen físico. Corresponde a tinción extrínseca por consumo de té/café en surcos profundos de pieza 46. Sondaje dental y transiluminación descartan desmineralización activa.",
            "fecha_gen": NOW - timedelta(days=3),
            "fecha_val": NOW - timedelta(days=3, hours=-1),
            "hallazgos": [
                {
                    "diente": 46,
                    "cuadrante": 4,
                    "patologia": "CARIES",
                    "severidad": "LEVE",
                    "confianza": 0.68,
                    "bbox_x": 0.39,
                    "bbox_y": 0.34,
                    "bbox_w": 0.20,
                    "bbox_h": 0.24,
                    "desc": "Predicción de tinción oclusal catalogada como sospecha de caries leve.",
                },
            ],
        },
        # CASO 7: Validado Clínicamente - Cálculo Dental
        {
            "key": "caso_carmen",
            "paciente": pacientes["carmen"],
            "estudio": estudios["estudio_carmen"],
            "imagen": imagenes["estudio_carmen"],
            "estado": "VALIDADO",
            "confianza": 0.95,
            "categoria": "ALTA",
            "segunda_opinion": False,
            "odontologo": odontologos["salazar"],
            "notas": "Presencia confirmada de tártaro/cálculo supragingival en cuello cervical de incisivos inferiores 31 y 41. Se procede a realizar detartraje ultrasónico y profilaxis con pasta abrasiva.",
            "motivo_rechazo": None,
            "fecha_gen": NOW - timedelta(days=1),
            "fecha_val": NOW - timedelta(days=1, hours=-1),
            "hallazgos": [
                {
                    "diente": 31,
                    "cuadrante": 3,
                    "patologia": "CALCULO_DENTAL",
                    "severidad": "MODERADA",
                    "confianza": 0.95,
                    "bbox_x": 0.48,
                    "bbox_y": 0.36,
                    "bbox_w": 0.20,
                    "bbox_h": 0.24,
                    "desc": "Cálculo dental cervical visible en superficie vestibular/interproximal.",
                },
                {
                    "diente": 41,
                    "cuadrante": 4,
                    "patologia": "CALCULO_DENTAL",
                    "severidad": "MODERADA",
                    "confianza": 0.94,
                    "bbox_x": 0.28,
                    "bbox_y": 0.36,
                    "bbox_w": 0.20,
                    "bbox_h": 0.24,
                    "desc": "Depósito calcificado en tercio cervical dental.",
                },
            ],
        },
    ]

    for c in casos:
        # 1. Inferencia técnica
        inf_id = gen_uuid("inferencia", str(c["estudio"].id))
        inf_obj = db.query(models.InferenciaIAORM).filter_by(id=inf_id).first()
        if not inf_obj:
            inf_obj = models.InferenciaIAORM(
                id=inf_id,
                estudio_id=c["estudio"].id,
                modelo_ml_id=modelo_prod.id,
                estado="COMPLETADO",
                worker_id="celery-inference-worker-01",
                gpu_utilizada="NVIDIA GeForce RTX 4090 (24GB VRAM)",
                tiempo_ms=54.2,
                created_at=c["fecha_gen"] - timedelta(seconds=15),
                completed_at=c["fecha_gen"],
            )
            db.add(inf_obj)

        # 2. Diagnóstico clínico (Write Model)
        diag_id = gen_uuid("diagnostico", str(c["estudio"].id))
        diag_obj = db.query(models.DiagnosticoORM).filter_by(id=diag_id).first()
        if not diag_obj:
            diag_obj = models.DiagnosticoORM(
                id=diag_id,
                estudio_id=c["estudio"].id,
                paciente_id=c["paciente"].id,
                inferencia_id=inf_id,
                modelo_ml_id=modelo_prod.id,
                odontologo_id=c["odontologo"].id if c["odontologo"] else None,
                estado=c["estado"],
                confianza_global=c["confianza"],
                categoria_confianza=c["categoria"],
                tiempo_inferencia_ms=54.2,
                fecha_generacion=c["fecha_gen"],
                fecha_validacion=c["fecha_val"],
                notas_validacion=c["notas"],
                motivo_rechazo=c["motivo_rechazo"],
                created_at=c["fecha_gen"],
                updated_at=c["fecha_val"] or c["fecha_gen"],
            )
            db.add(diag_obj)
        else:
            diag_obj.estado = c["estado"]
            diag_obj.confianza_global = c["confianza"]
            diag_obj.categoria_confianza = c["categoria"]
            diag_obj.odontologo_id = c["odontologo"].id if c["odontologo"] else None
            diag_obj.fecha_validacion = c["fecha_val"]
            diag_obj.notas_validacion = c["notas"]
            diag_obj.motivo_rechazo = c["motivo_rechazo"]

        db.flush()

        # 3. Hallazgos anatómicos (Write Model)
        for h_data in c["hallazgos"]:
            hid = gen_uuid("hallazgo", f"{diag_id}:{h_data['diente']}:{h_data['patologia']}")
            h_obj = db.query(models.HallazgoORM).filter_by(id=hid).first()
            if not h_obj:
                h_obj = models.HallazgoORM(
                    id=hid,
                    diagnostico_id=diag_id,
                    imagen_id=c["imagen"].id,
                    tipo_patologia=h_data["patologia"],
                    severidad=h_data["severidad"],
                    confianza=h_data["confianza"],
                    diente_numero=h_data["diente"],
                    cuadrante=h_data["cuadrante"],
                    bbox_x=h_data["bbox_x"],
                    bbox_y=h_data["bbox_y"],
                    bbox_width=h_data["bbox_w"],
                    bbox_height=h_data["bbox_h"],
                    descripcion_clinica=h_data["desc"],
                    created_at=c["fecha_gen"],
                )
                db.add(h_obj)

        # 4. Auditoría de estado (Append-Only)
        if c["estado"] in ("VALIDADO", "RECHAZADO"):
            audit_id = gen_uuid("audit_diag", str(diag_id))
            audit_obj = db.query(models.AuditoriaDiagnosticoORM).filter_by(id=audit_id).first()
            if not audit_obj:
                audit_obj = models.AuditoriaDiagnosticoORM(
                    id=audit_id,
                    diagnostico_id=diag_id,
                    odontologo_id=c["odontologo"].id if c["odontologo"] else None,
                    estado_anterior="SUGERIDO_IA",
                    estado_nuevo=c["estado"],
                    notas=c["notas"] or c["motivo_rechazo"],
                    created_at=c["fecha_val"] or c["fecha_gen"],
                )
                db.add(audit_obj)

        # 5. CQRS Read Models
        # Si está pendiente de revisión (SUGERIDO_IA / EN_REVISION) → rm_cola_revision
        if c["estado"] in ("SUGERIDO_IA", "EN_REVISION"):
            cola_id = gen_uuid("rm_cola", str(diag_id))
            cola_obj = db.query(models.RMColaRevisionORM).filter_by(diagnostico_id=diag_id).first()
            if not cola_obj:
                cola_obj = models.RMColaRevisionORM(
                    id=cola_id,
                    diagnostico_id=diag_id,
                    paciente_id=c["paciente"].id,
                    estudio_id=c["estudio"].id,
                    paciente_nombre=f"{c['paciente'].nombres} {c['paciente'].apellidos}",
                    tipo_examen=c["estudio"].tipo_examen,
                    confianza_global=c["confianza"],
                    categoria_confianza=c["categoria"],
                    segunda_opinion=c["segunda_opinion"],
                    fecha_generacion=c["fecha_gen"],
                    created_at=c["fecha_gen"],
                )
                db.add(cola_obj)
            else:
                cola_obj.confianza_global = c["confianza"]
                cola_obj.categoria_confianza = c["categoria"]
                cola_obj.segunda_opinion = c["segunda_opinion"]
        else:
            # Si ya fue validado o rechazado, asegurarse de que no quede en la cola
            db.query(models.RMColaRevisionORM).filter_by(diagnostico_id=diag_id).delete()

        # Historial de paciente CQRS → rm_historial_paciente
        hist_id = gen_uuid("rm_historial", str(diag_id))
        hist_obj = db.query(models.RMHistorialPacienteORM).filter_by(diagnostico_id=diag_id).first()
        if not hist_obj:
            hist_obj = models.RMHistorialPacienteORM(
                id=hist_id,
                paciente_id=c["paciente"].id,
                estudio_id=c["estudio"].id,
                diagnostico_id=diag_id,
                fecha_estudio=c["estudio"].created_at,
                tipo_examen=c["estudio"].tipo_examen,
                estado_diagnostico=c["estado"],
                total_hallazgos=len(c["hallazgos"]),
                confianza_global=c["confianza"],
                odontologo_nombre=f"Dr(a). {c['odontologo'].nombres} {c['odontologo'].apellidos}" if c["odontologo"] else None,
                fecha_validacion=c["fecha_val"],
                updated_at=c["fecha_val"] or c["fecha_gen"],
            )
            db.add(hist_obj)
        else:
            hist_obj.estado_diagnostico = c["estado"]
            hist_obj.total_hallazgos = len(c["hallazgos"])
            hist_obj.confianza_global = c["confianza"]
            hist_obj.odontologo_nombre = f"Dr(a). {c['odontologo'].nombres} {c['odontologo'].apellidos}" if c["odontologo"] else None
            hist_obj.fecha_validacion = c["fecha_val"]

    db.commit()
    logger.info("  Diagnósticos clínicos y read models sincronizados.")


def seed_estadisticas_modelos(
    db: Session, modelos: dict[str, models.ModeloMLORM]
) -> None:
    """Siembra métricas de producción agregadas en rm_estadisticas_modelo."""
    logger.info("Sembrando Métricas de Producción en rm_estadisticas_modelo...")

    stats_data = [
        {
            "modelo": modelos["yolo_v8n"],
            "total_diagnosticos": 142,
            "total_validados": 131,
            "total_rechazados": 11,
            "tasa_validacion": 0.9225,
            "tasa_segunda_opinion": 0.0845,
        },
        {
            "modelo": modelos["yolo_v8s"],
            "total_diagnosticos": 35,
            "total_validados": 33,
            "total_rechazados": 2,
            "tasa_validacion": 0.9428,
            "tasa_segunda_opinion": 0.0571,
        },
        {
            "modelo": modelos["svm_hog"],
            "total_diagnosticos": 60,
            "total_validados": 46,
            "total_rechazados": 14,
            "tasa_validacion": 0.7667,
            "tasa_segunda_opinion": 0.3000,
        },
        {
            "modelo": modelos["rf_texture"],
            "total_diagnosticos": 50,
            "total_validados": 41,
            "total_rechazados": 9,
            "tasa_validacion": 0.8200,
            "tasa_segunda_opinion": 0.2200,
        },
        {
            "modelo": modelos["mobilenet_v3"],
            "total_diagnosticos": 40,
            "total_validados": 34,
            "total_rechazados": 6,
            "tasa_validacion": 0.8500,
            "tasa_segunda_opinion": 0.1750,
        },
    ]

    for item in stats_data:
        m = item["modelo"]
        sid = gen_uuid("rm_stats", str(m.id))
        obj = db.query(models.RMEstadisticasModeloORM).filter_by(modelo_ml_id=m.id).first()
        if not obj:
            obj = models.RMEstadisticasModeloORM(
                id=sid,
                modelo_ml_id=m.id,
                nombre_modelo=m.nombre,
                version=m.version,
                total_diagnosticos=item["total_diagnosticos"],
                total_validados=item["total_validados"],
                total_rechazados=item["total_rechazados"],
                tasa_validacion=item["tasa_validacion"],
                tasa_segunda_opinion=item["tasa_segunda_opinion"],
                updated_at=NOW,
            )
            db.add(obj)
        else:
            obj.total_diagnosticos = item["total_diagnosticos"]
            obj.total_validados = item["total_validados"]
            obj.total_rechazados = item["total_rechazados"]
            obj.tasa_validacion = item["tasa_validacion"]
            obj.tasa_segunda_opinion = item["tasa_segunda_opinion"]
            obj.updated_at = NOW

    db.commit()
    logger.info("  %d estadísticas de modelos en producción listas.", len(stats_data))


def main() -> None:
    parser = argparse.ArgumentParser(description="Seeder Idempotente para Dental App Local")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Limpia todas las tablas antes de sembrar los datos",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        logger.info("=== INICIANDO SEEDER CLÍNICO LOCAL (DENTAL APP) ===")
        if args.reset:
            limpiar_base_de_datos(db)

        odontologos = seed_odontologos(db)
        modelos_ml = seed_modelos_ml(db)
        pacientes = seed_pacientes(db)
        estudios, imagenes = seed_estudios_e_imagenes(db, pacientes)
        seed_casos_clinicos(db, pacientes, odontologos, modelos_ml, estudios, imagenes)
        seed_estadisticas_modelos(db, modelos_ml)

        logger.info("=== SEEDING COMPLETADO EXITOSAMENTE ===")
        logger.info("Resumen de datos en base de datos:")
        for tbl in [
            models.PacienteORM,
            models.OdontologoORM,
            models.ModeloMLORM,
            models.EstudioORM,
            models.ImagenIntraoralORM,
            models.DiagnosticoORM,
            models.HallazgoORM,
            models.RMColaRevisionORM,
            models.RMEstadisticasModeloORM,
            models.RMHistorialPacienteORM,
        ]:
            count = db.query(tbl).count()
            logger.info("  - %-25s: %d registros", tbl.__tablename__, count)

    except Exception as e:
        db.rollback()
        logger.error("Error durante el seeding: %s", e, exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
