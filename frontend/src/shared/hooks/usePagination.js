import { useState, useMemo } from 'react';

/**
 * Hook reutilizable para paginación basada en limit y offset
 */
export function usePagination(initialPage = 1, initialPageSize = 20) {
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);

  const offset = useMemo(() => (page - 1) * pageSize, [page, pageSize]);
  const limit = pageSize;

  const goToNextPage = () => setPage((p) => p + 1);
  const goToPrevPage = () => setPage((p) => Math.max(1, p - 1));
  const resetPage = () => setPage(1);

  return {
    page,
    setPage,
    pageSize,
    setPageSize,
    offset,
    limit,
    goToNextPage,
    goToPrevPage,
    resetPage,
  };
}
