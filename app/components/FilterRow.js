"use client";

export default function FilterRow({ years, active, onChange }) {
  return (
    <div className="filter-row">
      <span className="filter-label">Graduating cohort</span>
      <button className="chip" data-active={active === "All"} onClick={() => onChange("All")}>
        All years
      </button>
      {years.map((y) => (
        <button key={y} className="chip" data-active={active === y} onClick={() => onChange(y)}>
          {y}
        </button>
      ))}
    </div>
  );
}
