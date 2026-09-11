import { Navigate, useParams } from 'react-router-dom'
import { Avatar, Badge, MediaCard, SectionHeading, StarRating } from '../components/ui'
import { currentUser, mediaById, reviewsByUser, users } from '../data/mock'
import { formatRelativeDate } from '../lib/utils'
import { useDemoStore } from '../store/demo'

export default function Profile() {
  const { username = '' } = useParams()
  const user = users.find((u) => u.username === username)
  const { watchlist } = useDemoStore()

  if (!user) return <Navigate to="/" replace />

  const isCurrent = user.id === currentUser.id
  const userReviews = reviewsByUser(user.id)
  const watchlistMedia = isCurrent ? watchlist.map((id) => mediaById(id)).filter(Boolean) : []

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-8">
      <div className="flex flex-col items-center gap-4 text-center sm:flex-row sm:items-start sm:text-left">
        <Avatar name={user.name} color={user.color} size="lg" />
        <div className="min-w-0">
          <h1 className="text-2xl font-extrabold text-text">{user.name}</h1>
          <p className="text-sm text-muted">
            @{user.username} · desde {user.joined}
          </p>
          <p className="mt-2 max-w-md text-sm text-text">{user.bio}</p>
          <div className="mt-3 flex flex-wrap justify-center gap-2 sm:justify-start">
            {user.favoriteGenres.map((g) => (
              <Badge key={g} tone="accent">
                {g}
              </Badge>
            ))}
          </div>
          <div className="mt-4 flex justify-center gap-6 text-sm sm:justify-start">
            <span>
              <b className="text-text">{userReviews.length}</b> <span className="text-muted">reviews</span>
            </span>
            <span>
              <b className="text-text">{user.followers}</b> <span className="text-muted">seguidores</span>
            </span>
            <span>
              <b className="text-text">{user.following}</b> <span className="text-muted">a seguir</span>
            </span>
          </div>
        </div>
      </div>

      {isCurrent && watchlistMedia.length > 0 && (
        <section>
          <SectionHeading title="A minha watchlist" />
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
            {watchlistMedia.map((m) => m && <MediaCard key={m.id} item={m} />)}
          </div>
        </section>
      )}

      <section>
        <SectionHeading title={`Reviews de ${user.name.split(' ')[0]}`} />
        {userReviews.length === 0 ? (
          <p className="text-sm text-muted">Ainda sem reviews.</p>
        ) : (
          <div className="flex flex-col gap-4">
            {userReviews.map((r) => {
              const item = mediaById(r.mediaId)
              if (!item) return null
              return (
                <div key={r.id} className="flex gap-3 rounded-xl border border-border bg-card p-4">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-text">{item.title}</p>
                    <div className="mt-1 flex items-center gap-2">
                      <StarRating value={r.rating} size={12} />
                      <span className="text-xs text-muted">{formatRelativeDate(r.date)}</span>
                    </div>
                    <p className="mt-2 text-sm text-muted">{r.text}</p>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>
    </div>
  )
}
