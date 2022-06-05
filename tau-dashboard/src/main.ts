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
import Menu from 'primevue/menu';
import Card from 'primevue/card';
import InputSwitch from 'primevue/inputswitch';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import AutoComplete from 'primevue/autocomplete';
import OverlayPanel from 'primevue/overlaypanel';
import TextArea from 'primevue/textarea';
import InputNumber from 'primevue/inputnumber';
import SelectButton from 'primevue/selectbutton';
import Chip from 'primevue/chip';
import ToastService from 'primevue/toastservice';
import Toast from 'primevue/toast';

import App from './App.vue';
import router from './router';
import store from './store';

const app = createApp(App);
app
  .use(store)
  .use(router)
  .use(PrimeVue, { ripple: true, inputStyle: 'filled' })
  .use(ToastService);

app.component('InputText', InputText);
app.component('InputNumber', InputNumber);
app.component('Password', Password);
app.component('Button', Button);
app.component('Panel', Panel);
app.component('DataTable', DataTable);
app.component('Column', Column);
app.component('Accordion', Accordion);
app.component('AccordionTab', AccordionTab);
app.component('Menu', Menu);
app.component('Card', Card);
app.component('InputSwitch', InputSwitch);
app.component('Dialog', Dialog);
app.component('Dropdown', Dropdown);
app.component('AutoComplete', AutoComplete);
app.component('OverlayPanel', OverlayPanel);
app.component('TextArea', TextArea);
app.component('SelectButton', SelectButton);
app.component('Toast', Toast);
app.component('Chip', Chip);

app.mount('#app');
