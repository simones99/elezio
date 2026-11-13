// @ts-check
import { defineConfig } from 'astro/config';
import { cartellaContenuti, contenutiDiProva } from './src/lib/cartella-contenuti.mjs';

// Con ELEZIO_CONTENUTI il sito si costruisce da un'altra cartella (i contenuti
// di prova dei test): build e cache vanno in cartelle separate, così le due
// build non si mescolano.
const prova = contenutiDiProva(cartellaContenuti());

export default defineConfig({
  site: 'https://elezio.pages.dev',
  trailingSlash: 'always',
  outDir: prova ? './dist-prova' : './dist',
  cacheDir: prova ? './node_modules/.astro-prova' : './node_modules/.astro',
  devToolbar: { enabled: false },
});
