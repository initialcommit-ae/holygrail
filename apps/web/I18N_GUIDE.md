# Internationalization (i18n) Guide

This application uses **next-intl** for internationalization with support for **English (en)**, **French (fr)**, and **Arabic (ar)**.

## Architecture

### Directory Structure

```
apps/web/
├── app/
│   ├── [locale]/           # Locale-based routing
│   │   ├── layout.tsx      # Locale-aware layout
│   │   ├── page.tsx        # Home page
│   │   └── marketing/      # Other pages
│   ├── components/
│   │   └── LanguageSwitcher/  # Language selector component
│   └── globals.css
├── i18n/
│   ├── config.ts          # Locale configuration
│   └── request.ts         # next-intl setup
├── messages/
│   ├── en.json           # English translations
│   ├── fr.json           # French translations
│   └── ar.json           # Arabic translations
└── middleware.ts         # Locale detection & routing
```

## Supported Languages

- **English (en)** - Default, LTR
- **French (fr)** - LTR
- **Arabic (ar)** - RTL (Right-to-Left)

## How to Use Translations

### In Client Components

```tsx
'use client';

import { useTranslations } from 'next-intl';

export default function MyComponent() {
  const t = useTranslations('namespace');

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  );
}
```

### In Server Components

```tsx
import { useTranslations } from 'next-intl';

export default async function MyServerComponent() {
  const t = await useTranslations('namespace');

  return (
    <div>
      <h1>{t('title')}</h1>
    </div>
  );
}
```

### Adding New Translations

1. Add the translation key to all language files in `messages/`:

**messages/en.json**
```json
{
  "myNamespace": {
    "newKey": "My new translation"
  }
}
```

**messages/fr.json**
```json
{
  "myNamespace": {
    "newKey": "Ma nouvelle traduction"
  }
}
```

**messages/ar.json**
```json
{
  "myNamespace": {
    "newKey": "ترجمتي الجديدة"
  }
}
```

2. Use in your component:
```tsx
const t = useTranslations('myNamespace');
<p>{t('newKey')}</p>
```

## URL Structure

The application uses locale-prefixed URLs:

- English: `https://yoursite.com/en` or `https://yoursite.com`
- French: `https://yoursite.com/fr`
- Arabic: `https://yoursite.com/ar`

## Language Switcher

The `<LanguageSwitcher />` component is already integrated in the Navbar. It:
- Displays the current language
- Allows users to switch between languages
- Preserves the current page path when switching
- Automatically applies RTL layout for Arabic

## RTL Support

Arabic language automatically applies `dir="rtl"` to the HTML element. The layout will mirror for Arabic users while maintaining LTR for English and French.

## Locale Detection

The middleware automatically:
1. Detects user's browser language preference
2. Redirects to appropriate locale
3. Handles locale-prefixed routes
4. Falls back to English if locale not supported

## Integration with Lingo.dev

This setup is compatible with Lingo.dev MCP server. You can:
1. Use Lingo.dev to generate translations
2. Export translations to the JSON files
3. Leverage AI-powered context-aware translations

## Best Practices

1. **Namespace Organization**: Group related translations under namespaces
   ```json
   {
     "navbar": { ... },
     "hero": { ... },
     "dashboard": { ... }
   }
   ```

2. **Consistent Keys**: Use camelCase for translation keys
   ```json
   {
     "getStarted": "Get Started",
     "learnMore": "Learn More"
   }
   ```

3. **Avoid Hardcoded Strings**: Always use translation keys, even for simple text

4. **Test All Locales**: Check your UI in all three languages, especially Arabic (RTL)

5. **Keep Translations Synchronized**: When adding new keys, update all language files

## Example: Full Component Translation

Before:
```tsx
export default function Hero() {
  return (
    <div>
      <h1>Welcome to MeshAI</h1>
      <button>Get Started</button>
    </div>
  );
}
```

After:
```tsx
'use client';

import { useTranslations } from 'next-intl';

export default function Hero() {
  const t = useTranslations('hero');

  return (
    <div>
      <h1>{t('title')}</h1>
      <button>{t('cta')}</button>
    </div>
  );
}
```

## Testing

Test the i18n setup:

```bash
# Run the development server
pnpm dev

# Visit:
# http://localhost:3000/en
# http://localhost:3000/fr
# http://localhost:3000/ar
```

## Troubleshooting

### Missing translations
If you see a translation key instead of text, check:
1. The key exists in all `messages/*.json` files
2. The namespace is correct in `useTranslations('namespace')`
3. No typos in the key name

### RTL not working
- Check that `localeDirections` in `i18n/config.ts` has `ar: 'rtl'`
- Verify the `dir` attribute is set on the `<html>` element

### Locale not detected
- Clear browser cache
- Check middleware configuration
- Verify locale is in the `locales` array in `i18n/config.ts`

## Resources

- [next-intl Documentation](https://next-intl.dev/)
- [Next.js App Router i18n](https://nextjs.org/docs/app/building-your-application/routing/internationalization)
- [Lingo.dev MCP](https://lingo.dev/en/mcp)
