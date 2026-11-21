import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  // Dominio oficial (ajústalo si publicas en otro): necesario para canonical y Open Graph.
  site: 'https://www.expoinmobiliariayconstruccion.com',
  integrations: [react()],
});
