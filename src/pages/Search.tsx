import { useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Link } from 'react-router-dom'
import { Avatar, MediaCard, SectionHeading } from '../components/ui'
import { media, users } from '../data/mock'

export default function Search() {
  const [params] = useSearchParams()
  const q = (params.get('q') ?? '').trim().toLowerCase()

  const mediaResults = useMemo(
    () => (q ? media.filter((m) => m.title.toLowerCase().includes(q)) : []),
    [q],
  )
  const userResults = useMemo(
    () => (q ? users.filter((u) => u.name.toLowerCase().includes(q) || u.username.includes(q)) : []),
    [q],
  )

  return (
    <div className="flex flex-col gap-8">
      <SectionHeading title={q ? `Resultados para "${params.get('q')}"` : 'Pesquisar'} />

      {q && mediaResults.length === 0 && userResults.length === 0 && (
        <p className="text-sm text-muted">Nada encontrado. Tenta outro termo.</p>
      )}

      {mediaResults.length > 0 && (
        <section>
          <h3 className="mb-3 text-sm font-bold text-muted uppercase">Filmes e séries</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
            {mediaResults.map((item) => (
              <MediaCard key={item.id} item={item} />
            ))}
          </div>
        </section>
      )}

      {userResults.length > 0 && (
        <section>
          <h3 className="mb-3 text-sm font-bold text-muted uppercase">Pessoas</h3>
          <div className="flex flex-col gap-2">
            {userResults.map((user) => (
              <Link
                key={user.id}
                to={`/perfil/${user.username}`}
                className="flex items-center gap-3 rounded-xl border border-border bg-card p-3 hover:border-border-strong"
              >
                <Avatar name={user.name} color={user.color} size="sm" />
                <div>
                  <p className="text-sm font-semibold text-text">{user.name}</p>
                  <p className="text-xs text-muted">@{user.username}</p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
