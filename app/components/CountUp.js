"use client";

import { useEffect, useRef, useState } from "react";

// Animates between values when the cohort filter changes; the first render
// shows the real number so the static page reads correctly without JavaScript.
export default function CountUp({ value, decimals = 0 }) {
  const [shown, setShown] = useState(value ?? 0);
  const from = useRef(value ?? 0);

  useEffect(() => {
    if (value == null) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setShown(value);
      from.current = value;
      return;
    }
    const start = from.current;
    const t0 = performance.now();
    let raf;
    const tick = (t) => {
      const p = Math.min(1, (t - t0) / 600);
      const v = start + (value - start) * (1 - Math.pow(1 - p, 3));
      setShown(v);
      from.current = v;
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value]);

  return value == null ? "–" : shown.toFixed(decimals);
}
