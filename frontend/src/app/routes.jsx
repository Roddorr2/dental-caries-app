import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { DashboardLayout } from '../layouts/DashboardLayout';

// Pacientes
import { PacientesList } from '../modules/pacientes/pages/PacientesList';
import { PacienteDetail } from '../modules/pacientes/pages/PacienteDetail';

// Estudios
import { EstudiosList } from '../modules/estudios/pages/EstudiosList';
import { CrearEstudio } from '../modules/estudios/pages/CrearEstudio';
import { SubirImagen } from '../modules/estudios/pages/SubirImagen';
import { EstudioDetail } from '../modules/estudios/pages/EstudioDetail';

// Diagnósticos
import { ColaRevision } from '../modules/diagnosticos/pages/ColaRevision';
import { DiagnosticoDetail } from '../modules/diagnosticos/pages/DiagnosticoDetail';

// Auditoría y Gobernanza Técnica CDSS (Segregada de la UX Clínica)
import { ModelosDashboard } from '../modules/modelos/pages/ModelosDashboard';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <DashboardLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/revision" replace />,
      },
      // Diagnósticos & Cola de Revisión Clínica
      {
        path: 'revision',
        element: <ColaRevision />,
      },
      {
        path: 'diagnosticos/:id',
        element: <DiagnosticoDetail />,
      },
      // Directorio de Pacientes y Fichas
      {
        path: 'pacientes',
        element: <PacientesList />,
      },
      {
        path: 'pacientes/:id',
        element: <PacienteDetail />,
      },
      // Repositorio de Estudios Fotográficos Intraorales
      {
        path: 'estudios',
        element: <EstudiosList />,
      },
      {
        path: 'estudios/nuevo',
        element: <CrearEstudio />,
      },
      {
        path: 'estudios/:id',
        element: <EstudioDetail />,
      },
      {
        path: 'estudios/:id/subir-imagen',
        element: <SubirImagen />,
      },
      // Auditoría Técnica y Validación del Modelo (Segregado de la navegación clínica)
      {
        path: 'admin/auditoria-modelo',
        element: <ModelosDashboard />,
      },
      // Redirección retrocompatible de la ruta antigua
      {
        path: 'modelos',
        element: <Navigate to="/admin/auditoria-modelo" replace />,
      },
      // Fallback a Cola de Revisión
      {
        path: '*',
        element: <Navigate to="/revision" replace />,
      },
    ],
  },
]);

