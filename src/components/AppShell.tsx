import { Compass, ExternalLink, Film, Home, LayoutList, Search, User } from 'lucide-react'
import { type ReactNode, useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { currentUser } from '../data/mock'
import { cn } from '../lib/utils'
import { Avatar, DemoBanner, Logo } from './ui'

const NAV = [
  { to: '/', label: 'Início', icon: Home, end: true },
  { to: '/feed', label: 'Feed', icon: LayoutList },
  { to: '/descobrir', label: 'Descobrir', icon: Compass },
  { to: '/catalogo', label: 'Catálogo', icon: Film },
]

export function AppShell({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState('')
  const navigate = useNavigate()

  function submitSearch(e: React.FormEvent) {
    e.preventDefault()
    if (query.trim()) navigate(`/pesquisa?q=${encodeURIComponent(query.trim())}`)
  }

  return (
    <div className="flex min-h-screen flex-col">
      <DemoBanner />
      <div className="flex flex-1 flex-col md:flex-row">
        <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-sidebar px-4 py-6 md:flex">
          <Link to="/" className="mb-8 px-2">
            <Logo />
          </Link>
          <nav className="flex flex-col gap-1">
            {NAV.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                    isActive ? 'bg-accent-soft text-accent' : 'text-muted hover:bg-card hover:text-text',
                  )
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="mt-auto flex flex-col gap-1">
            <NavLink
              to="/watchlist"
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive ? 'bg-accent-soft text-accent' : 'text-muted hover:bg-card hover:text-text',
                )
              }
            >
              <LayoutList size={18} />
              Watchlist
            </NavLink>
            <Link
              to={`/perfil/${currentUser.username}`}
              className="mt-3 flex items-center gap-3 rounded-lg border border-border bg-card px-3 py-2 hover:border-border-strong"
            >
              <Avatar name={currentUser.name} color={currentUser.color} size="sm" />
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-text">{currentUser.name}</p>
                <p className="truncate text-xs text-muted">@{currentUser.username}</p>
              </div>
            </Link>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-10 flex items-center gap-3 border-b border-border bg-bg/95 px-4 py-3 backdrop-blur-sm md:px-8">
            <Link to="/" className="md:hidden">
              <Logo size="sm" />
            </Link>
            <form onSubmit={submitSearch} className="relative ml-auto w-full max-w-sm">
              <Search size={16} className="absolute top-1/2 left-3 -translate-y-1/2 text-faint" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Pesquisar filmes, séries, pessoas…"
                className="w-full rounded-full border border-border bg-card py-2 pr-3 pl-9 text-sm text-text placeholder:text-faint focus:border-accent focus:outline-none"
              />
            </form>
            <a
              href="https://lisfilms.pt"
              target="_blank"
              rel="noreferrer"
              title="Site oficial (lisfilms.pt)"
              className="flex shrink-0 items-center gap-1.5 rounded-full bg-accent px-3 py-2 text-sm font-semibold text-black shadow-glow transition-colors hover:bg-accent-hover sm:px-4"
            >
              <ExternalLink size={14} />
              <span className="hidden sm:inline">Site oficial</span>
            </a>
            <Link to={`/perfil/${currentUser.username}`} className="md:hidden">
              <User size={22} className="text-muted" />
            </Link>
          </header>

          <main className="flex-1 px-4 py-6 md:px-8 md:py-8">{children}</main>

          <nav className="sticky bottom-0 z-10 flex items-center justify-around border-t border-border bg-sidebar px-2 py-2 md:hidden">
            {[...NAV, { to: '/watchlist', label: 'Lista', icon: LayoutList }].map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  cn('flex flex-col items-center gap-0.5 px-2 py-1 text-[10px]', isActive ? 'text-accent' : 'text-muted')
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>
    </div>
  )
}
