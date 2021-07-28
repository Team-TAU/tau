import 'prismjs';
import 'prismjs/themes/prism.css';
import 'prismjs/components/prism-json';

import 'primevue/resources/themes/saga-blue/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeflex/primeflex.css';
import 'primeicons/primeicons.css';

import { createApp } from 'vue';
import PrimeVue from 'primevue/config';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Panel from 'primevue/panel';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';

import App from './App.vue';
import router from './router';
import store from './store';

const app = createApp(App);
app
  .use(store)
  .use(router)
  .use(PrimeVue, { ripple: true, inputStyle: 'filled' });

app.component('InputText', InputText);
app.component('Password', Password);
app.component('Button', Button);
app.component('Panel', Panel);
app.component('DataTable', DataTable);
app.component('Column', Column);
app.component('Accordion', Accordion);
app.component('AccordionTab', AccordionTab);

app.mount('#app');
