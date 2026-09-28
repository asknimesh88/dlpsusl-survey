// Pure aggregation over the raw (already Animal Bio-Resource-only) response
// records, re-run in the browser whenever the year filter changes.

function avg(nums) {
  const vals = nums.filter((v) => v !== null && v !== undefined);
  if (!vals.length) return null;
  return Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 100) / 100;
}

function counts(items) {
  const c = new Map();
  for (const item of items) {
    if (!item) continue;
    c.set(item, (c.get(item) || 0) + 1);
  }
  return [...c.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value);
}

function multiCounts(records, field) {
  return counts(records.flatMap((r) => r[field] || []));
}

export function filterByYear(records, year) {
  if (!year || year === "All") return records;
  return records.filter((r) => r.year === year);
}

export function years(records) {
  return [...new Set(records.map((r) => r.year))].sort();
}

export function aggregate(records, courseColumns) {
  const n = records.length;

  const courseAverages = courseColumns.map((c) => ({
    id: c.id,
    code: c.code,
    title: c.title,
    category: c.category,
    average: avg(records.map((r) => r.courses[c.id])),
  })).filter((c) => c.average !== null);

  const byCategory = ["core", "compulsory", "elective"].map((cat) => ({
    label: cat === "core" ? "Core courses" : cat === "compulsory" ? "Compulsory specialization" : "Elective specialization",
    value: avg(courseAverages.filter((c) => c.category === cat).map((c) => c.average)),
  }));

  const sorted = [...courseAverages].sort((a, b) => a.average - b.average);

  return {
    n,
    overallExp: avg(records.map((r) => r.overallExp)),
    jobSkills: avg(records.map((r) => r.jobSkills)),
    careerPrep: avg(records.map((r) => r.careerPrep)),
    recommendPct: n ? Math.round((records.filter((r) => r.recommend === "Yes").length / n) * 100) : null,

    gradYear: counts(records.map((r) => r.year)),
    finalResult: counts(records.map((r) => r.finalResult)),
    sector: multiCounts(records, "sector"),
    fieldExpertise: multiCounts(records, "fieldExpertise"),
    qualification: counts(records.map((r) => r.qualification)),
    postgrad: counts(records.map((r) => r.postgrad)),

    curriculumFit: [
      { label: "Prepared me for my career", value: avg(records.map((r) => r.careerPrep)) },
      { label: "Learning outcomes communicated clearly", value: avg(records.map((r) => r.ilo)) },
      { label: "Assessment matched learning outcomes", value: avg(records.map((r) => r.assessAligned)) },
      { label: "Exam schedules were flexible", value: avg(records.map((r) => r.examFlex)) },
    ],

    courseByCategory: byCategory,
    lowestCourses: sorted.slice(0, 8),
    highestCourses: sorted.slice(-8).reverse(),

    jobRelatedness: counts(records.map((r) => r.jobRelatedness)),
    waitingPeriod: counts(records.map((r) => r.waitingPeriod)),

    trainingDuration: counts(records.map((r) => r.trainingDuration)),
    evalEffective: counts(records.map((r) => r.evalEffective)),
    facedChallenges: counts(records.map((r) => r.facedChallenges)),
    flexibility: counts(records.map((r) => r.flexibility)),

    comparedSimilar: counts(records.map((r) => r.comparedSimilar)),
    recommend: counts(records.map((r) => r.recommend)),
    strengths: multiCounts(records, "strengths"),
    improve: multiCounts(records, "improve"),

    strengthQuotes: records.map((r) => r.strengthQuote).filter(Boolean),
    weaknessQuotes: records.map((r) => r.weaknessQuote).filter(Boolean),
  };
}
