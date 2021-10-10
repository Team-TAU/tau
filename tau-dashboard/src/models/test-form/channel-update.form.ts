import { FormEleDef } from './interfaces';

const form: FormEleDef[] = [
  {
    inputType: 'current-broadcaster',
    keys: [
      'broadcaster_user_id',
      'broadcaster_user_login',
      'broadcaster_user_name',
    ],
    label: '',
    default: null,
  },
  {
    inputType: 'twitch-category',
    keys: ['category_id', 'category_name'],
    label: 'Category',
    default: null,
  },
  {
    inputType: 'text-input',
    keys: ['title'],
    label: 'Title',
    default: null,
  },
  {
    inputType: 'twitch-language',
    keys: ['language'],
    label: 'Language',
    default: 'en',
  },
  {
    inputType: 'toggle',
    keys: ['is_mature'],
    label: 'Is Mature?',
    default: false,
  },
];

export default form;
