# Miracle Birds — Frontend

Next.js 14 web application for the Miracle Birds AI Intelligence Platform.

## Tech Stack

- **Next.js 14** — App Router, React Server Components
- **TypeScript 5.3** — Strict mode
- **Tailwind CSS 3.4** — Utility-first styling
- **Shadcn UI** — Accessible components (Radix UI)
- **TanStack Query 5** — Server state, caching, background refresh
- **Zustand 4** — Client state (auth tokens, UI state)
- **React Hook Form + Zod** — Form handling and validation
- **Axios** — HTTP client with JWT interceptors

## Development

```bash
npm install
npm run dev       # http://localhost:3000
npm run build
npm run type-check
npm run lint
```

## Key Routes

| Route             | Description          |
| ----------------- | -------------------- |
| `/login`          | Authentication       |
| `/register`       | Sign up              |
| `/overview`       | Home dashboard       |
| `/customers`      | Customer list        |
| `/customers/[id]` | Customer 360 view    |
| `/copilot`        | AI Copilot chat      |
| `/predictions`    | Predictions overview |
| `/analytics`      | Analytics & charts   |
| `/integrations`   | CRM connections      |
| `/workflows`      | Workflow automation  |
| `/settings`       | Account settings     |

## Architecture

- Route groups: `(auth)` for unauthenticated pages, `(dashboard)` for protected pages
- `src/lib/api/` — Typed API functions using Axios
- `src/stores/` — Zustand stores (auth, UI)
- `src/types/` — Shared TypeScript interfaces
- `src/lib/hooks/` — Custom React hooks
- `src/components/features/` — Feature-specific components
- `src/components/layouts/` — Sidebar, nav shell
