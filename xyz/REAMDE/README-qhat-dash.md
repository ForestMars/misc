# Pedal 1

*A fast, role‑aware React dashboard stub with demo GitHub login,
built‑in docs and user management.*

<img src="https://img.shields.io/npm/v/vite_react_shadcn_ts" alt="npm version" />

<figure>
<img src="assets/ui/pedal_dashboard.png" title="Pedal 1 Dashboard"
width="60" />
<figcaption>Pedal 1 Dashboard</figcaption>
</figure>

## 🚀 Overview

Pedal 1 is a Vite‑powered React+TypeScript single‑page app scaffold
showcasing:

- Client‑side demo GitHub authentication
- Role‑based protected routes (admin, product_owner, etc.)
- Integrated documentation viewer
- User management interface

It bundles shadcn/UI + Radix components, React Query, React Router,
Framer Motion and Sonner toasts to jump‑start your dashboard.

## 🛠️ Quick Start

1.  Ensure you have Node.js ≥18 and npm.
2.  Clone the repo:

``` bash
git clone https://github.com/your‑org/pedal‑1.git
cd pedal‑1
```

1.  Install dependencies (we recommend npm):

``` bash
npm install
```

1.  Start dev server:

``` bash
npm run dev
```

\_Open [http://localhost:5173\_](http://localhost:5173_)

## 🔧 Installation Details

``` bash
# Production build
npm run build

# Preview the production bundle
npm run preview

# Lint all files
npm run lint
```

- Lockfile:\* This repo contains both \`package-lock.json\` and
  \`bun.lockb\`. Use one package manager—delete the other lockfile to
  avoid conflicts.

## 🗺️ Architecture

``` bash
📁 src/
 ├── main.tsx         # app entrypoint (renders <App/>)
 ├── App.tsx          # routes & providers (React Query, Router, Tooltip, Auth)
 ├── context/AuthContext.tsx   # demo auth logic & localStorage persistence
 ├── components/      # UI primitives (Toaster, ProtectedRoute, etc.)
 ├── pages/           # route targets: Index, Login, Documentation, UserManagement, Unauthorized, NotFound
 ├── hooks/           # custom React hooks
 └── lib/             # utilities
```

## ⚙️ Configuration

No env vars required for demo. To wire real GitHub OAuth:

``` bash
# in project root:
echo "VITE_GITHUB_CLIENT_ID=your_id" > .env
echo "VITE_GITHUB_CLIENT_SECRET=your_secret" >> .env
```

Vite auto‑loads \`VITE\_\*\` vars. Replace the stub in
\`AuthContext.login()\`.

## 🧩 Features

- \*\*Demo GitHub Login:\*\* Click “Sign in with GitHub” in \`/login\`.
- \*\*Protected Routes:\*\* Wrap pages in \`<ProtectedRoute>\`; roles in
  \`AuthContext\`.
- \*\*Docs Viewer:\*\* Navigate to \`/documentation\`.
- \*\*User Management:\*\* Accessible under \`/user-management\` for
  admins; updates flow through Context and localStorage.
- \*\*Animations & Toasts:\*\* Powered by Framer Motion and Sonner.

## 📚 Usage Examples

- Accessing Dashboard\*

``` jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";

<BrowserRouter>
  <Routes>
    <Route path="/" element={<Index />} />
    <Route path="/login" element={<Login />} />
    <Route path="/documentation" element={
      <ProtectedRoute><Documentation /></ProtectedRoute>
    }/>
  </Routes>
</BrowserRouter>
```

- Adding a New Route\*

1\. Create \`src/pages/MyPage.tsx\`. 2. Add
\`<Route path="/my-page" element={<MyPage />} /\>\` in \`App.tsx\` above
\`\*\`.

## 🛡️ Caveats & Security

\- \*\*Demo‑only Auth:\*\* All auth is client‑side; credentials in
plaintext localStorage. - \*\*No XSS Sanitization:\*\* Inputs rendered
raw. - \*\*No Error Boundaries:\*\* Async failures have no fallbacks.

## 🧪 Testing

\_No tests found.\_ We welcome Jest + React Testing Library
contributions. Suggested command:

``` bash
npm install --save-dev jest @testing-library/react @types/jest
```

## 🤝 Contributing

1\. Fork and branch off \`main\`. 2. Run \`npm install\` → \`npm run
lint\`. 3. Implement feature or bugfix; add tests. 4. Submit PR with
clear, scoped commit messages (Conventional Commits).

## 📄 License

\_No LICENSE file detected.\_ Consider adding an \[MIT
License\](https://choosealicense.com/licenses/mit/) to clarify usage
rights.

## 

Notes on This README== == This document reflects detailed codebase
analysis:

- Scripts & commands from \`package.json\`.
- Auth flow & routes from \`src/context/AuthContext.tsx\` and
  \`App.tsx\`.
- Feature set from \`src/pages\` and components.
- Stack versions from \`tsconfig.\*\`, \`vite.config.ts\`,
  \`tailwind.config.ts\`.
- Screenshot path from \`assets/ui/pedal_dashboard.png\`.
- Noted lockfile duplication, missing tests, missing license.