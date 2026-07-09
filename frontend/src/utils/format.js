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
