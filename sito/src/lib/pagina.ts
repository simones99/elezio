// Pagina di una citazione: intero, oppure intervallo "12-13" del PDF ufficiale.

/** Prima e ultima pagina; per un intero coincidono. */
export function estremi(pagina: number | string): [number, number] {
  if (typeof pagina === 'number') return [pagina, pagina];
  const [da, a] = pagina.split('-').map(Number);
  return [da ?? NaN, a ?? NaN];
}

/** "p. 7" oppure "pp. 8-9". */
export function etichetta(pagina: number | string) {
  const [da, a] = estremi(pagina);
  return da === a ? `p. ${da}` : `pp. ${da}-${a}`;
}
