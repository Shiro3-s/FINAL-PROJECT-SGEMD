import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    setupFiles: ['tests/setup.ts'],
    globalSetup: ['tests/globalSetup.ts'],
    restoreMocks: true,
    // La base es única para toda la suite: sin paralelismo entre archivos para que
    // las fixtures de cada uno no se pisen (§18.1).
    fileParallelism: false,
    testTimeout: 20_000,
    hookTimeout: 30_000,
  },
});
