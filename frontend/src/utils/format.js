/**
 * Formats a number with spaces as thousand separators.
 * 550000 → "550 000"
 */
export const fmtAmount = n =>
  Math.round(Number(n))
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
