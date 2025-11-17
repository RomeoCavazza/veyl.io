import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { formatDistanceToNow } from "date-fns";
import { fr } from "date-fns/locale";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Formate un nombre avec séparateurs de milliers
 * Exemples: 1000 -> "1,000" | 1000000 -> "1,000,000"
 */
export function formatNumber(num: number | undefined | null): string {
  if (num === undefined || num === null) return '0';
  return num.toLocaleString();
}

/**
 * Formate un nombre de manière compacte (K, M)
 * Exemples: 1000 -> "1.0K" | 1000000 -> "1.0M"
 */
export function formatCompactNumber(num: number | undefined | null): string {
  if (!num) return '0';
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}

/**
 * Formate une date en temps relatif (ex: "il y a 2 heures")
 */
export function formatRelativeTime(date: string | Date | undefined | null, locale: 'fr' | 'en' = 'fr'): string {
  if (!date) return '';
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  if (isNaN(dateObj.getTime())) return '';
  return formatDistanceToNow(dateObj, { addSuffix: true, locale: locale === 'fr' ? fr : undefined });
}

/**
 * Formate une date en format court (ex: "Jan 15, 2024")
 */
export function formatShortDate(date: string | Date | undefined | null, locale: string = 'en-US'): string {
  if (!date) return '';
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  if (isNaN(dateObj.getTime())) return '';
  return dateObj.toLocaleDateString(locale, { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Formate une date en format complet (ex: "January 15, 2024")
 */
export function formatFullDate(date: string | Date | undefined | null, locale: string = 'en-US'): string {
  if (!date) return '';
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  if (isNaN(dateObj.getTime())) return '';
  return dateObj.toLocaleDateString(locale, { month: 'long', day: 'numeric', year: 'numeric' });
}

/**
 * Formate une date pour les graphiques (ex: "Jan 15")
 */
export function formatChartDate(date: string | Date | undefined | null, locale: string = 'en-US'): string {
  if (!date) return '';
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  if (isNaN(dateObj.getTime())) return '';
  return dateObj.toLocaleDateString(locale, { month: 'short', day: 'numeric' });
}

/**
 * Extrait le message d'erreur de manière sûre depuis un objet error inconnu
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  if (error && typeof error === 'object' && 'message' in error) {
    return String(error.message);
  }
  return 'An unknown error occurred';
}
