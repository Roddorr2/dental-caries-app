import { create } from 'zustand';

/**
 * store.js
 * ========
 * Store global exclusivo para estado de UI del cliente (sin autenticación ni sesiones simuladas).
 * Regla de arquitectura: El estado del servidor NUNCA va aquí (va en React Query).
 */

export const useStore = create((set) => ({
  // Control visual del layout clínico
  sidebarCollapsed: false,
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  mobileMenuOpen: false,
  toggleMobileMenu: () => set((state) => ({ mobileMenuOpen: !state.mobileMenuOpen })),
  closeMobileMenu: () => set({ mobileMenuOpen: false }),

  // Preferencias visuales del visor fotográfico intraoral
  viewerPreferences: {
    showBoundingBoxes: true,
    showLabels: true,
    invertColors: false, // Inversión de imagen para inspección de contraste
    opacity: 0.9,
  },
  setViewerPreference: (key, value) =>
    set((state) => ({
      viewerPreferences: {
        ...state.viewerPreferences,
        [key]: value,
      },
    })),
}));
