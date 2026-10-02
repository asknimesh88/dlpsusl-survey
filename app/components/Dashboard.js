"use client";

import { useMemo, useState } from "react";
import BarList from "./BarList";
import DivergeList from "./DivergeList";
import FilterRow from "./FilterRow";
import StackedBars from "./StackedBars";
import ThemeToggle from "./ThemeToggle";
import { ACTIVITY_LEVELS, TEXT_QUESTIONS, aggregate, filterByYear, years as yearsOf } from "../lib/aggregate";

function Tags({ items, warn }) {
  return (
    <div className="tag-row">
      {items.map((f) => (
        <span className="tag" key={f.label} style={warn ? { borderColor: "var(--clay)" } : undefined}>
          <b>{f.value}</b> {f.label}
        </span>
      ))}
    </div>
  );
}

function Section({ title, note, children }) {
  return (
    <section className="section">
      <div className="section-head">
        <h2>{title}</h2>
        {note && <span className="section-note">{note}</span>}
      </div>
      {children}
    </section>
  );
}

const Panel = ({ title, children }) => (
  <div className="panel">
    <h3>{title}</h3>
    {children}
  </div>
);

export default function Dashboard({ records, courseColumns }) {
  const [year, setYear] = useState("All");

  const allYears = useMemo(() => yearsOf(records), [records]);
  const filtered = useMemo(() => filterByYear(records, year), [records, year]);
  const d = useMemo(() => aggregate(filtered, courseColumns), [filtered, courseColumns]);

  const tooShort = d.trainingDuration.find((t) => t.label === "Too short")?.value ?? 0;

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
              {d.jobSkills ?? "–"}
              <span className="stat-unit">/5</span>
            </span>
            <div className="stat-label">Job-related skills gained</div>
          </div>
          <div className="stat">
            <span className="stat-figure">{d.n}</span>
            <div className="stat-label">Responses in this view</div>
          </div>
        </section>

        <Section title="Who answered" note="Questions 1 to 4, 10 and 11: graduation year, degree class, sector and further study">
          <div className="grid-2">
            <Panel title="Graduation year">
              <BarList items={d.gradYear} total={d.n} color="var(--series-1)" />
            </Panel>
            <Panel title="Final classification">
              <BarList items={d.finalResult} total={d.n} color="var(--series-3)" />
            </Panel>
          </div>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <Panel title="Current employment sector">
              <BarList items={d.sector} total={d.n} color="var(--series-2)" />
            </Panel>
            <Panel title="Field of expertise">
              <Tags items={d.fieldExpertise} />
            </Panel>
          </div>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <Panel title="Started postgraduate or professional studies?">
              <BarList items={d.postgrad} total={d.n} color="var(--series-7)" />
            </Panel>
            <Panel title="Highest academic qualification">
              <BarList items={d.qualification} total={d.n} color="var(--series-5)" />
            </Panel>
          </div>
        </Section>

        <Section title="Where it leads" note="Questions 5 to 9: roles, employers, time to first job and fit with the degree">
          <div className="grid-2">
            <Panel title="How closely their job matches the degree">
              <BarList items={d.jobRelatedness} total={d.n} color="var(--series-7)" />
            </Panel>
            <Panel title="Wait from graduation to first job">
              <BarList items={d.waitingPeriod} total={d.n} color="var(--series-5)" />
            </Panel>
          </div>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <Panel title="Time in employment so far">
              <BarList items={d.empDuration} total={d.n} color="var(--series-3)" />
            </Panel>
            <Panel title="Current roles">
              <Tags items={d.roles} />
            </Panel>
          </div>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <Panel title="Organizations graduates work for">
              <Tags items={d.companies} />
            </Panel>
            <Panel title="Previous roles">
              <Tags items={d.prevRoles} />
            </Panel>
          </div>
          <p className="sub-note">Roles and organizations are listed separately, so no role is tied to a particular employer.</p>
        </Section>

        <Section title="Did the curriculum do its job?" note="Questions 13, 26 to 28, 30, 38 and 41 to 42. Ratings run 1 to 5">
          <Panel title="Average rating (1 = not well, 5 = extremely well)">
            <BarList items={d.curriculumFit} color="var(--series-1)" max={5} unit=" / 5" />
          </Panel>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <Panel title="Were expectations met?">
              <BarList items={d.expectationsMet} total={d.n} color="var(--series-6)" />
            </Panel>
            <Panel title="Would they recommend it?">
              <BarList items={d.recommend} total={d.n} color="var(--series-3)" />
            </Panel>
          </div>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <Panel title="Compared to similar programmes">
              <BarList items={d.comparedSimilar} total={d.n} color="var(--series-6)" />
            </Panel>
            <Panel title="Any subjects outdated or less useful?">
              <BarList items={d.outdated} total={d.n} color="var(--series-4)" />
            </Panel>
          </div>
        </Section>

        <Section title="Course by course" note={`Questions 13 to 15: all ${d.coreCourses.length + d.compulsoryCourses.length + d.electiveCourses.length} courses, average rating, centred on the scale midpoint (3)`}>
          <div className="grid-2">
            <Panel title={`Core courses (${d.coreCourses.length})`}>
              <DivergeList items={d.coreCourses} />
            </Panel>
            <Panel title={`Elective specialization (${d.electiveCourses.length})`}>
              <DivergeList items={d.electiveCourses} />
            </Panel>
          </div>
          <div className="panel" style={{ marginTop: 32 }}>
            <h3>Compulsory specialization ({d.compulsoryCourses.length})</h3>
            <DivergeList items={d.compulsoryCourses} />
          </div>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <Panel title="Average by course group">
              <BarList items={d.courseByCategory} color="var(--series-6)" max={5} unit=" / 5" />
            </Panel>
            <Panel title="Most useful in their careers (times named)">
              <BarList items={d.usefulCourses} color="var(--series-2)" />
              <p className="sub-note">Counted from the courses graduates named in their own words.</p>
            </Panel>
          </div>
        </Section>

        <Section title="Teaching, training & assessment" note={`Questions 16 to 25 and 33 to 34. ${tooShort} of ${d.n} called the training period too short`}>
          <Panel title="How adequate were these learning activities?">
            <StackedBars items={d.activities} levels={ACTIVITY_LEVELS} />
          </Panel>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <Panel title="Teaching methods (1 to 5)">
              <BarList items={d.teaching} color="var(--series-1)" max={5} unit=" / 5" />
            </Panel>
            <Panel title="Assessment methods (1 to 5)">
              <BarList items={d.assessment} color="var(--series-7)" max={5} unit=" / 5" />
            </Panel>
          </div>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <Panel title="200-hour industrial training">
              <BarList items={d.trainingDuration} total={d.n} color="var(--series-4)" />
            </Panel>
            <Panel title="Was the exam system effective?">
              <BarList items={d.evalEffective} total={d.n} color="var(--series-3)" />
            </Panel>
          </div>
          <div className="grid-2" style={{ marginTop: 32 }}>
            <Panel title="Which assessment methods should be strengthened?">
              <BarList items={d.strengthen} total={d.n} color="var(--series-2)" />
            </Panel>
            <Panel title="Faced strict or challenging situations">
              <BarList items={d.facedChallenges} total={d.n} color="var(--series-8)" />
            </Panel>
          </div>
          <div className="panel" style={{ marginTop: 32 }}>
            <h3>Course structure felt flexible</h3>
            <BarList items={d.flexibility} total={d.n} color="var(--series-1)" />
          </div>
        </Section>

        <Section title="Strengths and weaknesses" note="Questions 39 and 40: what graduates chose from the list">
          <div className="grid-2">
            <Panel title="Key strengths">
              <BarList items={d.strengths} total={d.n} color="var(--series-6)" />
            </Panel>
            <Panel title="Areas to improve">
              <BarList items={d.improve} total={d.n} color="var(--series-8)" />
            </Panel>
          </div>
        </Section>

        <Section title="In their own words" note="Every written answer, grouped by question and listed alphabetically">
          <div>
            {TEXT_QUESTIONS.map(([q, label]) => (
              <details className="answers" key={q}>
                <summary>
                  {label}
                  <span className="answers-count">{d.texts[q].length}</span>
                </summary>
                <ul>
                  {d.texts[q].map((t, i) => (
                    <li key={i}>{t}</li>
                  ))}
                </ul>
              </details>
            ))}
          </div>
        </Section>

        <footer className="footer">
          Graduate Satisfaction Survey on the Curriculum &mdash; Animal Bio-Resource
          Technology and Management. {records.length} responses analysed; Aquatic
          Bio-Resource Management responses excluded from this view.
        </footer>
      </div>
    </>
  );
}
