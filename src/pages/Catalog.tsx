import { useMemo, useState } from 'react'
import { MediaCard, SectionHeading } from '../components/ui'
import { allGenres, media } from '../data/mock'
import { cn } from '../lib/utils'
import type { MediaType } from '../data/types'

const TYPES: { value: MediaType | 'todos'; label: string }[] = [
  { value: 'todos', label: 'Todos' },
  { value: 'filme', label: 'Filmes' },
  { value: 'serie', label: 'Séries' },
]

export default function Catalog() {
  const [type, setType] = useState<MediaType | 'todos'>('todos')
  const [genre, setGenre] = useState<string | null>(null)
  const [sort, setSort] = useState<'rating' | 'year'>('rating')

  const filtered = useMemo(() => {
    let list = media
    if (type !== 'todos') list = list.filter((m) => m.type === type)
    if (genre) list = list.filter((m) => m.genres.includes(genre))
    return [...list].sort((a, b) => (sort === 'rating' ? b.communityRating - a.communityRating : b.year - a.year))
  }, [type, genre, sort])

  return (
    <div className="flex flex-col gap-6">
      <SectionHeading title="Catálogo" subtitle="Explora todos os filmes e séries desta demonstração" />

      <div className="flex flex-wrap items-center gap-2">
        {TYPES.map((t) => (
          <button
            key={t.value}
            onClick={() => setType(t.value)}
            className={cn(
              'rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors',
              type === t.value
                ? 'border-accent bg-accent-soft text-accent'
                : 'border-border bg-card text-muted hover:text-text',
            )}
          >
            {t.label}
          </button>
        ))}
        <span className="mx-1 h-5 w-px bg-border" />
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as 'rating' | 'year')}
          className="rounded-full border border-border bg-card px-3 py-1.5 text-sm text-text focus:border-accent focus:outline-none"
        >
          <option value="rating">Melhor avaliados</option>
          <option value="year">Mais recentes</option>
        </select>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setGenre(null)}
          className={cn(
            'rounded-full px-3 py-1 text-xs font-medium transition-colors',
            genre === null ? 'bg-text text-bg' : 'bg-card text-muted hover:text-text',
          )}
        >
          Todos os géneros
        </button>
        {allGenres.map((g) => (
          <button
            key={g}
            onClick={() => setGenre(g === genre ? null : g)}
            className={cn(
              'rounded-full px-3 py-1 text-xs font-medium transition-colors',
              genre === g ? 'bg-text text-bg' : 'bg-card text-muted hover:text-text',
            )}
          >
            {g}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted">Nenhum título encontrado com estes filtros.</p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {filtered.map((item) => (
            <MediaCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  )
}
