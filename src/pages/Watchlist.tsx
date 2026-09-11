import { Link } from 'react-router-dom'
import { MediaCard, SectionHeading } from '../components/ui'
import { mediaById } from '../data/mock'
import { useDemoStore } from '../store/demo'

export default function Watchlist() {
  const { watchlist } = useDemoStore()
  const items = watchlist.map((id) => mediaById(id)).filter((m) => m !== undefined)

  return (
    <div className="flex flex-col gap-6">
      <SectionHeading title="A minha watchlist" subtitle="Guardada apenas neste browser, como parte da demonstração" />

      {items.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border bg-card p-10 text-center">
          <p className="text-sm text-muted">
            Ainda não guardaste nenhum título. Explora o{' '}
            <Link to="/catalogo" className="font-semibold text-accent hover:text-accent-hover">
              catálogo
            </Link>{' '}
            e clica em "Adicionar à watchlist".
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {items.map((item) => (
            <MediaCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  )
}
