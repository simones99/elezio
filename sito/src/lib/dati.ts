// Lettura dei contenuti per le pagine e campi derivati in build
// (docs/schema-scheda.md, "Campi derivati in build, mai scritti nei file").
//
// Gli errori qui sotto non duplicano `pipeline verifica`: la pagina ha
// bisogno di partito e documento per disegnare la scheda, e senza non può
// che fermarsi.
import { getCollection, type CollectionEntry } from 'astro:content';
import { estremi, etichetta } from './pagina';

/** Elezione mostrata dal sito. Cambia quando arrivano le schede 2027. */
export const ELEZIONE = 2022;

type Fonte = CollectionEntry<'fonti'>['data'];
type Partito = CollectionEntry<'partiti'>['data'];

const ETICHETTA_TIPO: Record<Fonte['tipo'], string> = {
  programma: 'Programma depositato',
  programma_esteso: 'Programma esteso',
  accordo_coalizione: 'Accordo di coalizione',
  documento_programmatico: 'Documento programmatico',
};

const ETICHETTA_TIPO_BREVE: Record<Fonte['tipo'], string> = {
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
  /** Tipi di documento, senza ripetizioni (es. "Programma depositato"). */
  tipi: string[];
  /** "Partito" oppure "Coalizione", senza ripetizioni. */
  livelli: string[];
  citazioni: CitazioneMostrata[];
  /** Documento fonte da aprire per controllare un'assenza. */
  documentoDaAprire: { url: string } | undefined;
  entry: CollectionEntry<'schede'>;
}

const senzaRipetizioni = <T,>(valori: T[]) => [...new Set(valori)];

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

  const mostrate = schede.map((entry): SchedaMostrata => {
    const scheda = entry.data;
    if (scheda.stato === 'bozza') throw new Error(`${entry.id}: una bozza non si pubblica`);

    const partitoInPerimetro = (id: string) => {
      const partito = partitoDa.get(id);
      if (!partito) throw new Error(`${entry.id}: manca contenuti/partiti/${id}.yaml (nessun partito senza inclusione)`);
      return partito;
    };
    const partito = partitoInPerimetro(scheda.partito);

    const fontiCitate = scheda.citazioni.map((c) => {
      const fonte = fonteDa.get(c.fonte);
      if (!fonte) throw new Error(`${entry.id}: la citazione punta alla fonte "${c.fonte}", che non esiste`);
      return fonte;
    });

    const documentoDaAprire = fonti
      .map((f) => f.data)
      .filter((f) => f.elezione === scheda.elezione && f.partiti.includes(scheda.partito))
      .sort((a, b) => PRIORITA_TIPO.indexOf(a.tipo) - PRIORITA_TIPO.indexOf(b.tipo))[0];
    if (scheda.posizione === 'assente' && !documentoDaAprire) {
      throw new Error(`${entry.id}: posizione assente, ma nessuna fonte ${scheda.elezione} elenca il partito "${scheda.partito}"`);
    }

    // Per un'assenza tipo e livello vengono dal documento che non tratta il tema.
    const fontiDellaPosizione = scheda.posizione === 'dichiarata' ? fontiCitate : [documentoDaAprire!];

    return {
      id: entry.id,
      partito,
      posizione: scheda.posizione,
      titolo: scheda.titolo,
      stato: scheda.stato,
      tipi: senzaRipetizioni(fontiDellaPosizione.map((f) => ETICHETTA_TIPO[f.tipo])),
      livelli: senzaRipetizioni(fontiDellaPosizione.map(livello)),
      citazioni: scheda.citazioni.map((c, i) => {
        const fonte = fontiCitate[i]!;
        const sigle = fonte.partiti.map((id) => partitoInPerimetro(id).sigla).join(' - ');
        return {
          testo: c.testo,
          documento: `${ETICHETTA_TIPO_BREVE[fonte.tipo]} ${sigle} ${fonte.elezione}`,
          pagina: etichetta(c.pagina),
          href: `${fonte.url}#page=${estremi(c.pagina)[0]}`,
        };
      }),
      documentoDaAprire: documentoDaAprire && { url: documentoDaAprire.url },
      entry,
    };
  });

  return mostrate.sort((a, b) => a.partito.sigla.localeCompare(b.partito.sigla, 'it', { sensitivity: 'base' }));
}
