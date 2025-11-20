import { defineConfig } from 'orval';

export default defineConfig({
  veyl: {
    output: {
      mode: 'tags-split',
      target: 'src/api/generated',
      schemas: 'src/api/generated/model',
      client: 'react-query',
      mock: false,
      override: {
        mutator: {
          path: './src/lib/axios.ts',
          name: 'customInstance',
        },
      },
    },
    input: {
      target: '../backend/openapi.json',
    },
  },
});
