import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface LocalReview {
  id: string
  mediaId: string
  rating: number
  text: string
  date: string
}

interface DemoState {
  watchlist: string[]
  likedReviews: string[]
  localReviews: LocalReview[]
  toggleWatchlist: (mediaId: string) => void
  toggleLike: (reviewId: string) => void
  addReview: (mediaId: string, rating: number, text: string) => void
  reset: () => void
}

// Estado guardado apenas no localStorage do teu browser — é o que torna esta
// demonstração interativa sem existir qualquer servidor por trás.
export const useDemoStore = create<DemoState>()(
  persist(
    (set) => ({
      watchlist: [],
      likedReviews: [],
      localReviews: [],
      toggleWatchlist: (mediaId) =>
        set((s) => ({
          watchlist: s.watchlist.includes(mediaId)
            ? s.watchlist.filter((id) => id !== mediaId)
            : [...s.watchlist, mediaId],
        })),
      toggleLike: (reviewId) =>
        set((s) => ({
          likedReviews: s.likedReviews.includes(reviewId)
            ? s.likedReviews.filter((id) => id !== reviewId)
            : [...s.likedReviews, reviewId],
        })),
      addReview: (mediaId, rating, text) =>
        set((s) => ({
          localReviews: [
            {
              id: `local-${Date.now()}`,
              mediaId,
              rating,
              text,
              date: new Date().toISOString().slice(0, 10),
            },
            ...s.localReviews,
          ],
        })),
      reset: () => set({ watchlist: [], likedReviews: [], localReviews: [] }),
    }),
    { name: 'lisfilms-demo' },
  ),
)
