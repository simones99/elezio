// Collezioni del sito, lette da `contenuti/` (docs/stack.md, ADR 0006).
//
// Lo schema zod valida forma e coerenza interna di ogni file e ferma la build
// se qualcosa non torna. Ciò che richiede il repo privato o incroci tra file
// (citazioni nel testo estratto, 300 parole, fonte che include il partito) sta
// in `pipeline verifica`: le due regole non si duplicano.
// Campi e vincoli: docs/schema-scheda.md.
import { defineCollection } from 'astro:content';
import { file, glob } from 'astro/loaders';
import { z } from 'astro/zod';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { cartellaContenuti } from './lib/cartella-contenuti.mjs';

const contenuti = cartellaContenuti();
// I loader vogliono URL `file:` (un percorso assoluto di Windows non passa).
const percorso = (...parti: string[]) => pathToFileURL(join(contenuti, ...parti)).href;
const cartella = (nome: string) => new URL(percorso(nome) + '/');

const slug = z.string().regex(/^[a-z0-9]+(-[a-z0-9]+)*$/, 'slug: minuscole, cifre e trattini, senza accenti né spazi');
const data = z.coerce.date();
const url = z.url({ protocol: /^https?$/ });
const elezione = z.number().int().min(2018).max(2100);
const una_riga = z.string().trim().min(1).regex(/^[^\n]*$/, 'una riga sola');

/** Il file `<id>.yaml` deve dichiarare `id: <id>`. */
function idDalNomeFile({ entry, data }: { entry: string; data: Record<string, unknown> }) {
  const atteso = entry.replace(/\.ya?ml$/, '');
  if (data['id'] !== atteso) {
    throw new Error(`${entry}: id "${String(data['id'])}" diverso dal nome del file ("${atteso}")`);
  }
  return atteso;
}

const temi = defineCollection({
  loader: file(percorso('temi.yaml')),
  schema: z.strictObject({
    id: slug,
    nome: una_riga,
    definizione: una_riga,
    sotto_questioni: z.array(una_riga).min(3).max(6),
    dentro: z.array(una_riga).min(1),
    altrove: z.array(una_riga).min(1),
  }),
});

const partiti = defineCollection({
  loader: glob({ pattern: '*.yaml', base: cartella('partiti'), generateId: idDalNomeFile }),
  schema: ({ image }) =>
    z.strictObject({
      id: slug,
      nome: una_riga,
      sigla: una_riga,
      nomi_precedenti: z.array(z.strictObject({ nome: una_riga, fino_al: data })).optional(),
      alias: z.array(una_riga).optional(),
      logo: image(),
      sito: url,
      inclusione: z.strictObject({
        via: z.enum(['percentuale', 'parlamentari']),
        verificata_il: data,
        fonte: url,
      }),
    }),
});

const fonti = defineCollection({
  loader: glob({ pattern: '*.yaml', base: cartella('fonti'), generateId: idDalNomeFile }),
  schema: z.strictObject({
    id: slug,
    titolo: una_riga,
    tipo: z.enum(['programma', 'programma_esteso', 'accordo_coalizione', 'documento_programmatico']),
    elezione,
    partiti: z.array(slug).min(1),
    url,
    hash: z.string().regex(/^[0-9a-f]{64}$/, 'SHA-256 in esadecimale minuscolo'),
    acquisito_il: data,
    archivio: url.optional(),
    pagine: z.number().int().positive(),
    testo_estratto: z.string().min(1),
    data_documento: data.optional(),
    copie_equivalenti: z
      .array(z.strictObject({ url, hash: z.string().regex(/^[0-9a-f]{64}$/), partito: slug }))
      .optional(),
    ocr: z.enum(['mistral-ocr', 'tesseract']).optional(),
    ocr_versione: z.string().optional(),
  }),
});

/** Intero, oppure intervallo "12-13" con la prima pagina minore della seconda. */
const pagina = z.union([
  z.number().int().positive(),
  z.string().regex(/^\d+-\d+$/, 'pagina: intero oppure intervallo "12-13"').refine((s) => {
    const [da, a] = s.split('-').map(Number);
    return da! > 0 && da! < a!;
  }, 'intervallo di pagine non crescente'),
]);

const citazione = z.strictObject({
  id: slug.optional(),
  fonte: slug,
  pagina,
  testo: z.string().trim().min(1),
});

/** `schede/<elezione>/<partito>/<tema>.md`: i tre slug devono coincidere col frontmatter. */
function idDelPercorso({ entry, data }: { entry: string; data: Record<string, unknown> }) {
  const parti = entry.replace(/\.md$/, '').split('/');
  if (parti.length !== 3) {
    throw new Error(`${entry}: il percorso deve essere schede/<elezione>/<partito>/<tema>.md`);
  }
  const [cartellaElezione, cartellaPartito, nomeTema] = parti;
  const errori: string[] = [];
  if (String(data['elezione']) !== cartellaElezione) errori.push(`elezione "${String(data['elezione'])}" ≠ cartella "${cartellaElezione}"`);
  if (data['partito'] !== cartellaPartito) errori.push(`partito "${String(data['partito'])}" ≠ cartella "${cartellaPartito}"`);
  if (data['tema'] !== nomeTema) errori.push(`tema "${String(data['tema'])}" ≠ nome del file "${nomeTema}"`);
  if (errori.length > 0) throw new Error(`${entry}: ${errori.join('; ')}`);
  return parti.join('/');
}

const schede = defineCollection({
  loader: glob({ pattern: '**/*.md', base: cartella('schede'), generateId: idDelPercorso }),
  schema: z
    .strictObject({
      partito: slug,
      tema: slug,
      elezione,
      posizione: z.enum(['dichiarata', 'assente']),
      titolo: z.string().trim().regex(/^[^\n]*$/, 'una riga sola').optional(),
      citazioni: z.array(citazione).default([]),
      stato: z.enum(['bozza', 'verificata', 'contestata']),
      verificata_il: data.optional(),
      revisore: z.string().trim().min(1).optional(),
      aggiornata_il: data,
      bozza_da: z.strictObject({ modello: z.string().min(1), prompt: z.string().min(1) }).optional(),
      note: z.string().optional(),
    })
    .superRefine((s, ctx) => {
      const errore = (path: string, message: string) => ctx.addIssue({ code: 'custom', path: [path], message });
      if (s.posizione === 'dichiarata') {
        if (!s.titolo) errore('titolo', 'posizione dichiarata senza titolo');
        if (s.citazioni.length === 0) errore('citazioni', 'posizione dichiarata senza citazioni');
      } else {
        if (s.titolo) errore('titolo', 'posizione assente con titolo');
        if (s.citazioni.length > 0) errore('citazioni', 'posizione assente con citazioni');
      }
      if (s.stato !== 'bozza') {
        if (!s.verificata_il) errore('verificata_il', `stato ${s.stato} senza verificata_il`);
        if (!s.revisore) errore('revisore', `stato ${s.stato} senza revisore`);
      }
      const id = s.citazioni.flatMap((c) => (c.id ? [c.id] : []));
      if (new Set(id).size !== id.length) errore('citazioni', 'id di citazione ripetuto nella scheda');
    }),
});

export const collections = { temi, partiti, fonti, schede };
