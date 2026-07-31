import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function fmtDate(iso?: string | null) {
  if (!iso) return "";
  return new Date(iso).toLocaleString("pt-BR");
}
