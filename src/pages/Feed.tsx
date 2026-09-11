import { Link } from 'react-router-dom'
import { Avatar, Poster, SectionHeading, StarRating } from '../components/ui'
import { feed, mediaById, reviews, userById } from '../data/mock'
import { formatRelativeDate } from '../lib/utils'

export default function Feed() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-4">
      <SectionHeading title="Feed" subtitle="Atividade recente de quem usa a LisFilms" />

      {feed.map((item) => {
        const user = userById(item.userId)
        const item_media = mediaById(item.mediaId)
        const review = reviews.find((r) => r.id === item.reviewId)
        if (!user || !item_media || !review) return null

        return (
          <div key={item.id} className="flex gap-3 rounded-xl border border-border bg-card p-4">
            <Link to={`/perfil/${user.username}`}>
              <Avatar name={user.name} color={user.color} />
            </Link>
            <div className="min-w-0 flex-1">
              <p className="text-sm text-text">
                <Link to={`/perfil/${user.username}`} className="font-semibold hover:text-accent">
                  {user.name}
                </Link>{' '}
                avaliou{' '}
                <Link to={`/titulo/${item_media.id}`} className="font-semibold hover:text-accent">
                  {item_media.title}
                </Link>
              </p>
              <div className="mt-1 flex items-center gap-2">
                <StarRating value={review.rating} size={12} />
                <span className="text-xs text-muted">{formatRelativeDate(item.date)}</span>
              </div>
              <p className="mt-2 text-sm text-muted">{review.text}</p>
            </div>
            <Link to={`/titulo/${item_media.id}`} className="hidden w-16 shrink-0 sm:block">
              <Poster media={item_media} compact />
            </Link>
          </div>
        )
      })}
    </div>
  )
}
