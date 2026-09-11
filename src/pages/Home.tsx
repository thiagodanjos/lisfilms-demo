import { Link } from 'react-router-dom'
import { MediaCard, Poster, SectionHeading } from '../components/ui'
import { currentUser, media } from '../data/mock'

const featured = media.filter((m) => m.featured)
const popular = [...media].sort((a, b) => b.communityRating - a.communityRating).slice(0, 8)
const recommended = media
  .filter((m) => m.genres.some((g) => currentUser.favoriteGenres.includes(g)))
  .slice(0, 8)
const recent = [...media].sort((a, b) => b.year - a.year).slice(0, 8)

export default function Home() {
  const hero = featured[0]

  return (
    <div className="flex flex-col gap-10">
      {hero && (
        <section className="relative overflow-hidden rounded-2xl border border-border">
          <div
            className="absolute inset-0"
            style={{ backgroundImage: `linear-gradient(120deg, ${hero.gradient[0]}33 0%, transparent 60%)` }}
          />
          <div className="relative flex flex-col gap-6 p-6 md:flex-row md:items-center md:p-10">
            <Poster media={hero} className="w-40 shrink-0 md:w-56" />
            <div className="min-w-0">
              <p className="text-xs font-bold tracking-wide text-accent uppercase">Em destaque</p>
              <h1 className="mt-2 text-3xl font-extrabold text-text md:text-4xl">{hero.title}</h1>
              <p className="mt-3 max-w-xl text-sm text-muted md:text-base">{hero.synopsis}</p>
              <div className="mt-5 flex flex-wrap gap-3">
                <Link
                  to={`/titulo/${hero.id}`}
                  className="rounded-full bg-accent px-5 py-2.5 text-sm font-semibold text-black transition-colors hover:bg-accent-hover"
                >
                  Ver detalhes
                </Link>
                <Link
                  to="/descobrir"
                  className="rounded-full border border-border bg-card px-5 py-2.5 text-sm font-semibold text-text transition-colors hover:border-border-strong"
                >
                  Explorar mais
                </Link>
              </div>
            </div>
          </div>
        </section>
      )}

      <section>
        <SectionHeading title={`Bem-vindo de volta, ${currentUser.name.split(' ')[0]}`} subtitle="Sugestões com base nos teus géneros favoritos" />
        <Row items={recommended} />
      </section>

      <section>
        <SectionHeading title="Populares na comunidade" subtitle="Os títulos mais bem avaliados por quem usa a LisFilms" />
        <Row items={popular} />
      </section>

      <section>
        <SectionHeading title="Adicionados recentemente" />
        <Row items={recent} />
      </section>
    </div>
  )
}

function Row({ items }: { items: typeof media }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
      {items.map((item) => (
        <MediaCard key={item.id} item={item} />
      ))}
    </div>
  )
}
