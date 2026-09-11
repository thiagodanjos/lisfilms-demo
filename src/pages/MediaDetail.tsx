import { useState } from 'react'
import { Bookmark, Heart, Star } from 'lucide-react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { Avatar, Badge, Poster, StarRating } from '../components/ui'
import { currentUser, mediaById, reviewsForMedia, userById } from '../data/mock'
import { useDemoStore } from '../store/demo'
import { cn, formatRelativeDate } from '../lib/utils'

export default function MediaDetail() {
  const { id = '' } = useParams()
  const item = mediaById(id)
  const { watchlist, toggleWatchlist, likedReviews, toggleLike, localReviews, addReview } = useDemoStore()

  const [rating, setRating] = useState(5)
  const [text, setText] = useState('')

  if (!item) return <Navigate to="/catalogo" replace />

  const reviews = reviewsForMedia(id)
  const mine = localReviews.filter((r) => r.mediaId === id)
  const inWatchlist = watchlist.includes(id)

  function submitReview(e: React.FormEvent) {
    e.preventDefault()
    if (!text.trim()) return
    addReview(id, rating, text.trim())
    setText('')
  }

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-8">
      <div className="flex flex-col gap-6 sm:flex-row">
        <Poster media={item} className="w-40 shrink-0 sm:w-52" />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            {item.genres.map((g) => (
              <Badge key={g}>{g}</Badge>
            ))}
          </div>
          <h1 className="mt-2 text-3xl font-extrabold text-text">{item.title}</h1>
          <p className="mt-1 text-sm text-muted">
            {item.year} · {item.type === 'filme' ? item.runtime : `${item.seasons} temporadas`} · {item.director}
          </p>

          <div className="mt-4 flex flex-wrap items-center gap-6">
            <div>
              <p className="text-xs font-semibold tracking-wide text-faint uppercase">LisFilms</p>
              <div className="mt-1 flex items-center gap-2">
                <StarRating value={item.communityRating} />
                <span className="text-sm font-semibold text-text">{item.communityRating.toFixed(1)} / 5</span>
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold tracking-wide text-faint uppercase">Crítica</p>
              <p className="mt-1 text-sm font-semibold text-text">{item.criticScore.toFixed(1)} / 10</p>
            </div>
          </div>

          <p className="mt-5 max-w-2xl text-sm leading-relaxed text-muted">{item.synopsis}</p>
          <p className="mt-3 text-sm text-muted">
            <span className="font-semibold text-text">Elenco: </span>
            {item.cast.join(', ')}
          </p>

          <button
            onClick={() => toggleWatchlist(id)}
            className={cn(
              'mt-5 inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-semibold transition-colors',
              inWatchlist
                ? 'border-accent bg-accent-soft text-accent'
                : 'border-border bg-card text-text hover:border-border-strong',
            )}
          >
            <Bookmark size={16} className={inWatchlist ? 'fill-accent' : ''} />
            {inWatchlist ? 'Na watchlist' : 'Adicionar à watchlist'}
          </button>
        </div>
      </div>

      <section>
        <h2 className="mb-3 text-lg font-bold text-text">
          Reviews da comunidade <span className="text-muted">({reviews.length + mine.length})</span>
        </h2>

        <form onSubmit={submitReview} className="mb-6 rounded-xl border border-border bg-card p-4">
          <div className="flex items-center gap-3">
            <Avatar name={currentUser.name} color={currentUser.color} size="sm" />
            <span className="text-sm font-semibold text-text">{currentUser.name}</span>
            <div className="ml-auto flex items-center gap-1">
              {Array.from({ length: 5 }).map((_, i) => (
                <button key={i} type="button" onClick={() => setRating(i + 1)}>
                  <Star size={18} className={i < rating ? 'fill-gold text-gold' : 'text-border-strong'} />
                </button>
              ))}
            </div>
          </div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={`O que achaste de "${item.title}"?`}
            rows={3}
            className="mt-3 w-full resize-none rounded-lg border border-border bg-raised p-3 text-sm text-text placeholder:text-faint focus:border-accent focus:outline-none"
          />
          <div className="mt-2 flex justify-end">
            <button
              type="submit"
              disabled={!text.trim()}
              className="rounded-full bg-accent px-4 py-1.5 text-sm font-semibold text-black transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-40"
            >
              Publicar review
            </button>
          </div>
        </form>

        <div className="flex flex-col gap-4">
          {mine.map((r) => (
            <div key={r.id} className="rounded-xl border border-accent/30 bg-accent-soft/40 p-4">
              <div className="flex items-center gap-3">
                <Avatar name={currentUser.name} color={currentUser.color} size="sm" />
                <div>
                  <p className="text-sm font-semibold text-text">{currentUser.name}</p>
                  <p className="text-xs text-muted">agora mesmo</p>
                </div>
                <div className="ml-auto">
                  <StarRating value={r.rating} size={12} />
                </div>
              </div>
              <p className="mt-3 text-sm text-text">{r.text}</p>
            </div>
          ))}

          {reviews.map((r) => {
            const author = userById(r.userId)
            if (!author) return null
            const liked = likedReviews.includes(r.id)
            return (
              <div key={r.id} className="rounded-xl border border-border bg-card p-4">
                <div className="flex items-center gap-3">
                  <Link to={`/perfil/${author.username}`}>
                    <Avatar name={author.name} color={author.color} size="sm" />
                  </Link>
                  <div className="min-w-0">
                    <Link to={`/perfil/${author.username}`} className="text-sm font-semibold text-text hover:text-accent">
                      {author.name}
                    </Link>
                    <p className="text-xs text-muted">{formatRelativeDate(r.date)}</p>
                  </div>
                  <div className="ml-auto">
                    <StarRating value={r.rating} size={12} />
                  </div>
                </div>
                <p className="mt-3 text-sm text-text">{r.text}</p>
                <button
                  onClick={() => toggleLike(r.id)}
                  className={cn(
                    'mt-3 inline-flex items-center gap-1.5 text-xs font-medium transition-colors',
                    liked ? 'text-danger' : 'text-muted hover:text-text',
                  )}
                >
                  <Heart size={14} className={liked ? 'fill-danger' : ''} />
                  {r.likes + (liked ? 1 : 0)}
                </button>
              </div>
            )
          })}
        </div>
      </section>
    </div>
  )
}
