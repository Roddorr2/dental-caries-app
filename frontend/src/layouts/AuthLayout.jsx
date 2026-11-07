import React from 'react';
import { Outlet } from 'react-router-dom';

/**
 * Layout austero centrado para autenticación o pantallas modales completas
 */
export const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8 font-sans">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="w-10 h-10 mx-auto rounded bg-slate-900 text-white flex items-center justify-center font-bold text-sm tracking-wider mb-3">
          DA
        </div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          DentalApp
        </h2>
        <p className="mt-1 text-xs text-slate-500 font-mono">
          Sistema Clínico de Apoyo al Diagnóstico Odontológico
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 border border-slate-200 shadow-sm rounded-lg sm:px-10">
          <Outlet />
        </div>
      </div>
    </div>
  );
};
