---
paths: "**/*.{ts,tsx,js,jsx}"
---

# Frontend Guidelines

## General
- Use TypeScript, not plain JavaScript — every new file should be `.ts` or `.tsx`
- Prefer functional components with hooks over class components
- Co-locate component, styles, and tests in the same directory

## Code Quality
- Lint: `npx eslint .`
- Format: `npx prettier --write .`
- Type check: `npx tsc --noEmit`

## Naming
- Components: PascalCase (`UserCard.tsx`)
- Hooks: camelCase prefixed with `use` (`useUserData.ts`)
- Utilities: camelCase (`formatDate.ts`)

## State & Data
- Keep state as local as possible — lift only when needed
- Use `const` for everything, `let` only when reassignment is unavoidable
- Avoid `any` — use `unknown` and narrow types explicitly

## Best Practices
- No magic strings — define constants
- Handle loading and error states explicitly, never assume success
- Avoid `useEffect` for derived state — compute it during render instead
