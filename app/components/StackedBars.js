"use client";

const STEP = { Sufficient: "var(--ord-3)", Somewhat: "var(--ord-2)", Inadequate: "var(--ord-1)" };
const TEXT = { Sufficient: "var(--ord-t3)", Somewhat: "var(--ord-t2)", Inadequate: "var(--ord-t1)" };

export default function StackedBars({ items, levels }) {
  return (
    <div>
      <div className="stack-legend">
        {levels.map((lv) => (
          <span key={lv}>
            <i style={{ background: STEP[lv] }} />
            {lv}
          </span>
        ))}
      </div>
      {items.map((item) => {
        const total = item.levels.reduce((a, l) => a + l.value, 0) || 1;
        return (
          <div className="stack-row" key={item.label}>
            <span className="stack-name">{item.label}</span>
            <div className="stack-track">
              {item.levels.map((l) =>
                l.value ? (
                  <div
                    key={l.level}
                    className="stack-seg"
                    style={{ width: `${(l.value / total) * 100}%`, background: STEP[l.level], color: TEXT[l.level] }}
                    title={`${item.label}: ${l.level}, ${l.value} of ${total} (${Math.round((l.value / total) * 100)}%)`}
                  >
                    {l.value}
                  </div>
                ) : null
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
