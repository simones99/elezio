// Dove stanno i contenuti: `../contenuti` del monorepo, oppure la cartella
// indicata da ELEZIO_CONTENUTI (relativa a `sito/`), usata dai test.
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const radiceSito = fileURLToPath(new URL('../../', import.meta.url));
const predefinita = resolve(radiceSito, '../contenuti');

/** Percorso assoluto della cartella dei contenuti; fallisce se non esiste. */
export function cartellaContenuti() {
  const scelta = process.env['ELEZIO_CONTENUTI'];
  const cartella = scelta ? resolve(radiceSito, scelta) : predefinita;
  if (!existsSync(cartella)) {
    throw new Error(`Cartella dei contenuti inesistente: ${cartella}`);
  }
  return cartella;
}

/**
 * Vero se la cartella non è quella vera del monorepo.
 * @param {string} cartella
 */
export function contenutiDiProva(cartella) {
  return cartella !== predefinita;
}
