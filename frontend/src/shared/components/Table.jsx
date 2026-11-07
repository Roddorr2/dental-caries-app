import React from 'react';
import { Loader } from './Loader';
import { EmptyState } from './EmptyState';
import { ChevronLeft, ChevronRight } from 'lucide-react';

/**
 * Table médica austera con soporte para paginación y ordenamiento visual
 */
export const Table = ({
  columns = [],
  data = [],
  isLoading = false,
  emptyMessage = 'No hay registros disponibles',
  emptyDescription = '',
  emptyAction = null,
  keyExtractor = (item, idx) => item.id || idx,
  onRowClick = null,
  // Paginación opcional
  pagination = null, // { page, pageSize, total, onPageChange }
}) => {
  return (
    <div className="w-full bg-white border border-slate-200 rounded-xl overflow-hidden shadow-subtle flex flex-col min-w-0">
      <div className="overflow-x-auto overscroll-x-contain">
        <table className="w-full text-left text-xs sm:text-sm border-collapse font-sans">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/90 whitespace-nowrap">
              {columns.map((col, index) => (
                <th
                  key={col.key || index}
                  className={`py-3 px-3 sm:px-4 text-[11px] font-semibold text-slate-700 tracking-wider uppercase select-none ${col.className || ''}`}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isLoading ? (
              <tr>
                <td colSpan={columns.length} className="py-8">
                  <Loader size="md" message="Cargando registros clínicos..." />
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="py-6">
                  <EmptyState
                    title={emptyMessage}
                    description={emptyDescription}
                    action={emptyAction}
                    bordered={false}
                  />
                </td>
              </tr>
            ) : (
              data.map((item, index) => {
                const rowKey = keyExtractor(item, index);
                return (
                  <tr
                    key={rowKey}
                    onClick={() => onRowClick && onRowClick(item)}
                    className={`transition-colors ${
                      onRowClick ? 'cursor-pointer hover:bg-slate-50 active:bg-slate-100' : 'hover:bg-slate-50/50'
                    }`}
                  >
                    {columns.map((col, cIndex) => (
                      <td
                        key={col.key || cIndex}
                        className={`py-2.5 px-3 sm:py-3 sm:px-4 text-slate-700 align-middle ${col.cellClassName || ''}`}
                      >
                        {col.render ? col.render(item, index) : item[col.accessor]}
                      </td>
                    ))}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pie de tabla con controles de paginación responsivos */}
      {pagination && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-2.5 px-3 sm:px-4 py-2.5 border-t border-slate-200 bg-slate-50 text-xs text-slate-500 font-sans">
          <div className="text-center sm:text-left">
            <span>
              Página <span className="font-semibold text-slate-800">{pagination.page}</span> de <span className="font-semibold text-slate-800">{Math.max(1, Math.ceil((pagination.total || 0) / pagination.pageSize))}</span>
            </span>
            {pagination.total !== undefined && (
              <span className="ml-1.5 text-slate-400 font-sans">
                ({pagination.total} registros en total)
              </span>
            )}
          </div>
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              disabled={pagination.page <= 1}
              onClick={() => pagination.onPageChange(pagination.page - 1)}
              className="w-8 h-8 flex items-center justify-center rounded-lg border border-slate-300 bg-white text-slate-600 hover:bg-slate-50 active:bg-slate-100 disabled:opacity-40 disabled:pointer-events-none transition-colors"
              aria-label="Página anterior"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              type="button"
              disabled={pagination.page >= Math.ceil((pagination.total || 0) / pagination.pageSize)}
              onClick={() => pagination.onPageChange(pagination.page + 1)}
              className="w-8 h-8 flex items-center justify-center rounded-lg border border-slate-300 bg-white text-slate-600 hover:bg-slate-50 active:bg-slate-100 disabled:opacity-40 disabled:pointer-events-none transition-colors"
              aria-label="Página siguiente"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
