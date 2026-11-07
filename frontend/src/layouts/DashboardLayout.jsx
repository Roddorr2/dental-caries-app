import React from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  Activity,
  Users,
  FolderOpen,
  Cpu,
  Menu,
  ShieldCheck,
} from "lucide-react";
import { useStore } from "../app/store";

export const DashboardLayout = () => {
  const {
    sidebarCollapsed,
    toggleSidebar,
  } = useStore();
  const location = useLocation();

  const navigation = [
    {
      name: "Cola de Revisión",
      shortName: "Revisión",
      to: "/revision",
      icon: Activity,
      description: "Diagnósticos IA pendientes",
    },
    {
      name: "Pacientes",
      shortName: "Pacientes",
      to: "/pacientes",
      icon: Users,
      description: "Historias clínicas y fichas",
    },
    {
      name: "Estudios Fotográficos",
      shortName: "Estudios",
      to: "/estudios",
      icon: FolderOpen,
      description: "Adquisición y archivo de fotos intraorales",
    },
  ];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 text-slate-900 font-sans">
      {/* ======================================================== */}
      {/* 1. Desktop Sidebar (md:flex) */}
      {/* ======================================================== */}
      <aside
        className={`hidden md:flex flex-col border-r border-slate-200 bg-white transition-all duration-150 z-20 shrink-0 ${
          sidebarCollapsed ? "w-16" : "w-64"
        }`}
      >
        {/* Cabecera del sidebar desktop */}
        <div
          className={`flex items-center h-14 border-b border-slate-200 bg-white transition-all ${
            sidebarCollapsed ? "justify-center px-0" : "justify-between px-4"
          }`}
        >
          {!sidebarCollapsed ? (
            <>
              <div className="flex items-center gap-2.5 overflow-hidden">
                <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold text-xs shrink-0 tracking-wider shadow-sm">
                  DA
                </div>
                <div className="truncate">
                  <span className="font-bold text-xs text-slate-900 tracking-tight block">
                    DENTAL APP
                  </span>
                  <span className="font-sans text-[10px] text-slate-500 uppercase tracking-wider block font-medium">
                    CDSS Clínico
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={toggleSidebar}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                title="Colapsar menú"
                aria-label="Colapsar barra lateral"
              >
                <Menu className="w-4 h-4" />
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={toggleSidebar}
              className="w-10 h-10 rounded-lg flex items-center justify-center text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
              title="Expandir menú"
              aria-label="Expandir barra lateral"
            >
              <Menu className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Lista de navegación principal desktop */}
        <nav className="flex-1 px-2 py-3 space-y-1.5 overflow-y-auto">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  sidebarCollapsed
                    ? `w-10 h-10 mx-auto flex items-center justify-center rounded-lg transition-colors ${
                        isActive
                          ? "bg-slate-900 text-white shadow-sm"
                          : "text-slate-500 hover:bg-slate-100 hover:text-slate-900"
                      }`
                    : `flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-lg transition-colors ${
                        isActive
                          ? "bg-slate-900 text-white shadow-sm"
                          : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                      }`
                }
                title={item.name}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {!sidebarCollapsed && (
                  <span className="truncate">{item.name}</span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Footer del sidebar desktop: Estado CDSS y Auditoría Técnica */}
        <div
          className={`border-t border-slate-200 bg-slate-50/70 transition-all ${
            sidebarCollapsed
              ? "p-2 flex flex-col items-center justify-center"
              : "p-3 space-y-2"
          }`}
        >
          {!sidebarCollapsed ? (
            <div className="space-y-2">
              <div className="flex items-start gap-2 px-1">
                <span className="relative flex h-2 w-2 mt-1 shrink-0">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <div className="min-w-0">
                  <p className="text-[11px] font-semibold text-slate-800 leading-tight">
                    Motor CDSS: Operativo
                  </p>
                  <p className="text-[10px] font-sans text-slate-500 leading-tight mt-0.5">
                    Protocolo: Caries Coronal (OMS CPO-D / ceo-d)
                  </p>
                </div>
              </div>

              {/* Enlace secundario discreto de auditoría y gobernanza médica */}
              <div className="pt-1.5 border-t border-slate-200/60">
                <NavLink
                  to="/admin/auditoria-modelo"
                  className={({ isActive }) =>
                    `flex items-center gap-1.5 text-[10px] font-mono px-1 py-1 rounded transition-colors ${
                      isActive
                        ? "text-slate-900 font-semibold bg-slate-200/60"
                        : "text-slate-400 hover:text-slate-700 hover:bg-slate-100"
                    }`
                  }
                  title="Auditoría técnica de modelos y métricas SaMD"
                >
                  <ShieldCheck className="w-3.5 h-3.5 shrink-0 text-slate-400" />
                  <span className="truncate">Auditoría del Modelo CDSS</span>
                </NavLink>
              </div>
            </div>
          ) : (
            <NavLink
              to="/admin/auditoria-modelo"
              title="Motor CDSS: Operativo | Clic para Auditoría Técnica"
              className="w-10 h-10 rounded-lg flex items-center justify-center hover:bg-slate-200/70 transition-colors relative text-slate-600 hover:text-slate-900"
            >
              <ShieldCheck className="w-5 h-5 text-slate-600" />
              <span className="absolute top-2 right-2 flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
            </NavLink>
          )}
        </div>
      </aside>

      {/* ======================================================== */}
      {/* 2. Main Workspace Area */}
      {/* ======================================================== */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Cabecera superior clínica responsiva */}
        <header className="h-14 bg-white border-b border-slate-200 px-3.5 sm:px-6 flex items-center justify-between shrink-0 z-10">
          <div className="flex items-center gap-2.5 sm:gap-3 min-w-0">
            {/* Logo en mobile */}
            <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex md:hidden items-center justify-center font-bold text-xs shrink-0 tracking-wider shadow-sm">
              DA
            </div>

            <div className="min-w-0">
              <h1 className="text-xs sm:text-sm font-semibold text-slate-900 tracking-tight truncate">
                <span className="sm:hidden">DentalApp CDSS</span>
                <span className="hidden sm:inline">Sistema de Apoyo al Diagnóstico Odontológico</span>
              </h1>
              <p className="hidden md:block text-[11px] text-slate-400 font-sans truncate">
                Fotografía Clínica Intraoral & Detección con IA
              </p>
            </div>
          </div>

          {/* Indicador de integridad y estado del servicio clínico */}
          <div className="flex items-center gap-2 shrink-0">
            {/* Indicador desktop */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-[11px] font-mono text-slate-700">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              <span>Estación Clínica</span>
            </div>

            {/* Indicador mobile compacto */}
            <div
              className="flex sm:hidden items-center gap-1 px-2 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-[10px] font-mono text-emerald-800"
              title="Estación Clínica Activa"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="font-semibold">ONLINE</span>
            </div>
          </div>
        </header>

        {/* Canvas de trabajo médico responsivo */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden bg-slate-50 p-3 sm:p-5 md:p-6 pb-20 md:pb-6 max-w-full">
          <Outlet />
        </main>

        {/* ======================================================== */}
        {/* 4. Mobile Bottom Navigation Bar (md:hidden) */}
        {/* ======================================================== */}
        <nav
          aria-label="Navegación inferior móvil"
          className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-white/95 backdrop-blur-md border-t border-slate-200 z-30 flex items-center justify-around px-1 shadow-[0_-2px_12px_rgba(0,0,0,0.06)]"
        >
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.to);
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={`flex-1 flex flex-col items-center justify-center py-1 px-1 rounded-lg transition-colors select-none ${
                  isActive
                    ? "text-slate-900 font-semibold"
                    : "text-slate-400 hover:text-slate-700 active:text-slate-900 font-normal"
                }`}
              >
                <div
                  className={`relative p-1 rounded-full transition-all ${
                    isActive ? "bg-slate-900 text-white scale-105 shadow-sm" : ""
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-[10px] tracking-tight mt-0.5 truncate max-w-[70px]">
                  {item.shortName}
                </span>
              </NavLink>
            );
          })}
        </nav>
      </div>
    </div>
  );
};
