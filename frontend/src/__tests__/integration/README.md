# Integration tests (non-testing pages)

These tests cover all non-testing pages and exercise backend-connected flows.

## Required environment variables

- `EXPO_PUBLIC_BACKEND_URL`

The backend integration suite now creates a unique user first, logs in with that user, and then runs the rest of the backend tests.

## Run

```bash
npm run test:integration
```

## Test files

- `src/__tests__/integration/backendPages.integration.test.tsx`
  - Exercises `loginPage`, `createUserPage`, `allRecipePage`, `recipePage`, `chatHistoryPage`, and `chatPage` with live backend requests.
- `src/__tests__/integration/appRoutes.integration.test.tsx`
  - Covers non-testing route pages in `src/app`, including layouts and wrappers.

