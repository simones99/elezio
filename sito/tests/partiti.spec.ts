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
    const alfa = join(contenuti, 'partiti', 'alfa.yaml');
    const senzaInclusione = readFileSync(alfa, 'utf8').replace(/^inclusione:\n(?:[ ]+.*\n)+/m, '');
    expect(senzaInclusione, 'il file di prova deve avere un blocco inclusione da togliere').not.toContain('inclusione');
    writeFileSync(alfa, senzaInclusione);

    const build = spawnSync(process.execPath, ['node_modules/astro/bin/astro.mjs', 'build', '--outDir', join(cartella, 'dist')], {
      env: { ...process.env, ELEZIO_CONTENUTI: contenuti },
      encoding: 'utf8',
    });

    expect(build.status, 'la build doveva fallire').not.toBe(0);
    expect(build.stdout + build.stderr).toMatch(/alfa[\s\S]*inclusione/);
  } finally {
    rmSync(cartella, { recursive: true, force: true });
  }
});
