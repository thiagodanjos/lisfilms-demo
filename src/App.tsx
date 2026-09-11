import { Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import Catalog from './pages/Catalog'
import Discover from './pages/Discover'
import Feed from './pages/Feed'
import Home from './pages/Home'
import MediaDetail from './pages/MediaDetail'
import NotFound from './pages/NotFound'
import Profile from './pages/Profile'
import Search from './pages/Search'
import Watchlist from './pages/Watchlist'

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/catalogo" element={<Catalog />} />
        <Route path="/titulo/:id" element={<MediaDetail />} />
        <Route path="/feed" element={<Feed />} />
        <Route path="/descobrir" element={<Discover />} />
        <Route path="/watchlist" element={<Watchlist />} />
        <Route path="/pesquisa" element={<Search />} />
        <Route path="/perfil/:username" element={<Profile />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AppShell>
  )
}
