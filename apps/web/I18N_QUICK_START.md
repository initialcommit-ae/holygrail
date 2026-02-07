# i18n Quick Start Guide

## 🌍 Supported Languages

- 🇬🇧 **English (en)** - Default
- 🇫🇷 **French (fr)**
- 🇸🇦 **Arabic (ar)** - RTL support

## 🚀 Quick Usage

### 1. In Client Components

```tsx
'use client';

import { useTranslations } from 'next-intl';

export default function MyComponent() {
  const t = useTranslations('namespace');

  return <h1>{t('key')}</h1>;
}
```

### 2. Add Language Switcher

Already integrated in Navbar! Users can switch languages from the header.

### 3. Add New Translations

Edit these files simultaneously:
- `messages/en.json`
- `messages/fr.json`
- `messages/ar.json`

```json
{
  "mySection": {
    "myKey": "My translation"
  }
}
```

## 📁 URL Structure

- `/en` or `/` → English
- `/fr` → French
- `/ar` → Arabic (RTL)

## ✅ Testing

```bash
pnpm dev

# Visit:
# http://localhost:3000/en
# http://localhost:3000/fr
# http://localhost:3000/ar
```

## 📚 Full Documentation

See `I18N_GUIDE.md` for comprehensive documentation.

## 🔧 Current Implementation

### Components with i18n:
- ✅ Navbar (with LanguageSwitcher)
- ✅ Hero section
- ✅ All translation files (en, fr, ar)

### To Do:
- 🔲 Update remaining marketing components
- 🔲 Add dashboard translations
- 🔲 Test all pages in all languages

## 💡 Pro Tips

1. Always use translation keys - never hardcode strings
2. Keep all language files in sync
3. Test Arabic (RTL) layout separately
4. Use meaningful namespace names (navbar, hero, dashboard, etc.)
