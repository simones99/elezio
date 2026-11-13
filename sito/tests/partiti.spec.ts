import { expect, test } from '@playwright/test';
import { spawnSync } from 'node:child_process';
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

// docs/schema-scheda.md, "Vincoli verificati in build": ogni partito in
// `partiti/` ha `inclusione` compilata (ticket #43). Il test costruisce il
// sito da una copia dei contenuti di prova in cui un partito non la ha.

test('la build rifiuta un partito senza inclusione', () => {
  test.setTimeout(120_000);
  const cartella = mkdtempSync(join(tmpdir(), 'elezio-senza-inclusione-'));
  try {
    const contenuti = join(cartella, 'contenuti');
    cpSync('tests/contenuti-prova', contenuti, { recursive: true });
    const fileAlfa = join(contenuti, 'partiti', 'alfa.yaml');
    const senzaInclusione = readFileSync(fileAlfa, 'utf8').replace(/^inclusione:\n(?:[ ]+.*\n)+/m, '');
    expect(senzaInclusione, 'il file di prova deve avere un blocco inclusione da togliere').not.toContain('inclusione');
    writeFileSync(fileAlfa, senzaInclusione);

    const build = spawnSync(process.execPath, ['node_modules/astro/bin/astro.mjs', 'build', '--outDir', join(cartella, 'dist')], {
      env: { ...process.env, ELEZIO_CONTENUTI: contenuti },
      encoding: 'utf8',
    });

    expect(build.status, 'la build doveva fallire').not.toBe(0);
    // L'errore di schema di Astro, senza i colori del terminale.
    const uscita = (build.stdout + build.stderr).replace(/\x1b\[[0-9;]*m/g, '');
    expect(uscita).toContain('partiti → alfa data does not match collection schema');
    expect(uscita).toMatch(/inclusione: Required/);
  } finally {
    rmSync(cartella, { recursive: true, force: true });
  }
});
