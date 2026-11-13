import { expect, test, type Page } from '@playwright/test';

// Test di fumo sui contenuti di prova (tests/contenuti-prova), senza
// JavaScript: schede e citazioni devono essere HTML leggibile da solo.

async function senzaScorrimentoOrizzontale(page: Page) {
  const { larghezza, visibile } = await page.evaluate(() => ({
    larghezza: document.documentElement.scrollWidth,
    visibile: document.documentElement.clientWidth,
  }));
  expect(larghezza, 'la pagina scorre in orizzontale').toBeLessThanOrEqual(visibile);
}

test('la home porta alla pagina del tema', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('link', { name: 'Sanità' }).click();
  await expect(page).toHaveURL('/temi/sanita/');
});

test('la pagina tema mostra le schede pubblicate, non le bozze', async ({ page }) => {
  await page.goto('/temi/sanita/');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Sanità');
  await expect(page.getByText('Servizio sanitario nazionale, accesso alle cure e personale sanitario.')).toBeVisible();

  const schede = page.getByRole('article');
  await expect(schede).toHaveCount(2);
  // ordine alfabetico per sigla
  await expect(schede.nth(0)).toContainText('Alfa');
  await expect(schede.nth(1)).toContainText('Beta');

  await expect(page.getByText('Gamma')).toHaveCount(0);
  await expect(page.getByText('Titolo della bozza Gamma che non deve comparire')).toHaveCount(0);

  await senzaScorrimentoOrizzontale(page);
});

test('una posizione dichiarata mostra titolo, sintesi e citazioni con la pagina', async ({ page }) => {
  await page.goto('/temi/sanita/');
  const alfa = page.getByRole('article').filter({ hasText: 'Alfa' });

  await expect(alfa.getByRole('heading', { level: 2 })).toHaveText('Più medici di base nei quartieri e attese massime di 60 giorni');
  await expect(alfa).toContainText('Il partito Alfa vuole una casa della salute in ogni quartiere');
  await expect(alfa).toContainText('Programma depositato');
  await expect(alfa).toContainText('Verificata');

  const citazione = alfa.getByText('Apriremo una casa della salute in ogni quartiere con almeno dieci medici di base.');
  await expect(citazione).toBeHidden();
  await alfa.getByText('Leggi nel programma · 2 citazioni').click();
  await expect(citazione).toBeVisible();

  await expect(alfa.getByRole('link', { name: 'p. 7' })).toHaveAttribute('href', 'https://example.org/alfa/programma.pdf#page=7');
  await expect(alfa.getByRole('link', { name: 'pp. 8-9' })).toHaveAttribute('href', 'https://example.org/alfa/programma.pdf#page=8');

  await senzaScorrimentoOrizzontale(page);
});

test('una posizione assente ha lo stesso posto e il link al programma', async ({ page }) => {
  await page.goto('/temi/sanita/');
  const beta = page.getByRole('article').filter({ hasText: 'Beta' });

  await expect(beta.getByRole('heading', { level: 2 })).toHaveText('Il programma non tratta il tema');
  await expect(beta).toContainText('Verificata');
  await expect(beta.getByRole('link', { name: 'Controlla tu: apri il programma' })).toHaveAttribute(
    'href',
    'https://example.org/beta/programma.pdf',
  );
});
