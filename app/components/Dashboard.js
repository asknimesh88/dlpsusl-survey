"use client";

import { useMemo, useState } from "react";
import BarList from "./BarList";
import DivergeList from "./DivergeList";
import FilterRow from "./FilterRow";
import ThemeToggle from "./ThemeToggle";
import { aggregate, filterByYear, years as yearsOf } from "../lib/aggregate";

export default function Dashboard({ records, courseColumns }) {
  const [year, setYear] = useState("All");

  const allYears = useMemo(() => yearsOf(records), [records]);
  const filtered = useMemo(() => filterByYear(records, year), [records, year]);
  const d = useMemo(() => aggregate(filtered, courseColumns), [filtered, courseColumns]);

  const quotes = useMemo(() => {
    const s = d.strengthQuotes.slice(0, 4).map((q) => ({ q, kind: "Key strength", weak: false }));
    const w = d.weaknessQuotes.slice(0, 4).map((q) => ({ q, kind: "Key weakness", weak: true }));
    const out = [];
    for (let i = 0; i < Math.max(s.length, w.length); i++) {
      if (s[i]) out.push(s[i]);
      if (w[i]) out.push(w[i]);
    }
    return out.slice(0, 8);
  }, [d]);

  return (
    <>
      <header className="masthead">
        <div className="wrap">
          <div className="masthead-top">
            <span>Curriculum review · Sabaragamuwa University of Sri Lanka</span>
            <span className="masthead-top-right">
              {records.length} graduates surveyed, 2022–2026
              <ThemeToggle />
            </span>
          </div>
          <h1>Animal Bio-Resource Technology &amp; Management, through its graduates&rsquo; eyes</h1>
          <p>
            Every response here comes from a graduate of the Animal Bio-Resource
            specialization &mdash; Aquatic Bio-Resource responses have been set aside so
            the curriculum committee is reading feedback on the track it actually owns.
          </p>
        </div>
      </header>

      <div className="wrap">
        <FilterRow years={allYears} active={year} onChange={setYear} />

        <section className="hero">
          <div className="stat hero-main">
            <span className="stat-figure">
              {d.overallExp ?? "–"}
              <span className="stat-unit">/5</span>
            </span>
            <div className="stat-label">Overall graduate experience</div>
          </div>
          <div className="stat">
            <span className="stat-figure">{d.recommendPct ?? "–"}%</span>
            <div className="stat-label">Would recommend the programme</div>
          </div>
          <div className="stat">
            <span className="stat-figure">
              {d.careerPrep ?? "–"}
              <span className="stat-unit">/5</span>
            </span>
            <div className="stat-label">Felt prepared for their career</div>
          </div>
          <div className="stat">
            <span className="stat-figure">{d.n}</span>
            <div className="stat-label">Responses in this view</div>
          </div>
        </section>

        {/* Cohort */}
        <section className="section">
          <div className="section-head">
            <h2>Who answered</h2>
            <span className="section-note">Graduation year, degree class and where they landed</span>
          </div>
          <div className="grid-2">
            <div className="panel">
              <h3>Graduation year</h3>
              <BarList items={d.gradYear} total={d.n} color="var(--series-1)" />
            </div>
            <div className="panel">
              <h3>Final classification</h3>
              <BarList items={d.finalResult} total={d.n} color="var(--series-3)" />
            </div>
          </div>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <div className="panel">
              <h3>Employment sector</h3>
              <BarList items={d.sector} total={d.n} color="var(--series-2)" />
            </div>
            <div className="panel">
              <h3>Field of expertise</h3>
              <div className="tag-row">
                {d.fieldExpertise.map((f) => (
                  <span className="tag" key={f.label}>
                    <b>{f.value}</b> {f.label}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Curriculum fit */}
        <section className="section">
          <div className="section-head">
            <h2>Did the curriculum do its job?</h2>
            <span className="section-note">Self-rated 1 (not well) to 5 (extremely well)</span>
          </div>
          <div className="panel">
            <BarList items={d.curriculumFit.map((c) => ({ label: c.label, value: c.value ?? 0 }))} color="var(--series-1)" max={5} unit=" / 5" />
          </div>
        </section>

        {/* Course ratings */}
        <section className="section">
          <div className="section-head">
            <h2>Course by course</h2>
            <span className="section-note">Average rating, centred on the scale midpoint (3)</span>
          </div>
          <div className="grid-2">
            <div className="panel">
              <h3>Rated lowest</h3>
              <DivergeList items={d.lowestCourses} />
            </div>
            <div className="panel">
              <h3>Rated highest</h3>
              <DivergeList items={d.highestCourses} />
            </div>
          </div>
          <div className="panel" style={{ marginTop: 32 }}>
            <h3>Average by course group</h3>
            <BarList
              items={d.courseByCategory.map((c) => ({ label: c.label, value: c.value ?? 0 }))}
              color="var(--series-6)"
              max={5}
              unit=" / 5"
            />
          </div>
        </section>

        {/* Industrial training & evaluation */}
        <section className="section">
          <div className="section-head">
            <h2>Industrial training &amp; assessment</h2>
            <span className="section-note">
              {d.trainingDuration.find((t) => t.label === "Too short")?.value ?? 0} of {d.n} called the training period too short
            </span>
          </div>
          <div className="grid-2">
            <div className="panel">
              <h3>200-hour industrial training</h3>
              <BarList items={d.trainingDuration} total={d.n} color="var(--series-4)" />
            </div>
            <div className="panel">
              <h3>Was the exam system effective?</h3>
              <BarList items={d.evalEffective} total={d.n} color="var(--series-3)" />
            </div>
          </div>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <div className="panel">
              <h3>Faced strict or challenging situations</h3>
              <BarList items={d.facedChallenges} total={d.n} color="var(--series-8)" />
            </div>
            <div className="panel">
              <h3>Course structure felt flexible</h3>
              <BarList items={d.flexibility} total={d.n} color="var(--series-1)" />
            </div>
          </div>
        </section>

        {/* Careers */}
        <section className="section">
          <div className="section-head">
            <h2>Where it leads</h2>
            <span className="section-note">Job relatedness and time to first employment</span>
          </div>
          <div className="grid-2">
            <div className="panel">
              <h3>How closely their job matches the degree</h3>
              <BarList items={d.jobRelatedness} total={d.n} color="var(--series-7)" />
            </div>
            <div className="panel">
              <h3>Wait from graduation to first job</h3>
              <BarList items={d.waitingPeriod} total={d.n} color="var(--series-5)" />
            </div>
          </div>
        </section>

        {/* Standing */}
        <section className="section">
          <div className="section-head">
            <h2>How the programme stacks up</h2>
            <span className="section-note">Against similar degrees, in graduates&rsquo; own words</span>
          </div>
          <div className="grid-2">
            <div className="panel">
              <h3>Compared to similar programmes</h3>
              <BarList items={d.comparedSimilar} total={d.n} color="var(--series-6)" />
            </div>
            <div className="panel">
              <h3>Strengths vs. areas to improve</h3>
              <div className="tag-row">
                {d.strengths.map((s) => (
                  <span className="tag" key={s.label}>
                    <b>{s.value}</b> {s.label}
                  </span>
                ))}
              </div>
              <div className="tag-row" style={{ marginTop: 10 }}>
                {d.improve.map((s) => (
                  <span className="tag" key={s.label} style={{ borderColor: "var(--clay)" }}>
                    <b>{s.value}</b> {s.label}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Quotes */}
        {quotes.length > 0 && (
          <section className="section">
            <div className="section-head">
              <h2>In their own words</h2>
              <span className="section-note">Short, unedited comments from this cohort</span>
            </div>
            <div className="quote-grid">
              {quotes.map((item, i) => (
                <div className={`quote${item.weak ? " weak" : ""}`} key={i}>
                  <span className="quote-kind">{item.kind}</span>
                  &ldquo;{item.q}&rdquo;
                </div>
              ))}
            </div>
          </section>
        )}

        <footer className="footer">
          Graduate Satisfaction Survey on the Curriculum &mdash; Animal Bio-Resource
          Technology and Management. {records.length} responses analysed; Aquatic
          Bio-Resource Management responses excluded from this view.
        </footer>
      </div>
    </>
  );
}
