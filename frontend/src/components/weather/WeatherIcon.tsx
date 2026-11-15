import { cn } from '@/lib/utils'
import type { Weather } from '@/types'

const ICONS_URL = 'https://cdn.meteocons.com/3.0.0-next.10/svg/line'

interface WeatherIconProps {
  weather: Weather
  /** Tamanho do círculo (classes `size-*`) */
  className?: string
}

// Círculo escuro: as nuvens dos ícones são quase brancas e sumiam no fundo claro do card.
export default function WeatherIcon({ weather, className }: Readonly<WeatherIconProps>) {
  return (
    <span className={cn('grid shrink-0 place-items-center rounded-full bg-ink', className)}>
      <img
        src={`${ICONS_URL}/${weather.iconSlug}.svg`}
        alt={weather.condition}
        loading="lazy"
        width="64"
        height="64"
        className="size-4/5"
      />
    </span>
  )
}
