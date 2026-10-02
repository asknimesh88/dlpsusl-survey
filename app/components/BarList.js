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

export default function BarList({ items, total, color, max, unit = "" }) {
  const items_ = items || [];
  const denom = max || Math.max(1, ...items_.map((i) => i.value));

  return (
    <div className="bar-list">
      {items_.map((item, i) => {
        const pct = total ? Math.round((item.value / total) * 100) : null;
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
