// Lettura dei contenuti per le pagine e campi derivati in build
// (docs/schema-scheda.md, "Campi derivati in build, mai scritti nei file").
import { getCollection, type CollectionEntry } from 'astro:content';

/** Elezione mostrata dal sito. Cambia quando arrivano le schede 2027. */
export const ELEZIONE = 2022;

type Fonte = CollectionEntry<'fonti'>['data'];
type Partito = CollectionEntry<'partiti'>['data'];
type Citazione = CollectionEntry<'schede'>['data']['citazioni'][number];

const TIPO: Record<Fonte['tipo'], string> = {
  programma: 'Programma depositato',
  programma_esteso: 'Programma esteso',
  accordo_coalizione: 'Accordo di coalizione',
  documento_programmatico: 'Documento programmatico',
};

const TIPO_BREVE: Record<Fonte['tipo'], string> = {
  programma: 'Programma',
  programma_esteso: 'Programma esteso',
  accordo_coalizione: 'Accordo',
  documento_programmatico: 'Documento programmatico',
};

/** Per una posizione assente si apre il documento più vicino al deposito. */
const PRIORITA_TIPO: Fonte['tipo'][] = ['programma', 'accordo_coalizione', 'documento_programmatico', 'programma_esteso'];

export interface CitazioneMostrata {
  testo: string;
  documento: string;
  pagina: string;
  href: string;
}

export interface SchedaMostrata {
  id: string;
  partito: Partito;
  posizione: 'dichiarata' | 'assente';
  titolo: string | undefined;
  stato: 'verificata' | 'contestata';
  /** Tipi di documento delle fonti, senza ripetizioni (es. "Programma depositato"). */
  tipi: string[];
  /** "Partito" oppure "Coalizione", senza ripetizioni. */
  livelli: string[];
  citazioni: CitazioneMostrata[];
  /** Documento da aprire per controllare un'assenza. */
  programma: { url: string } | undefined;
  entry: CollectionEntry<'schede'>;
}

const unici = <T,>(valori: T[]) => [...new Set(valori)];

function etichettaPagina(pagina: Citazione['pagina']) {
  return typeof pagina === 'number' ? `p. ${pagina}` : `pp. ${pagina}`;
}

function primaPagina(pagina: Citazione['pagina']) {
  return typeof pagina === 'number' ? pagina : Number(pagina.split('-')[0]);
}

const livello = (fonte: Fonte) => (fonte.partiti.length > 1 ? 'Coalizione' : 'Partito');

/**
 * Le schede pubblicate di un tema, in ordine alfabetico per sigla.
 * Le bozze non escono mai da qui. Un riferimento rotto ferma la build.
 */
export async function schedeDelTema(tema: string): Promise<SchedaMostrata[]> {
  const [schede, partiti, fonti] = await Promise.all([
    getCollection('schede', (s) => s.data.tema === tema && s.data.elezione === ELEZIONE && s.data.stato !== 'bozza'),
    getCollection('partiti'),
    getCollection('fonti'),
  ]);
  const partitoDa = new Map(partiti.map((p) => [p.id, p.data]));
  const fonteDa = new Map(fonti.map((f) => [f.id, f.data]));
  const sigla = (id: string) => partitoDa.get(id)?.sigla ?? id.toUpperCase();

  const mostrate = schede.map((entry): SchedaMostrata => {
    const s = entry.data;
    if (s.stato === 'bozza') throw new Error(`${entry.id}: una bozza non si pubblica`);
    const partito = partitoDa.get(s.partito);
    if (!partito) {
      throw new Error(`${entry.id}: manca contenuti/partiti/${s.partito}.yaml (nessuna scheda senza partito in perimetro)`);
    }

    const fontiCitate = s.citazioni.map((c) => {
      const fonte = fonteDa.get(c.fonte);
      if (!fonte) throw new Error(`${entry.id}: la citazione punta alla fonte "${c.fonte}", che non esiste`);
      return fonte;
    });

    const fontiDelPartito = fonti
      .map((f) => f.data)
      .filter((f) => f.elezione === s.elezione && f.partiti.includes(s.partito))
      .sort((a, b) => PRIORITA_TIPO.indexOf(a.tipo) - PRIORITA_TIPO.indexOf(b.tipo));
    const programma = fontiDelPartito[0];
    if (s.posizione === 'assente' && !programma) {
      throw new Error(`${entry.id}: posizione assente, ma nessuna fonte ${s.elezione} elenca il partito "${s.partito}"`);
    }

    // Per un'assenza tipo e livello vengono dal documento che non tratta il tema.
    const fontiDiRiferimento = s.posizione === 'dichiarata' ? fontiCitate : [programma!];

    return {
      id: entry.id,
      partito,
      posizione: s.posizione,
      titolo: s.titolo,
      stato: s.stato,
      tipi: unici(fontiDiRiferimento.map((f) => TIPO[f.tipo])),
      livelli: unici(fontiDiRiferimento.map(livello)),
      citazioni: s.citazioni.map((c, i) => {
        const fonte = fontiCitate[i]!;
        return {
          testo: c.testo,
          documento: `${TIPO_BREVE[fonte.tipo]} ${fonte.partiti.map(sigla).join(' - ')} ${fonte.elezione}`,
          pagina: etichettaPagina(c.pagina),
          href: `${fonte.url}#page=${primaPagina(c.pagina)}`,
        };
      }),
      programma: programma && { url: programma.url },
      entry,
    };
  });

  return mostrate.sort((a, b) => a.partito.sigla.localeCompare(b.partito.sigla, 'it', { sensitivity: 'base' }));
}
