import { Link } from 'react-router-dom'
import { Poster, SectionHeading, StarRating } from '../components/ui'
import { media } from '../data/mock'

const ranking = [...media].sort((a, b) => b.communityRating - a.communityRating)

const comingSoon = [
  { title: 'Areia Fina', year: 2027, genres: ['Drama'], gradient: ['#e0569b', '#330f24'] as [string, string] },
  { title: 'Circuito', year: 2027, genres: ['Ficção Científica', 'Ação'], gradient: ['#22a7ff', '#06263f'] as [string, string] },
  { title: 'Quarto 402', year: 2027, genres: ['Terror'], gradient: ['#f23f42', '#3a0a0c'] as [string, string] },
  { title: 'Última Ronda', year: 2028, genres: ['Comédia'], gradient: ['#ff8a3d', '#3a1d05'] as [string, string] },
]

export default function Discover() {
  return (
    <div className="flex flex-col gap-10">
      <section>
        <SectionHeading title="Top LisFilms" subtitle="Os títulos mais bem avaliados pela comunidade desta demonstração" />
        <ol className="flex flex-col gap-2">
          {ranking.map((item, i) => (
            <li key={item.id}>
              <Link
                to={`/titulo/${item.id}`}
                className="flex items-center gap-4 rounded-xl border border-border bg-card p-3 hover:border-border-strong"
              >
                <span className="w-6 shrink-0 text-center text-lg font-extrabold text-faint">{i + 1}</span>
                <div className="w-12 shrink-0">
                  <Poster media={item} compact />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold text-text">{item.title}</p>
                  <p className="truncate text-xs text-muted">
                    {item.year} · {item.genres.join(', ')}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <StarRating value={item.communityRating} size={12} />
                  <span className="text-xs font-semibold text-text">{item.communityRating.toFixed(1)}</span>
                </div>
              </Link>
            </li>
          ))}
        </ol>
      </section>

      <section>
        <SectionHeading title="Lançamentos brevemente" subtitle="Títulos fictícios só para ilustrar a secção — ainda não têm ficha própria" />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {comingSoon.map((item) => (
            <div key={item.title} className="flex flex-col gap-2 opacity-90">
              <div
                className="relative flex aspect-2/3 w-full flex-col justify-end overflow-hidden rounded-xl p-3"
                style={{ backgroundImage: `linear-gradient(155deg, ${item.gradient[0]} 0%, ${item.gradient[1]} 100%)` }}
              >
                <div className="absolute top-2 right-2 rounded-full bg-black/40 px-2 py-0.5 text-[10px] font-bold text-white backdrop-blur-sm">
                  Em breve
                </div>
                <span className="text-xs font-medium text-white/80">{item.year}</span>
                <span className="text-lg leading-tight font-extrabold text-white drop-shadow-sm">{item.title}</span>
              </div>
              <span className="truncate text-sm font-semibold text-text">{item.title}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
