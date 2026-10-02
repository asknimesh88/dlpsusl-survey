"use client";

// Horizontal bars diverging from the neutral midpoint of a 1-5 rating scale.
export default function DivergeList({ items, mid = 3, scaleMax = 2 }) {
  return (
    <div>
      {items.map((c) => {
        const delta = c.average - mid;
        const widthPct = (Math.abs(delta) / scaleMax) * 50;
        const positive = delta >= 0;
        return (
          <div className="diverge-row" key={c.id}>
            <span className="diverge-name" title={c.title}>
              {c.title}
            </span>
            <div className="diverge-track">
              <div className="diverge-mid" />
              <div
                className="diverge-fill"
                style={{
                  width: `${widthPct}%`,
                  left: positive ? "50%" : `${50 - widthPct}%`,
                  background: positive ? "var(--good)" : "var(--critical)",
                }}
                title={`${c.title}: ${c.average.toFixed(2)} avg`}
              />
            </div>
            <span className="diverge-score">{c.average.toFixed(2)}</span>
          </div>
        );
      })}
    </div>
  );
}
