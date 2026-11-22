import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { ArrowUpRight, ChevronDown, Search, X } from 'lucide-react';

interface Company {
  name: string;
  acronym: string;
  url: string;
  initial: string;
  gradient: string;
  logo?: string;
  subcategory?: 'urbanizaciones' | 'lotes' | 'inmobiliarias';
}

interface Rubro {
  id: string;
  name: string;
  companies: Company[];
}

const RUBROS: Rubro[] = [
  {
    id: 'maquinaria-pesada',
    name: 'Maquinaria pesada',
    companies: [
      { name: 'AGSA – Agencias Generales S.A.', acronym: 'AGSA', url: 'https://www.agsa.com/', initial: 'A', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/agsa.webp' },
      { name: 'Puntomaq / Komatsu Bolivia', acronym: 'KOMATSU', url: 'https://www.komatsulatinoamerica.com/bolivia/', initial: 'K', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/komatsu.webp' },
      { name: 'Gregomaq S.R.L.', acronym: 'GREGOMAQ', url: 'https://www.gregomaq.com/', initial: 'G', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/maquinaria-pesada_gregomaq.webp' },
      { name: 'Hansa Ltda. (Industria & Construcción)', acronym: 'HANSA', url: 'https://www.hi.com.bo/', initial: 'H', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/maquinaria-pesada_hansa.webp' },
      { name: 'Finning CAT Bolivia', acronym: 'FINNING CAT', url: 'https://www.finning.com/es_BO.html', initial: 'F', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/maquinaria-pesada_finning_cat.webp' },
      { name: 'SACI Maquinarias', acronym: 'SACI', url: 'https://www.saci.com.bo/', initial: 'S', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/maquinaria-pesada_saci.webp' },
    ],
  },
  {
    id: 'pintura',
    name: 'Pintura',
    companies: [
      { name: 'Pinturas MONOPOL', acronym: 'MONOPOL', url: 'https://www.pinturasmonopol.com/', initial: 'M', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/pintura_monopol.webp' },
      { name: 'FLEXCOLOR Bolivia', acronym: 'FLEXCOLOR', url: 'https://flex-color.com/', initial: 'F', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/pintura_flexcolor.webp' },
      { name: 'Pinturas Coral Bolivia', acronym: 'CORAL', url: 'https://www.coral.com.bo/', initial: 'C', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/pintura_coral.webp' },
      { name: 'Importadora Campero (Pinturas)', acronym: 'CAMPERO', url: 'https://importadoracampero.com.bo/', initial: 'C', gradient: 'linear-gradient(135deg,#00695C,#26A69A)', logo: '/assets/logos/pintura_campero.webp' },
      { name: 'Multicenter Bolivia (Pinturas)', acronym: 'MULTICENTER', url: 'https://www.multicenter.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#AD1457,#EC407A)', logo: '/assets/logos/pintura_multicenter.webp' },
      { name: 'Sika Pinturas y Revestimientos Bolivia', acronym: 'SIKA PINTURAS', url: 'https://bol.sika.com/', initial: 'S', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/pintura_sika_pinturas.webp' },
    ],
  },
  {
    id: 'materiales-electricos',
    name: 'Materiales eléctricos',
    companies: [
      { name: 'Electrored (Bolivia) S.R.L.', acronym: 'ELECTRORED', url: 'https://www.electrored.com.bo/', initial: 'E', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/materiales-electricos_electrored.webp' },
      { name: 'Bolivian Group S.R.L.', acronym: 'BOLIVIAN GROUP', url: 'https://bolivianelectric.com.bo/', initial: 'B', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/materiales-electricos_bolivian_group.webp' },
      { name: 'Homepac S.R.L. (Multicenter)', acronym: 'HOMEPAC', url: 'https://www.multicenter.com.bo/', initial: 'H', gradient: 'linear-gradient(135deg,#C62828,#EF5350)', logo: '/assets/logos/materiales-electricos_homepac.webp' },
      { name: 'Schneider Electric Bolivia', acronym: 'SCHNEIDER', url: 'https://www.se.com/bo/es/', initial: 'S', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/materiales-electricos_schneider.webp' },
      { name: 'Tigre Bolivia', acronym: 'TIGRE', url: 'https://tigre.bo/', initial: 'T', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/materiales-electricos_tigre.webp' },
      { name: 'Importadora Campero (Eléctricos)', acronym: 'CAMPERO', url: 'https://importadoracampero.com.bo/', initial: 'C', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/materiales-electricos_campero.webp' },
    ],
  },
  {
    id: 'ceramica',
    name: 'Cerámica',
    companies: [
      { name: 'Cerámica COBOCE', acronym: 'COBOCE', url: 'https://ceramicacoboce.com/', initial: 'C', gradient: 'linear-gradient(135deg,#6A1B9A,#AB47BC)', logo: '/assets/logos/ceramica_coboce.webp' },
      { name: 'Cerabol Ltda.', acronym: 'CERABOL', url: 'https://www.cerabol.com/', initial: 'C', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/ceramica_cerabol.webp' },
      { name: 'Industrias Duralit S.A.', acronym: 'DURALIT', url: 'https://duralit.com/', initial: 'D', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/ceramica_duralit.webp' },
      { name: 'Morales Ltda.', acronym: 'MORALES', url: 'https://www.morales.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#00695C,#26A69A)', logo: '/assets/logos/ceramica_morales.webp' },
      { name: 'Faboce S.R.L.', acronym: 'FABOCE', url: 'https://www.faboce.com.bo/', initial: 'F', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/ceramica_faboce.webp' },
      { name: 'Cerámica Gladymar', acronym: 'GLADYMAR', url: 'https://gladymar.com.bo/', initial: 'G', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/ceramica_gladymar.webp' },
    ],
  },
  {
    id: 'estanteria-industrial',
    name: 'Estantería industrial',
    companies: [
      { name: 'Sinter Bolivia', acronym: 'SINTER', url: 'https://sinterbolivia.com/', initial: 'S', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/estanteria-industrial_sinter.webp' },
      { name: 'DECO-IM', acronym: 'DECO-IM', url: 'https://www.decoim.cl/', initial: 'D', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/estanteria-industrial_deco_im.webp' },
      { name: 'Todocentro Estanterías', acronym: 'TODOCENTRO', url: 'https://todocentro.com.bo/', initial: 'T', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/estanteria-industrial_todocentro.webp' },
      { name: 'Multicenter Muebles & Racks', acronym: 'MULTICENTER', url: 'https://www.multicenter.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/estanteria-industrial_multicenter.webp' },
      { name: 'Industrias Ferrotodo (Estructuras)', acronym: 'FERROTODO', url: 'https://ferrotodo.com/', initial: 'F', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/estanteria-industrial_ferrotodo.webp' },
      { name: 'Hansa Logística Industrial', acronym: 'HANSA', url: 'https://www.hi.com.bo/', initial: 'H', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/estanteria-industrial_hansa.webp' },
    ],
  },
  {
    id: 'tableros-melaminicos',
    name: 'Tableros melamínicos',
    companies: [
      { name: 'SOBOLMA', acronym: 'SOBOLMA', url: 'https://sobolma.com/', initial: 'S', gradient: 'linear-gradient(135deg,#4527A0,#7E57C2)', logo: '/assets/logos/tableros-melaminicos_sobolma.webp' },
      { name: 'Laminex Bolivia', acronym: 'LAMINEX', url: 'https://www.laminexbolivia.com/', initial: 'L', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/tableros-melaminicos_laminex.webp' },
      { name: 'M.A.D. Center', acronym: 'M.A.D. CENTER', url: 'https://www.mad-center.com/', initial: 'M', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/tableros-melaminicos_m.a.d._center.webp' },
      { name: 'Duraplac Bolivia', acronym: 'DURAPLAC', url: 'https://duraplast.com.pe/', initial: 'D', gradient: 'linear-gradient(135deg,#AD1457,#EC407A)', logo: '/assets/logos/tableros-melaminicos_duraplac.webp' },
      { name: 'Todocentro Melaminas', acronym: 'TODOCENTRO', url: 'https://todocentro.com.bo/', initial: 'T', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/tableros-melaminicos_todocentro.webp' },
      { name: 'Importadora Campero (Maderas)', acronym: 'CAMPERO', url: 'https://importadoracampero.com.bo/', initial: 'C', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/materiales-electricos_campero.webp' },
    ],
  },
  {
    id: 'carpinteria',
    name: 'Carpintería',
    companies: [
      { name: 'Todocentro', acronym: 'TODOCENTRO', url: 'https://todocentro.com.bo/', initial: 'T', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/carpinteria_todocentro.webp' },
      { name: 'Makita Bolivia', acronym: 'MAKITA', url: 'https://www.makita.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#00695C,#26A69A)', logo: '/assets/logos/carpinteria_makita.webp' },
      { name: 'Bosch Professional Bolivia', acronym: 'BOSCH', url: 'https://www.bosch-professional.com/bo/es/', initial: 'B', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/carpinteria_bosch.webp' },
      { name: 'Hansa Herramientas & Equipos', acronym: 'HANSA', url: 'https://www.hi.com.bo/', initial: 'H', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/carpinteria_hansa.webp' },
      { name: 'Truper Bolivia (Salcedo Importaciones)', acronym: 'TRUPER', url: 'https://www.truper.com/', initial: 'T', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/carpinteria_truper.webp' },
      { name: 'Multicenter Carpintería', acronym: 'MULTICENTER', url: 'https://www.multicenter.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#AD1457,#EC407A)', logo: '/assets/logos/carpinteria_multicenter.webp' },
    ],
  },
  {
    id: 'cerrajeria',
    name: 'Cerrajería',
    companies: [
      { name: 'Yale Locks Bolivia (Salcedo / Multicenter)', acronym: 'YALE', url: 'https://www.multicenter.com.bo/', initial: 'Y', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/cerrajeria_yale.webp' },
      { name: 'Papaiz Cerraduras Bolivia', acronym: 'PAPAIZ', url: 'https://importadoracampero.com.bo/', initial: 'P', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/cerrajeria_papaiz.webp' },
      { name: 'Cerrajería Todocentro', acronym: 'TODOCENTRO', url: 'https://todocentro.com.bo/', initial: 'T', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/cerrajeria_todocentro.webp' },
      { name: 'Importadora Campero (Cerrajería)', acronym: 'CAMPERO', url: 'https://importadoracampero.com.bo/', initial: 'C', gradient: 'linear-gradient(135deg,#00695C,#26A69A)', logo: '/assets/logos/cerrajeria_campero.webp' },
      { name: 'Ferrotodo Herrajes & Seguridad', acronym: 'FERROTODO', url: 'https://ferrotodo.com/', initial: 'F', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/cerrajeria_ferrotodo.webp' },
      { name: 'Truper Cerraduras & Candados Bolivia', acronym: 'TRUPER', url: 'https://www.truper.com/', initial: 'T', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/carpinteria_truper.webp' },
    ],
  },
  {
    id: 'aluminio',
    name: 'Aluminio',
    companies: [
      { name: 'VidrAlum Bolivia', acronym: 'VIDRALUM', url: 'https://www.vidralum.com.bo/', initial: 'V', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/aluminio_vidralum.webp' },
      { name: 'Alvitec Carpintería de Aluminio', acronym: 'ALVITEC', url: 'https://www.alvitec.com.bo/', initial: 'A', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/aluminio_alvitec.webp' },
      { name: 'Cristembo Aluminio y Vidrio', acronym: 'CRISTEMBO', url: 'https://www.cristembo.com/', initial: 'C', gradient: 'linear-gradient(135deg,#00695C,#26A69A)', logo: '/assets/logos/aluminio_cristembo.webp' },
      { name: 'ProVen SRL Aluminio', acronym: 'PROVEN', url: 'https://www.provensrl.com/', initial: 'P', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/aluminio_proven.webp' },
      { name: 'Plamat Perfiles de Aluminio', acronym: 'PLAMAT', url: 'https://www.plamat.com.bo/', initial: 'P', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/aluminio_plamat.webp' },
      { name: 'Partner Bolivia Aluminio', acronym: 'PARTNER', url: 'https://www.partner.com.bo/', initial: 'P', gradient: 'linear-gradient(135deg,#6A1B9A,#AB47BC)', logo: '/assets/logos/aluminio_partner.webp' },
    ],
  },
  {
    id: 'decoracion-de-interior',
    name: 'Decoración de interior',
    companies: [
      { name: 'Multicenter Hogar & Decoración', acronym: 'MULTICENTER', url: 'https://www.multicenter.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#AD1457,#EC407A)', logo: '/assets/logos/decoracion-de-interior_multicenter.webp' },
      { name: 'Morales Ltda. Diseño Interior', acronym: 'MORALES', url: 'https://www.morales.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/decoracion-de-interior_morales.webp' },
      { name: 'Gladymar Ambientes & Deco', acronym: 'GLADYMAR', url: 'https://gladymar.com.bo/', initial: 'G', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/decoracion-de-interior_gladymar.webp' },
      { name: 'Faboce Revestimientos & Deco', acronym: 'FABOCE', url: 'https://www.faboce.com.bo/', initial: 'F', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/decoracion-de-interior_faboce.webp' },
      { name: 'Todocentro Decoración', acronym: 'TODOCENTRO', url: 'https://todocentro.com.bo/', initial: 'T', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/decoracion-de-interior_todocentro.webp' },
      { name: 'Cerabol Living', acronym: 'CERABOL', url: 'https://www.cerabol.com/', initial: 'C', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/decoracion-de-interior_cerabol.webp' },
    ],
  },
  {
    id: 'paisajismo',
    name: 'Paisajismo',
    companies: [
      { name: 'Milter Bolivia', acronym: 'MILTER', url: 'https://milter.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/paisajismo_milter.webp' },
      { name: 'Hansa Husqvarna Jardinería Bolivia', acronym: 'HUSQVARNA', url: 'https://www.hi.com.bo/', initial: 'H', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/paisajismo_husqvarna.webp' },
      { name: 'AGSA Maquinaria de Jardín', acronym: 'AGSA', url: 'https://www.agsa.com/', initial: 'A', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/paisajismo_agsa.webp' },
      { name: 'Multicenter Jardín y Riego', acronym: 'MULTICENTER', url: 'https://www.multicenter.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#00695C,#26A69A)', logo: '/assets/logos/paisajismo_multicenter.webp' },
      { name: 'Tigre Riego Bolivia', acronym: 'TIGRE', url: 'https://tigre.bo/', initial: 'T', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/paisajismo_tigre.webp' },
      { name: 'SACI Agro & Jardín Bolivia', acronym: 'SACI', url: 'https://www.saci.com.bo/', initial: 'S', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/paisajismo_saci.webp' },
    ],
  },
  {
    id: 'domotica',
    name: 'Domótica',
    companies: [
      { name: 'DOMOBOL Bolivia', acronym: 'DOMOBOL', url: 'https://domobol.com/', initial: 'D', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/domotica_domobol.webp' },
      { name: 'AGADON Seguridad Electrónica', acronym: 'AGADON', url: 'https://www.agadon.com.bo/seguridad-electronica.html', initial: 'A', gradient: 'linear-gradient(135deg,#C62828,#EF5350)', logo: '/assets/logos/domotica_agadon.webp' },
      { name: 'Tecnomatic Automatización Bolivia', acronym: 'TECNOMATIC', url: 'https://www.tecnomatic.com.bo/', initial: 'T', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/domotica_tecnomatic.webp' },
      { name: 'Electrored Domótica & Control', acronym: 'ELECTRORED', url: 'https://www.electrored.com.bo/', initial: 'E', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/seguridad_electrored.webp' },
      { name: 'Schneider Smart Home Bolivia', acronym: 'SCHNEIDER', url: 'https://www.se.com/bo/es/', initial: 'S', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/domotica_schneider.webp' },
      { name: 'Multicenter Smart Life', acronym: 'MULTICENTER', url: 'https://www.multicenter.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#AD1457,#EC407A)', logo: '/assets/logos/domotica_multicenter.webp' },
    ],
  },
  {
    id: 'seguridad',
    name: 'Seguridad',
    companies: [
      { name: 'S.I.PRO.C. Seguridad', acronym: 'SIPROC', url: 'https://www.siproc.com/', initial: 'S', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/seguridad_siproc.webp' },
      { name: 'Prosegur Bolivia', acronym: 'PROSEGUR', url: 'https://www.prosegur.com/', initial: 'P', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/seguridad_prosegur.webp' },
      { name: 'Seguridad Privada Boliviana', acronym: 'SEGURIBOL', url: 'https://seguribol.com.bo/', initial: 'S', gradient: 'linear-gradient(135deg,#00695C,#26A69A)', logo: '/assets/logos/seguridad_seguribol.webp' },
      { name: 'AGADON Sistemas de Seguridad', acronym: 'AGADON', url: 'https://www.agadon.com.bo/seguridad-electronica.html', initial: 'A', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/seguridad_agadon.webp' },
      { name: 'Electrored CCTV & Seguridad', acronym: 'ELECTRORED', url: 'https://www.electrored.com.bo/', initial: 'E', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/seguridad_electrored.webp' },
      { name: 'Bolivian Group Alarmas & Monitoreo', acronym: 'BOLIVIAN GROUP', url: 'https://bolivianelectric.com.bo/', initial: 'B', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/seguridad_bolivian_group.webp' },
    ],
  },
  {
    id: 'cemento',
    name: 'Cemento',
    companies: [
      { name: 'SOBOCE S.A.', acronym: 'SOBOCE', url: 'https://soboce.com/', initial: 'S', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/cemento_soboce.webp' },
      { name: 'FANCESA (Fábrica Nacional de Cemento)', acronym: 'FANCESA', url: 'https://fancesa.com/', initial: 'F', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/cemento_fancesa.webp' },
      { name: 'COBOCE Cemento', acronym: 'COBOCE', url: 'https://coboce.com/', initial: 'C', gradient: 'linear-gradient(135deg,#6A1B9A,#AB47BC)', logo: '/assets/logos/cemento_coboce.webp' },
      { name: 'Cemento El Puente (Tarija)', acronym: 'EL PUENTE', url: 'https://soboce.com/', initial: 'E', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/cemento_el_puente.webp' },
      { name: 'Cemento Viacha (La Paz)', acronym: 'VIACHA', url: 'https://soboce.com/', initial: 'V', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/cemento_viacha.webp' },
      { name: 'Cemento Warnes (Santa Cruz)', acronym: 'WARNES', url: 'https://soboce.com/', initial: 'W', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/cemento_warnes.webp' },
    ],
  },
  {
    id: 'ladrillo',
    name: 'Ladrillo',
    companies: [
      { name: 'Cerámica Titán', acronym: 'TITÁN', url: 'https://ceramicatitan.com/inicio/', initial: 'T', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/ladrillo_titan.webp' },
      { name: 'Cerámica COBOCE Ladrillos', acronym: 'COBOCE', url: 'https://ceramicacoboce.com/', initial: 'C', gradient: 'linear-gradient(135deg,#6A1B9A,#AB47BC)', logo: '/assets/logos/ladrillo_coboce.webp' },
      { name: 'Morales Ltda. Materiales Cerámicos', acronym: 'MORALES', url: 'https://www.morales.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/ladrillo_morales.webp' },
      { name: 'Importadora Campero (Mampostería)', acronym: 'CAMPERO', url: 'https://importadoracampero.com.bo/', initial: 'C', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/ladrillo_campero.webp' },
      { name: 'Gladymar Cerámica Estructural', acronym: 'GLADYMAR', url: 'https://gladymar.com.bo/', initial: 'G', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/ladrillo_gladymar.webp' },
      { name: 'Duralit Construcción', acronym: 'DURALIT', url: 'https://duralit.com/', initial: 'D', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/ladrillo_duralit.webp' },
    ],
  },
  {
    id: 'estuco',
    name: 'Estuco',
    companies: [
      { name: 'Estuco Vichaya / Super Yeso Vichaya', acronym: 'VICHAYA', url: 'https://estucovichaya.com/', initial: 'V', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/estuco_vichaya.webp' },
      { name: 'Monterrey Yesos & Acabados', acronym: 'MONTERREY', url: 'https://www.monterrey.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/estuco_monterrey.webp' },
      { name: 'Importadora Campero (Estucos)', acronym: 'CAMPERO', url: 'https://importadoracampero.com.bo/', initial: 'C', gradient: 'linear-gradient(135deg,#00695C,#26A69A)', logo: '/assets/logos/estuco_campero.webp' },
      { name: 'Sika Morteros & Yesos Bolivia', acronym: 'SIKA', url: 'https://bol.sika.com/', initial: 'S', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/estuco_sika.webp' },
      { name: 'Todocentro Revoques', acronym: 'TODOCENTRO', url: 'https://todocentro.com.bo/', initial: 'T', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/estuco_todocentro.webp' },
      { name: 'Multicenter Obra Fina', acronym: 'MULTICENTER', url: 'https://www.multicenter.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/estuco_multicenter.webp' },
    ],
  },
  {
    id: 'fierro',
    name: 'Fierro',
    companies: [
      { name: 'Aceros Arequipa Bolivia', acronym: 'ACEROS AREQUIPA', url: 'https://acerosarequipa.com/bo/', initial: 'A', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/fierro_aceros_arequipa.webp' },
      { name: 'Industrias Ferrotodo', acronym: 'FERROTODO', url: 'https://ferrotodo.com/', initial: 'F', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/fierro_ferrotodo.webp' },
      { name: 'ArcelorMittal Bolivia', acronym: 'ARCELORMITTAL', url: 'https://bolivia.arcelormittal.com/', initial: 'A', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/fierro_arcelormittal.webp' },
      { name: 'Importadora Campero', acronym: 'CAMPERO', url: 'https://importadoracampero.com.bo/', initial: 'C', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/fierro_campero.webp' },
      { name: 'Truper Bolivia (Salcedo Importaciones)', acronym: 'TRUPER', url: 'https://www.truper.com/', initial: 'T', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/fierro_truper.webp' },
      { name: 'Monterrey Aceros Bolivia', acronym: 'MONTERREY', url: 'https://www.monterrey.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/fierro_monterrey.webp' },
    ],
  },
  {
    id: 'pegamentos',
    name: 'Pegamentos',
    companies: [
      { name: 'Sika Bolivia', acronym: 'SIKA', url: 'https://bol.sika.com/', initial: 'S', gradient: 'linear-gradient(135deg,#F57F17,#FFEE58)', logo: '/assets/logos/pegamentos_sika.webp' },
      { name: 'Mapei Bolivia', acronym: 'MAPEI', url: 'https://mapei.com/bo/', initial: 'M', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/pegamentos_mapei.webp' },
      { name: 'Industrias del Oriente – MAXXI', acronym: 'MAXXI', url: 'https://ioriente.com/', initial: 'I', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/pegamentos_maxxi.webp' },
      { name: 'Weber / Saint-Gobain Bolivia', acronym: 'WEBER', url: 'https://saint-gobain.com/', initial: 'W', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/pegamentos_weber.webp' },
      { name: 'Chemical Bolivia Ltda.', acronym: 'CHEMICAL BOLIVIA', url: 'https://wetbolivia.com/', initial: 'C', gradient: 'linear-gradient(135deg,#C62828,#EF5350)', logo: '/assets/logos/pegamentos_chemical_bolivia.webp' },
      { name: 'Pinturas Monopol (Pegamentos & Colas)', acronym: 'MONOPOL', url: 'https://www.pinturasmonopol.com/', initial: 'M', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/pegamentos_monopol.webp' },
    ],
  },
  {
    id: 'vidrio',
    name: 'Vidrio',
    companies: [
      { name: 'Rojas Glass', acronym: 'ROJAS GLASS', url: 'https://rojasglass.com.bo/', initial: 'R', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/vidrio_rojas_glass.webp' },
      { name: 'Cristembo (Industria del Vidrio)', acronym: 'CRISTEMBO', url: 'https://www.cristembo.com/', initial: 'C', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/vidrio_cristembo.webp' },
      { name: 'VidrAlum Bolivia (Vidrios Templados)', acronym: 'VIDRALUM', url: 'https://www.vidralum.com.bo/', initial: 'V', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/vidrio_vidralum.webp' },
      { name: 'Alvitec Vidrios & Cerramientos', acronym: 'ALVITEC', url: 'https://www.alvitec.com.bo/', initial: 'A', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/vidrio_alvitec.webp' },
      { name: 'ProVen SRL Vidriería', acronym: 'PROVEN', url: 'https://www.provensrl.com/', initial: 'P', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/vidrio_proven.webp' },
      { name: 'Partner Bolivia Cristal', acronym: 'PARTNER', url: 'https://www.partner.com.bo/', initial: 'P', gradient: 'linear-gradient(135deg,#6A1B9A,#AB47BC)', logo: '/assets/logos/vidrio_partner.webp' },
    ],
  },
  {
    id: 'techos',
    name: 'Techos / Calaminas',
    companies: [
      { name: 'CONDOR S.R.L. / Calaminas Cóndor', acronym: 'CÓNDOR', url: 'https://calaminascondor.com/', initial: 'C', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/techos_condor.webp' },
      { name: 'TODO TECHO Bolivia', acronym: 'TODO TECHO', url: 'https://todotechobolivia.com/', initial: 'T', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/techos_todo_techo.webp' },
      { name: 'CIF CONDOR S.R.L.', acronym: 'CIF CONDOR', url: 'https://calaminascondor.com/', initial: 'C', gradient: 'linear-gradient(135deg,#6A1B9A,#AB47BC)', logo: '/assets/logos/techos_cif_condor.webp' },
      { name: 'Importadora Campero (Techos & Cubiertas)', acronym: 'CAMPERO', url: 'https://importadoracampero.com.bo/', initial: 'C', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/techos_campero.webp' },
      { name: 'Industrias Duralit S.A. (Tejas)', acronym: 'DURALIT', url: 'https://duralit.com/', initial: 'D', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/techos_duralit.webp' },
      { name: 'Monterrey Calaminas & Estructuras', acronym: 'MONTERREY', url: 'https://www.monterrey.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/techos_monterrey.webp' },
    ],
  },
  {
    id: 'pisos',
    name: 'Pisos',
    companies: [
      { name: 'Cerámica Gladymar', acronym: 'GLADYMAR', url: 'https://gladymar.com.bo/', initial: 'G', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/pisos_gladymar.webp' },
      { name: 'Cerámica COBOCE Pisos', acronym: 'COBOCE', url: 'https://ceramicacoboce.com/', initial: 'C', gradient: 'linear-gradient(135deg,#6A1B9A,#AB47BC)', logo: '/assets/logos/pisos_coboce.webp' },
      { name: 'Faboce Pisos & Porcelanatos', acronym: 'FABOCE', url: 'https://faboce.com.bo/', initial: 'F', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/pisos_faboce.webp' },
      { name: 'Morales Ltda. Revestimientos', acronym: 'MORALES', url: 'https://morales.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#00695C,#26A69A)', logo: '/assets/logos/pisos_morales.webp' },
      { name: 'Cerabol Pisos', acronym: 'CERABOL', url: 'https://www.cerabol.com/', initial: 'C', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/pisos_cerabol.webp' },
      { name: 'Italpissos Bolivia', acronym: 'ITALPISSOS', url: 'https://italpisos.com.ec/', initial: 'I', gradient: 'linear-gradient(135deg,#AD1457,#EC407A)', logo: '/assets/logos/pisos_italpissos.webp' },
    ],
  },
  {
    id: 'equipamiento-de-cocina',
    name: 'Equipamiento de cocina',
    companies: [
      { name: 'EquipExitos Bolivia', acronym: 'EQUIPEXITOS', url: 'https://equipexitos.com/', initial: 'E', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/equipamiento-de-cocina_equipexitos.webp' },
      { name: 'IMPOAL Gastronomía Bolivia', acronym: 'IMPOAL', url: 'https://impoal.net/', initial: 'I', gradient: 'linear-gradient(135deg,#6A1B9A,#AB47BC)', logo: '/assets/logos/equipamiento-de-cocina_impoal.webp' },
      { name: 'Multicenter Cocinas & Hogar', acronym: 'MULTICENTER', url: 'https://www.multicenter.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#AD1457,#EC407A)', logo: '/assets/logos/equipamiento-de-cocina_multicenter.webp' },
      { name: 'Importadora Campero (Cocinas)', acronym: 'CAMPERO', url: 'https://importadoracampero.com.bo/', initial: 'C', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/equipamiento-de-cocina_campero.webp' },
      { name: 'Todocentro Cocinas Integrales', acronym: 'TODOCENTRO', url: 'https://todocentro.com.bo/', initial: 'T', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/equipamiento-de-cocina_todocentro.webp' },
      { name: 'Coprodumat Equipamiento Hogar', acronym: 'COPRODUMAT', url: 'https://coprodumat.com/', initial: 'C', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/equipamiento-de-cocina_coprodumat.webp' },
    ],
  },
  {
    id: 'banos-sanitarios-griferia',
    name: 'Baños / Sanitarios / Grifería',
    companies: [
      { name: 'Coprodumat Ltda.', acronym: 'COPRODUMAT', url: 'https://coprodumat.com/', initial: 'C', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/banos-sanitarios-griferia_coprodumat.webp' },
      { name: 'Sorimex S.R.L.', acronym: 'SORIMEX', url: 'https://sorimex.com/', initial: 'S', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/banos-sanitarios-griferia_sorimex.webp' },
      { name: 'FV / Canal Bolivia (Grifería)', acronym: 'FV BOLIVIA', url: 'https://importadoracampero.com.bo/producto/griferia/', initial: 'F', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/banos-sanitarios-griferia_fv_bolivia.webp' },
      { name: 'Importadora Campero (Sanitarios)', acronym: 'CAMPERO', url: 'https://importadoracampero.com.bo/', initial: 'C', gradient: 'linear-gradient(135deg,#00695C,#26A69A)', logo: '/assets/logos/banos-sanitarios-griferia_campero.webp' },
      { name: 'Morales Ltda. Baños y Sanitarios', acronym: 'MORALES', url: 'https://www.morales.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/banos-sanitarios-griferia_morales.webp' },
      { name: 'Gladymar Baños & Griferías', acronym: 'GLADYMAR', url: 'https://gladymar.com.bo/', initial: 'G', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/banos-sanitarios-griferia_gladymar.webp' },
    ],
  },
  {
    id: 'marcos-de-ventana',
    name: 'Marcos de ventana',
    companies: [
      { name: 'ProVen SRL (Ventanas PVC & Aislamiento)', acronym: 'PROVEN', url: 'https://www.provensrl.com/', initial: 'P', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/marcos-de-ventana_proven.webp' },
      { name: 'Plamat Bolivia (Sistemas de Ventanas)', acronym: 'PLAMAT', url: 'https://www.plamat.com.bo/', initial: 'P', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/marcos-de-ventana_plamat.webp' },
      { name: 'Monterrey (Puertas & Ventanas PVC)', acronym: 'MONTERREY', url: 'https://www.monterrey.com.bo/', initial: 'M', gradient: 'linear-gradient(135deg,#D32F2F,#FF5252)', logo: '/assets/logos/marcos-de-ventana_monterrey.webp' },
      { name: 'TecnoSuisse Bolivia', acronym: 'TECNOSUISSE', url: 'https://www.tecnosuisse.com/', initial: 'T', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/marcos-de-ventana_tecnosuisse.webp' },
      { name: 'VidrAlum Bolivia (Aluminio y Cerramientos)', acronym: 'VIDRALUM', url: 'https://www.vidralum.com.bo/', initial: 'V', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/marcos-de-ventana_vidralum.webp' },
      { name: 'Partner Bolivia (Sistemas Deceuninck)', acronym: 'PARTNER', url: 'https://www.partner.com.bo/', initial: 'P', gradient: 'linear-gradient(135deg,#6A1B9A,#AB47BC)', logo: '/assets/logos/marcos-de-ventana_partner.webp' },
    ],
  },
  {
    id: 'urbanizaciones',
    name: 'Urbanizaciones e Inmobiliarias',
    companies: [
      { name: 'Urubó Village', acronym: 'URUBÓ VILLAGE', url: 'https://villageurubo.com/', initial: 'U', gradient: 'linear-gradient(135deg,#0277BD,#29B6F6)', logo: '/assets/logos/urbanizaciones_urubo_village.webp', subcategory: 'urbanizaciones' },
      { name: 'Playa Turquesa', acronym: 'PLAYA TURQUESA', url: 'https://playaturquesa.bo/', initial: 'P', gradient: 'linear-gradient(135deg,#00695C,#26A69A)', logo: '/assets/logos/urbanizaciones_playa_turquesa.webp', subcategory: 'urbanizaciones' },
      { name: 'Grupo Sion Inmobiliaria', acronym: 'GRUPO SION', url: 'https://www.gruposion.bo/', initial: 'G', gradient: 'linear-gradient(135deg,#E65100,#FF9800)', logo: '/assets/logos/urbanizaciones_grupo_sion.webp', subcategory: 'urbanizaciones' },
      { name: 'Las Palmas del Urubó', acronym: 'LAS PALMAS', url: 'https://laspalmasdelurubo.com/', initial: 'L', gradient: 'linear-gradient(135deg,#2E7D32,#66BB6A)', logo: '/assets/logos/urbanizaciones_las_palmas.webp', subcategory: 'urbanizaciones' },
      { name: 'La Fuente Inmobiliaria', acronym: 'LA FUENTE', url: 'https://www.facebook.com/LaFuenteInmobiliaria/', initial: 'L', gradient: 'linear-gradient(135deg,#1565C0,#42A5F5)', logo: '/assets/logos/urbanizaciones_la_fuente.webp', subcategory: 'urbanizaciones' },
      { name: 'El Pahuichi Urbanizaciones', acronym: 'EL PAHUICHI', url: 'https://elpahuichi.com.bo/', initial: 'E', gradient: 'linear-gradient(135deg,#AD1457,#EC407A)', logo: '/assets/logos/urbanizaciones_el_pahuichi.webp', subcategory: 'lotes' },
      { name: 'RE/MAX Bolivia Real Estate', acronym: 'RE/MAX', url: 'https://www.remax.bo/', initial: 'R', gradient: 'linear-gradient(135deg,#0D47A1,#D32F2F)', logo: '/assets/logos/urbanizaciones_remax_bolivia.webp', subcategory: 'inmobiliarias' },
      { name: 'Century 21 Bolivia', acronym: 'CENTURY 21', url: 'https://c21.com.bo/(https://c21.com.bo/)', initial: 'C', gradient: 'linear-gradient(135deg,#B78A38,#E5C158)', logo: '/assets/logos/urbanizaciones_century21.webp', subcategory: 'inmobiliarias' },
      { name: 'Ciudad Milenio Urbanizaciones y Lotes', acronym: 'CIUDAD MILENIO', url: 'https://www.facebook.com/CiudadMilenioBolivia/', initial: 'M', gradient: 'linear-gradient(135deg,#0277BD,#00897B)', logo: '/assets/logos/urbanizaciones_ciudad_milenio.webp', subcategory: 'lotes' },
      { name: 'Terreno & Lotes Bolivia', acronym: 'TERRENOS & LOTES', url: 'https://www.facebook.com/TerrenosyLotesBolivia/', initial: 'T', gradient: 'linear-gradient(135deg,#2E7D32,#8BC34A)', logo: '/assets/logos/urbanizaciones_terreno_lotes.webp', subcategory: 'lotes' },
      { name: 'InfoCasas Bolivia', acronym: 'INFOCASAS', url: 'https://www.infocasas.com.bo/', initial: 'I', gradient: 'linear-gradient(135deg,#0288D1,#FF6F00)', logo: '/assets/logos/urbanizaciones_infocasas.webp', subcategory: 'inmobiliarias' },
      { name: 'Terranova Urbanizaciones', acronym: 'TERRANOVA', url: 'https://www.facebook.com/TerranovaUrbanizaciones/', initial: 'T', gradient: 'linear-gradient(135deg,#1B5E20,#4CAF50)', logo: '/assets/logos/urbanizaciones_terranova.webp', subcategory: 'urbanizaciones' },
      { name: 'TerrenoBolivia — Lotes y Terrenos', acronym: 'TERRENOBOLIVIA', url: 'https://www.facebook.com/terrenoslapazelaltobolivia/', initial: 'T', gradient: 'linear-gradient(135deg,#2E7D32,#F57F17)', logo: '/assets/logos/urbanizaciones_terrenobolivia_lotes.webp', subcategory: 'lotes' },
      { name: 'Kalomai Park Resort & Urbanizaciones', acronym: 'KALOMAI', url: 'https://www.facebook.com/kalomaipark/', initial: 'K', gradient: 'linear-gradient(135deg,#059669,#10B981)', logo: '/assets/logos/urbanizaciones_kalomai.webp', subcategory: 'urbanizaciones' },
      { name: 'Mar Adentro Urbanización & Crystal Lagoons', acronym: 'MAR ADENTRO', url: 'https://www.facebook.com/MarAdentroBolivia/', initial: 'M', gradient: 'linear-gradient(135deg,#0284C7,#38BDF8)', logo: '/assets/logos/urbanizaciones_mar_adentro.webp', subcategory: 'urbanizaciones' },
      { name: 'Condado del Valle Urbanizaciones', acronym: 'CONDADO DEL VALLE', url: 'https://www.facebook.com/Condadodelvallebolivia/', initial: 'C', gradient: 'linear-gradient(135deg,#B45309,#F59E0B)', logo: '/assets/logos/urbanizaciones_condado_del_valle.webp', subcategory: 'urbanizaciones' },
      { name: 'Colinas del Urubó Condominio Privado', acronym: 'COLINAS DEL URUBÓ', url: 'https://www.facebook.com/colinasdelurubo/', initial: 'C', gradient: 'linear-gradient(135deg,#15803D,#22C55E)', logo: '/assets/logos/urbanizaciones_colinas_del_urubo.webp', subcategory: 'urbanizaciones' },
      { name: 'Lotes al Día — Venta de Terrenos en Cuotas', acronym: 'LOTES AL DÍA', url: 'https://www.facebook.com/lotesaldia/', initial: 'L', gradient: 'linear-gradient(135deg,#B91C1C,#EF4444)', logo: '/assets/logos/urbanizaciones_terrenos_al_dia.webp', subcategory: 'lotes' },
      { name: 'Inbolsa — Terrenos & Lotes Urbanos', acronym: 'INBOLSA LOTES', url: 'https://www.inbolsa.com/', initial: 'I', gradient: 'linear-gradient(135deg,#4338CA,#6366F1)', logo: '/assets/logos/urbanizaciones_inbolsa.webp', subcategory: 'lotes' },
      { name: 'Lotes y Urbanizaciones La Paz - El Alto', acronym: 'LOTES LA PAZ', url: 'https://www.facebook.com/terrenoselaltoypaz/', initial: 'L', gradient: 'linear-gradient(135deg,#D97706,#FBBF24)', logo: '/assets/logos/urbanizaciones_lotes_la_paz.webp', subcategory: 'lotes' },
      { name: 'TerraVida — Lotes & Condominios Ecológicos', acronym: 'TERRAVIDA', url: 'https://www.facebook.com/terravidabolivia/', initial: 'T', gradient: 'linear-gradient(135deg,#047857,#34D399)', logo: '/assets/logos/urbanizaciones_terravida.webp', subcategory: 'lotes' },
      { name: 'Smart Studio Desarrollos Inmobiliarios', acronym: 'SMART STUDIO', url: 'https://www.smartstudio.com.bo/', initial: 'S', gradient: 'linear-gradient(135deg,#7C3AED,#A78BFA)', logo: '/assets/logos/urbanizaciones_smart_studio.webp', subcategory: 'inmobiliarias' },
      { name: 'Latin Bienes Raíces Bolivia', acronym: 'LATIN BIENES', url: 'https://www.latinbienesraices.com/', initial: 'L', gradient: 'linear-gradient(135deg,#0369A1,#0EA5E9)', logo: '/assets/logos/urbanizaciones_latin_bienes_raices.webp', subcategory: 'inmobiliarias' },
      { name: 'Bolivia Propiedades Portal Inmobiliario', acronym: 'BOLIVIA PROPIEDADES', url: 'https://www.boliviapropiedades.com/', initial: 'B', gradient: 'linear-gradient(135deg,#BE185D,#F43F5E)', logo: '/assets/logos/urbanizaciones_bolivia_propiedades.webp', subcategory: 'inmobiliarias' },
      { name: 'Casa Crédito Inmobiliaria Bolivia', acronym: 'CASA CRÉDITO', url: 'https://casacredito.com/bolivia/', initial: 'C', gradient: 'linear-gradient(135deg,#1D4ED8,#3B82F6)', logo: '/assets/logos/urbanizaciones_casa_credito.webp', subcategory: 'inmobiliarias' },
    ],
  },
];

const PILLS = [
  { id: 'all', label: `Todos los rubros (${RUBROS.length})` },
  { id: 'urbanizaciones', label: 'Urbanizaciones & Inmobiliarias' },
  { id: 'obra-gruesa', label: 'Obra Gruesa & Estructura' },
  { id: 'maquinaria', label: 'Maquinaria & Herramientas' },
  { id: 'acabados', label: 'Acabados & Decoración' },
  { id: 'tecnologia', label: 'Tecnología & Seguridad' },
];

const FILTER_MAP: Record<string, string[]> = {
  urbanizaciones: ['urbanizaciones'],
  'obra-gruesa': ['cemento', 'ladrillo', 'fierro', 'estuco', 'pegamentos'],
  maquinaria: ['maquinaria-pesada', 'carpinteria', 'cerrajeria', 'estanteria-industrial'],
  acabados: [
    'pintura',
    'ceramica',
    'tableros-melaminicos',
    'aluminio',
    'decoracion-de-interior',
    'paisajismo',
    'vidrio',
    'techos',
    'pisos',
    'equipamiento-de-cocina',
    'banos-sanitarios-griferia',
    'marcos-de-ventana',
  ],
  tecnologia: ['materiales-electricos', 'domotica', 'seguridad'],
};

type UrbanSubtab = 'all' | 'urbanizaciones' | 'lotes' | 'inmobiliarias';

/** Minúsculas y sin tildes: "cordoba" encuentra "Córdoba", "ceramica" encuentra "Cerámica". */
const normalize = (text: string) =>
  text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();

export default function RubrosDirectory() {
  const [query, setQuery] = useState('');
  const [activePill, setActivePill] = useState('all');
  const [openId, setOpenId] = useState<string | null>(null);
  const [urbanSubtab, setUrbanSubtab] = useState<UrbanSubtab>('all');

  const isSearching = query.trim() !== '';

  // Cada rubro con SOLO las empresas que corresponden a la búsqueda y a la pestaña activa
  const visibleRubros = useMemo(() => {
    const q = normalize(query);
    const allowed = activePill !== 'all' ? FILTER_MAP[activePill] : null;

    return RUBROS.filter((r) => !allowed || allowed.includes(r.id))
      .map((rubro) => {
        let companies = rubro.companies;

        if (q) {
          const rubroMatches = normalize(rubro.name).includes(q);
          if (!rubroMatches) {
            companies = companies.filter(
              (c) => normalize(c.name).includes(q) || normalize(c.acronym).includes(q),
            );
          }
        }

        if (rubro.id === 'urbanizaciones' && urbanSubtab !== 'all') {
          companies = companies.filter((c) => c.subcategory === urbanSubtab);
        }

        return { rubro, companies };
      })
      .filter(({ rubro, companies }) => !q || companies.length > 0 || normalize(rubro.name).includes(q));
  }, [query, activePill, urbanSubtab]);

  return (
    <section className="rubros" id="rubros">
      <div className="wrap">
        <motion.div
          className="section-head"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <span className="section-tag">Rubros expositores</span>
          <h2>Todo lo que se construye, en un solo pabellón</h2>
          <p>
            Los rubros líderes conforman la oferta integral de esta edición - desde
            urbanizaciones, lotes y maquinaria pesada hasta los acabados más finos.
          </p>
        </motion.div>

        <div className="rubros-controls-wrap">
          <div className="rubros-search-container relative flex items-center">
            <Search className="rubros-search-icon absolute left-4 text-gray-400" size={18} aria-hidden="true" />
            <input
              type="search"
              className="rubros-search-input"
              placeholder="Buscar rubro, empresa o producto..."
              aria-label="Buscar rubro, empresa o producto"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            {query && (
              <button
                type="button"
                className="rubros-clear-btn absolute right-4 text-gray-400 hover:text-black"
                onClick={() => setQuery('')}
                aria-label="Borrar búsqueda"
              >
                <X size={16} />
              </button>
            )}
          </div>

          <div className="rubros-pills-row">
            {PILLS.map((pill) => (
              <button
                key={pill.id}
                type="button"
                className={`rubro-pill ${activePill === pill.id ? 'active' : ''}`}
                aria-pressed={activePill === pill.id}
                onClick={() => setActivePill(pill.id)}
              >
                {pill.label}
              </button>
            ))}
          </div>
        </div>

        <div className="rubros-accordion">
          {visibleRubros.length === 0 && (
            <div className="companies-empty" role="status">
              <p>No se encontraron rubros ni empresas para &ldquo;{query.trim()}&rdquo;.</p>
            </div>
          )}

          {visibleRubros.map(({ rubro, companies }) => {
            const isOpen = openId === rubro.id || isSearching;
            const bodyId = `rubro-body-${rubro.id}`;
            const countLabel =
              rubro.companies.length > 0
                ? `${companies.length} empresa${companies.length === 1 ? '' : 's'}`
                : 'Próximamente';
            const countOf = (sub: UrbanSubtab) =>
              rubro.companies.filter((c) => c.subcategory === sub).length;

            return (
              <div key={rubro.id} className={`rubro-accordion-item ${isOpen ? 'open' : ''}`} data-id={rubro.id}>
                <button
                  className="rubro-accordion-header"
                  type="button"
                  aria-expanded={isOpen}
                  aria-controls={bodyId}
                  onClick={() => !isSearching && setOpenId(isOpen ? null : rubro.id)}
                >
                  <span className="rubro-accordion-icon" />
                  <span className="rubro-accordion-title">{rubro.name}</span>
                  <span className="rubro-accordion-count">{countLabel}</span>
                  <span className="rubro-accordion-chevron">
                    <ChevronDown size={18} />
                  </span>
                </button>

                {/* inert: el contenido colapsado no recibe foco de teclado */}
                <div className="rubro-accordion-body" id={bodyId} inert={!isOpen}>
                  <div className="rubro-accordion-inner">
                    {rubro.id === 'urbanizaciones' && (
                      <div className="urban-subnav-bar">
                        <button
                          type="button"
                          className={`urban-subtab-btn ${urbanSubtab === 'all' ? 'active' : ''}`}
                          onClick={() => setUrbanSubtab('all')}
                        >
                          Todos ({rubro.companies.length})
                        </button>
                        <button
                          type="button"
                          className={`urban-subtab-btn ${urbanSubtab === 'urbanizaciones' ? 'active' : ''}`}
                          onClick={() => setUrbanSubtab('urbanizaciones')}
                        >
                          Urbanizaciones &amp; Condominios ({countOf('urbanizaciones')})
                        </button>
                        <button
                          type="button"
                          className={`urban-subtab-btn ${urbanSubtab === 'lotes' ? 'active' : ''}`}
                          onClick={() => setUrbanSubtab('lotes')}
                        >
                          Lotes &amp; Terrenos ({countOf('lotes')})
                        </button>
                        <button
                          type="button"
                          className={`urban-subtab-btn ${urbanSubtab === 'inmobiliarias' ? 'active' : ''}`}
                          onClick={() => setUrbanSubtab('inmobiliarias')}
                        >
                          Inmobiliarias &amp; Portales ({countOf('inmobiliarias')})
                        </button>
                      </div>
                    )}

                    {companies.length > 0 ? (
                      <div className="companies-grid">
                        {companies.map((company) => (
                          <motion.a
                            key={`${rubro.id}-${company.name}`}
                            href={company.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="company-card"
                            title={`Visitar sitio de ${company.name}`}
                            whileHover={{ y: -4 }}
                            transition={{ duration: 0.2 }}
                          >
                            <div className="company-top-meta">
                              <span className="company-badge-tag">
                                {company.subcategory === 'lotes'
                                  ? 'Lotes & Terrenos'
                                  : company.subcategory === 'inmobiliarias'
                                    ? 'Inmobiliaria'
                                    : rubro.name}
                              </span>
                              <span className="company-arrow-icon">
                                <ArrowUpRight size={12} />
                              </span>
                            </div>

                            <div className="company-logo-box">
                              {company.logo ? (
                                <img
                                  src={company.logo}
                                  alt={`Logo ${company.name}`}
                                  className="company-logo-img"
                                  loading="lazy"
                                  decoding="async"
                                />
                              ) : (
                                <span className="company-initial" style={{ background: company.gradient }}>
                                  {company.initial}
                                </span>
                              )}
                            </div>

                            <div className="company-content">
                              <span className="company-acronym">{company.acronym}</span>
                              <p className="company-name">{company.name}</p>
                              <span className="text-[10px] font-mono text-[var(--yellow-dark)] font-bold mt-auto inline-flex items-center gap-1">
                                Visitar sitio web →
                              </span>
                            </div>
                          </motion.a>
                        ))}
                      </div>
                    ) : (
                      <div className="companies-empty">
                        <p>No se encontraron empresas en esta selección.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
