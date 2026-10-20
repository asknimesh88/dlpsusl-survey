"use client";

const SLOTS = [
  "var(--series-1)",
  "var(--series-2)",
  "var(--series-3)",
  "var(--series-4)",
  "var(--series-5)",
  "var(--series-6)",
  "var(--series-7)",
  "var(--series-8)",
];

// Percentages of the same whole must add to exactly 100 on screen, or a reader
// checking the column is right to distrust it. Rounding each share on its own
// lands on 99 or 101 often enough to matter, so the rounding error is handed to
// the rows with the largest fractions until the column balances.
//
// Only applied when the rows actually partition the total. A question where
// graduates could tick several answers has rows summing past the total, and
// there each percentage is a share of all graduates, not of all the ticks.
function sharePercents(values, total) {
  if (!total) return values.map(() => null);
  const exact = values.map((v) => (v / total) * 100);
  if (values.reduce((a, b) => a + b, 0) !== total) return exact.map((p) => Math.round(p));

  const out = exact.map((p) => Math.floor(p));
  const spare = 100 - out.reduce((a, b) => a + b, 0);
  const byRemainder = exact
    .map((p, i) => ({ frac: p - Math.floor(p), i }))
    .sort((a, b) => b.frac - a.frac);
  for (let k = 0; k < spare && k < byRemainder.length; k += 1) out[byRemainder[k].i] += 1;
  return out;
}

export default function BarList({ items, total, color, max, unit = "" }) {
  const items_ = items || [];
  const denom = max || Math.max(1, ...items_.map((i) => i.value));
  const percents = sharePercents(
    items_.map((i) => i.value),
    total
  );

  return (
    <div className="bar-list">
      {items_.map((item, i) => {
        const pct = percents[i];
        const fill = color || SLOTS[i % SLOTS.length];
        return (
          <div className="bar-row-full" key={item.label}>
            <div className="bar-row-label">
              <span className="bar-row-name">{item.label}</span>
              <span className="bar-row-count">
                {item.value}
                {unit}
                {pct !== null ? ` · ${pct}%` : ""}
              </span>
            </div>
            <div
              className="bar-track"
              title={pct !== null ? `${item.label}: ${item.value} (${pct}%)` : `${item.label}: ${item.value}`}
            >
              <div
                className="bar-fill"
                style={{ width: `${(item.value / denom) * 100}%`, background: fill }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
