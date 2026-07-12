# 🎨 TransitOps Frontend Architecture

Welcome to the frontend documentation for **TransitOps**. The frontend is built to be lightning-fast, highly responsive, and easy to maintain. It uses modern tools to ensure a premium user experience.

## 🛠️ Technology Stack
* **Framework:** React 19 (Modern UI library)
* **Language:** TypeScript (Ensures strict type-checking and fewer bugs)
* **Build Tool:** Vite (Extremely fast bundler and development server)
* **Styling:** Tailwind CSS V4 (Utility-first CSS for rapid, consistent styling)
* **Routing:** React Router DOM (Client-side routing without page reloads)
* **State Management:** Zustand (Lightweight and fast global state manager)
* **Forms & Validation:** React Hook Form + Zod (Strict, error-free form handling)
* **Icons:** Lucide React (Clean, professional SVG icons)
* **Charts:** Recharts (Interactive data visualizations)

---

## 📁 Project Structure
The frontend codebase is neatly organized inside the `src/` directory:

```text
Frontend/
├── src/
│   ├── components/    # Reusable UI parts (Buttons, Navbars, Modals, etc.)
│   ├── lib/           # Utility functions (API callers, formatters, Auth logic)
│   ├── mock-data/     # Static JSON data for offline development/testing
│   ├── routes/        # The actual Pages (Views) the user interacts with
│   ├── schemas/       # Zod validation schemas (mirroring the backend)
│   ├── store/         # Zustand global state (auth state, user data)
│   └── types/         # TypeScript Interfaces and Types
├── docs/              # Frontend Documentation
├── package.json       # Project dependencies and scripts
└── vite.config.ts     # Vite bundler configuration
```

---

## 🚀 How to Run the Frontend Locally

### Prerequisites
Make sure you have [Node.js](https://nodejs.org/) installed on your computer.

### Steps
1. **Open Terminal** in the `Frontend/` folder.
2. **Install Dependencies:** Run `npm install` to download all the necessary packages.
3. **Configure Environment:** Ensure you have a `.env` file that points to the backend (e.g., `VITE_API_BASE_URL=http://localhost:8000`).
4. **Start Development Server:** Run `npm run dev`.
5. **Open Browser:** Go to `http://localhost:5173/` (or the port Vite provides).

### Building for Production
When it's time to deploy the app to a live server:
1. Run `npm run build`
2. This will statically analyze the TypeScript (`tsc -b`) and bundle the React app into a highly optimized `dist/` folder containing static HTML, CSS, and JS files.
