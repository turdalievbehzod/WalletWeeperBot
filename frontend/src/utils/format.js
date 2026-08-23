/**
 * Formats a number with spaces as thousand separators, rounded to 2 decimal
 * places. Whole numbers show no decimal part (e.g. UZS); fractional amounts
 * (e.g. small USD/EUR values) keep their decimals instead of being truncated.
 * 550000 → "550 000"   1.554 → "1.55"
 */
export const fmtAmount = n => {
  const rounded = Math.round(Number(n) * 100) / 100
  const [intPart, decPart] = rounded.toFixed(2).split('.')
  const withSep = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '\xa0')
  return decPart === '00' ? withSep : `${withSep}.${decPart}`
}

/**
 * Live-formats a raw numeric string being typed into an amount input —
 * groups the integer part with thousand separators, leaves an in-progress
 * decimal part untouched so the user can keep typing after the dot.
 * '550000' → '550 000'   '1234.5' → '1 234.5'   '' → ''
 */
export const formatAmountInput = raw => {
  if (!raw) return ''
  const [intPart, decPart] = String(raw).split('.')
  const grouped = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '\xa0')
  return decPart !== undefined ? `${grouped}.${decPart}` : grouped
}

/** Strips an amount input's raw value down to digits + at most one dot. */
export const cleanAmountInput = value => {
  const cleaned = value.replace(/[^\d.]/g, '')
  const dot = cleaned.indexOf('.')
  return dot === -1 ? cleaned : cleaned.slice(0, dot + 1) + cleaned.slice(dot + 1).replace(/\./g, '')
}
