import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Interceptor de respuestas para estandarizar datos y manejar errores clínicos contextualmente
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    let message = 'Error en el servidor clínico';
    let isNetworkError = false;

    if (!error.response) {
      isNetworkError = true;
      message = 'No fue posible sincronizar los datos con el servidor clínico. Verifique su conexión de red o contacte al soporte.';
    } else {
      if (error.response.status >= 500) {
        message = 'El servidor clínico reportó una incidencia interna. Intente nuevamente en unos instantes.';
      }

      if (error.response.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          message = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          // Validación de campos clínicos
          message = error.response.data.detail
            .map((err) => `${err.loc?.slice(1).join('.') || 'campo'}: ${err.msg}`)
            .join(', ');
        }
      } else if (error.response.status === 404) {
        message = 'Recurso clínico no encontrado.';
      } else if (error.response.status === 409) {
        message = 'Conflicto de dominio clínico o registro duplicado.';
      }
    }

    const clinicalError = new Error(message);
    clinicalError.status = error.response?.status;
    clinicalError.isNetworkError = isNetworkError;
    clinicalError.originalError = error;

    return Promise.reject(clinicalError);
  }
);
