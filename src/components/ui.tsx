import { Star } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { Media } from '../data/types'
import { cn, initials } from '../lib/utils'

export function Logo({ size = 'md', className }: { size?: 'sm' | 'md' | 'lg'; className?: string }) {
  const text = { sm: 'text-lg', md: 'text-2xl', lg: 'text-4xl' }[size]
  const dot = { sm: 'size-2', md: 'size-3', lg: 'size-4' }[size]
  return (
    <div className={cn('flex items-center gap-2 select-none', className)}>
      <span className={cn('rounded-full bg-accent shadow-glow', dot)} />
      <span className={cn('font-extrabold tracking-tight leading-none', text)}>
        <span className="text-text">Lis</span>
        <span className="text-accent">Films</span>
      </span>
    </div>
  )
}

export function Badge({ children, tone = 'default' }: { children: React.ReactNode; tone?: 'default' | 'accent' | 'gold' }) {
  const styles = {
    default: 'bg-card border-border text-muted',
    accent: 'bg-accent-soft border-accent/40 text-accent',
    gold: 'bg-gold/10 border-gold/40 text-gold',
  }[tone]
  return (
    <span className={cn('inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-semibold', styles)}>
      {children}
    </span>
  )
}

export function Avatar({ name, color, size = 'md' }: { name: string; color: string; size?: 'sm' | 'md' | 'lg' }) {
  const dims = { sm: 'size-8 text-xs', md: 'size-10 text-sm', lg: 'size-20 text-2xl' }[size]
  return (
    <div
      className={cn('flex shrink-0 items-center justify-center rounded-full font-bold text-black', dims)}
      style={{ backgroundColor: color }}
    >
      {initials(name)}
    </div>
  )
}

export function StarRating({ value, outOf = 5, size = 14 }: { value: number; outOf?: number; size?: number }) {
  return (
    <div className="flex items-center gap-0.5" aria-label={`${value} de ${outOf} estrelas`}>
      {Array.from({ length: outOf }).map((_, i) => {
        const filled = i + 1 <= Math.round(value)
        return (
          <Star
            key={i}
            size={size}
            className={filled ? 'fill-gold text-gold' : 'text-border-strong'}
          />
        )
      })}
    </div>
  )
}

export function Poster({
  media,
  className,
  compact = false,
}: {
  media: Media
  className?: string
  /** versão sem badge/texto, para miniaturas pequenas (feed, rankings) */
  compact?: boolean
}) {
  const [from, to] = media.gradient
  return (
    <div
      className={cn('relative flex aspect-2/3 w-full flex-col justify-end overflow-hidden rounded-xl', compact ? 'p-1.5' : 'p-3', className)}
      style={{ backgroundImage: `linear-gradient(155deg, ${from} 0%, ${to} 100%)` }}
    >
      <div className="absolute inset-0 bg-black/10" />
      {!compact && (
        <>
          <div className="absolute top-2 right-2 rounded-full bg-black/40 px-2 py-0.5 text-[10px] font-bold text-white backdrop-blur-sm">
            {media.type === 'filme' ? 'Filme' : 'Série'}
          </div>
          <span className="relative text-xs font-medium text-white/80">{media.year}</span>
          <span className="relative text-lg leading-tight font-extrabold text-white drop-shadow-sm">{media.title}</span>
        </>
      )}
      {compact && (
        <span className="relative line-clamp-3 text-[10px] leading-tight font-bold text-white drop-shadow-sm">{media.title}</span>
      )}
    </div>
  )
}

export function MediaCard({ item }: { item: Media }) {
  return (
    <Link to={`/titulo/${item.id}`} className="group flex flex-col gap-2">
      <Poster media={item} className="shadow-card transition-transform group-hover:scale-[1.02]" />
      <div className="flex items-center justify-between gap-2">
        <span className="truncate text-sm font-semibold text-text group-hover:text-accent">{item.title}</span>
      </div>
      <div className="flex items-center gap-1 text-xs text-muted">
        <Star size={12} className="fill-gold text-gold" />
        {item.communityRating.toFixed(1)}
      </div>
    </Link>
  )
}

export function SectionHeading({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-4">
      <h2 className="text-xl font-bold text-text">{title}</h2>
      {subtitle && <p className="mt-0.5 text-sm text-muted">{subtitle}</p>}
    </div>
  )
}

export function DemoBanner() {
  return (
    <div className="border-b border-accent/20 bg-accent-soft px-4 py-2 text-center text-xs font-medium text-accent sm:px-6">
      Isto é uma demonstração com dados fictícios — não há backend nem contas reais.{' '}
      <a
        href="https://github.com/thiagodanjos/lisfilms-demo"
        target="_blank"
        rel="noreferrer"
        className="underline underline-offset-2 hover:text-accent-hover"
      >
        Ver código no GitHub
      </a>
    </div>
  )
}
