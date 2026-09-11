export type MediaType = 'filme' | 'serie'

export interface Media {
  id: string
  type: MediaType
  title: string
  year: number
  genres: string[]
  synopsis: string
  director: string
  cast: string[]
  runtime?: string
  seasons?: number
  communityRating: number
  criticScore: number
  gradient: [string, string]
  featured?: boolean
}

export interface DemoUser {
  id: string
  name: string
  username: string
  bio: string
  color: string
  favoriteGenres: string[]
  followers: number
  following: number
  joined: string
}

export interface Review {
  id: string
  mediaId: string
  userId: string
  rating: number
  text: string
  date: string
  likes: number
}

export interface FeedItem {
  id: string
  userId: string
  mediaId: string
  reviewId?: string
  kind: 'review' | 'watchlist' | 'rating'
  date: string
}
