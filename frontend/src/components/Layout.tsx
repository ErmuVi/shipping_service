import { Link, NavLink, Outlet } from "react-router-dom";

import { BoxIcon, ChatIcon, PlusIcon } from "./icons";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  [
    "inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition-colors",
    isActive
      ? "bg-indigo-50 text-indigo-700"
      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
  ].join(" ");

export function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6 lg:px-8">
          <Link to="/parcels" className="flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white">
              <BoxIcon className="h-5 w-5" />
            </span>
            <span className="flex flex-col leading-tight">
              <span className="text-sm font-semibold text-slate-900">
                Shipping Service
              </span>
              <span className="text-xs text-slate-500">
                Международная доставка
              </span>
            </span>
          </Link>

          <nav className="flex items-center gap-1">
            <NavLink to="/parcels" end className={navLinkClass}>
              <BoxIcon className="h-4 w-4" />
              Посылки
            </NavLink>
            <NavLink to="/parcels/new" className={navLinkClass}>
              <PlusIcon className="h-4 w-4" />
              Новая
            </NavLink>
            <NavLink to="/support" className={navLinkClass}>
              <ChatIcon className="h-4 w-4" />
              Поддержка
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6 lg:px-8">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-5 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <span>Shipping Service · демо-проект службы доставки</span>
          <a
            className="font-medium text-indigo-600 hover:text-indigo-500"
            href="/docs"
            target="_blank"
            rel="noreferrer"
          >
            API-документация (Swagger)
          </a>
        </div>
      </footer>
    </div>
  );
}
