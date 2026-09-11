import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-24 text-center">
      <p className="text-6xl font-extrabold text-accent">404</p>
      <p className="text-sm text-muted">Esta página não existe nesta demonstração.</p>
      <Link to="/" className="mt-2 rounded-full bg-accent px-5 py-2 text-sm font-semibold text-black hover:bg-accent-hover">
        Voltar ao início
      </Link>
    </div>
  )
}
