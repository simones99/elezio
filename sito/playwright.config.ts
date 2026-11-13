import { defineConfig, devices } from '@playwright/test';

// Il test di fumo gira sul sito costruito dai contenuti di prova
// (tests/contenuti-prova), non da quelli veri: serve una scheda verificata,
// una assente e una bozza, che i contenuti veri non hanno ancora.
const porta = 4329;

export default defineConfig({
  testDir: 'tests',
  forbidOnly: !!process.env['CI'],
  retries: 0,
  reporter: process.env['CI'] ? 'github' : 'list',
  use: {
    baseURL: `http://localhost:${porta}`,
    javaScriptEnabled: false,
  },
  projects: [
    {
      name: 'telefono',
      use: { ...devices['Pixel 7'], viewport: { width: 390, height: 844 } },
    },
  ],
  webServer: {
    command: `pnpm astro build && pnpm astro preview --port ${porta}`,
    env: { ELEZIO_CONTENUTI: 'tests/contenuti-prova' },
    url: `http://localhost:${porta}/`,
    reuseExistingServer: !process.env['CI'],
    timeout: 120_000,
  },
});
