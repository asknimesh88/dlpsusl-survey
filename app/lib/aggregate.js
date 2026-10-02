// Pure aggregation over the raw (Animal Bio-Resource-only) response records,
// re-run in the browser whenever the year filter changes.

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
    .sort((a, b) => b.value - a.value || a.label.localeCompare(b.label));
}

const multiCounts = (records, field) => counts(records.flatMap((r) => r[field] || []));

// Merge spelling/company-suffix variants ("X Pvt Ltd" vs "X") into one tag
function looseCounts(items) {
  const groups = new Map();
  for (const raw of items) {
    if (!raw) continue;
    const key = raw.toLowerCase().replace(/\b(pvt|ltd|plc|limited|private)\b/g, "").replace(/[^a-z0-9]/g, "");
    if (!key) continue;
    const g = groups.get(key) || { label: raw.trim(), value: 0 };
    g.value += 1;
    groups.set(key, g);
  }
  return [...groups.values()].sort((a, b) => b.value - a.value || a.label.localeCompare(b.label));
}

const avgByKey = (records, field, keys) =>
  keys.map((k) => ({ label: k, value: avg(records.map((r) => r[field][k])) ?? 0 }));

export const ACTIVITY_LEVELS = ["Sufficient", "Somewhat", "Inadequate"];

export const TEXT_QUESTIONS = [
  ["15", "Courses most useful in their career"],
  ["14i", "Comments on core courses"],
  ["14ii", "Comments on compulsory specialization courses"],
  ["16b", "Subjects felt outdated or less useful"],
  ["17", "New subjects or topics to add"],
  ["12", "Professional qualifications"],
  ["22", "Improving the final-year research and training"],
  ["24", "Additional teaching methods"],
  ["29", "Improving assessment methods"],
  ["30", "Were expectations met"],
  ["31", "Teaching and learning practices"],
  ["32", "Workload of the course"],
  ["33", "Strict or challenging situations faced"],
  ["34", "Flexibility of the course structure"],
  ["35", "Key strength of the programme"],
  ["36", "Key weakness of the programme"],
  ["37", "Would they recommend it, and why"],
  ["43", "Other comments or suggestions"],
];

export function filterByYear(records, year) {
  if (!year || year === "All") return records;
  return records.filter((r) => r.year === year);
}

export function years(records) {
  return [...new Set(records.map((r) => r.year))].sort();
}

export function aggregate(records, courseColumns) {
  const n = records.length;

  const courses = courseColumns
    .map((c) => ({ ...c, average: avg(records.map((r) => r.courses[c.id])) }))
    .filter((c) => c.average !== null);

  const group = (cat) => courses.filter((c) => c.category === cat).sort((a, b) => b.average - a.average);

  // Written answers per question, alphabetical so rows cannot be matched up across questions
  const texts = {};
  for (const [q] of TEXT_QUESTIONS) {
    texts[q] = records
      .map((r) => r.text[q])
      .filter(Boolean)
      .sort((a, b) => a.localeCompare(b));
  }

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

    jobRelatedness: counts(records.map((r) => r.jobRelatedness)),
    waitingPeriod: counts(records.map((r) => r.waitingPeriod)),
    empDuration: counts(records.map((r) => r.empDuration)),
    roles: looseCounts(records.map((r) => r.roleNow)),
    prevRoles: looseCounts(records.map((r) => r.rolePrev)),
    companies: looseCounts(records.map((r) => r.company)),

    curriculumFit: [
      { label: "Prepared me for my career", value: avg(records.map((r) => r.careerPrep)) ?? 0 },
      { label: "Gave me job-related skills and knowledge", value: avg(records.map((r) => r.jobSkills)) ?? 0 },
      { label: "Overall graduate experience", value: avg(records.map((r) => r.overallExp)) ?? 0 },
      { label: "Learning outcomes communicated clearly", value: avg(records.map((r) => r.ilo)) ?? 0 },
      { label: "Assessment matched learning outcomes", value: avg(records.map((r) => r.assessAligned)) ?? 0 },
      { label: "Exam schedules were flexible", value: avg(records.map((r) => r.examFlex)) ?? 0 },
    ],
    expectationsMet: counts(records.map((r) => r.expectationsMet)),
    outdated: counts(records.map((r) => r.outdated)),

    coreCourses: group("core"),
    compulsoryCourses: group("compulsory"),
    electiveCourses: group("elective"),
    courseByCategory: [
      { label: "Core courses", value: avg(group("core").map((c) => c.average)) ?? 0 },
      { label: "Compulsory specialization", value: avg(group("compulsory").map((c) => c.average)) ?? 0 },
      { label: "Elective specialization", value: avg(group("elective").map((c) => c.average)) ?? 0 },
    ],
    usefulCourses: multiCounts(records, "usefulCourses").slice(0, 12),

    activities: Object.keys(records[0]?.activities || {}).map((label) => ({
      label,
      levels: ACTIVITY_LEVELS.map((lv) => ({ level: lv, value: records.filter((r) => r.activities[label] === lv).length })),
    })),
    teaching: avgByKey(records, "teaching", Object.keys(records[0]?.teaching || {})),
    assessment: avgByKey(records, "assessment", Object.keys(records[0]?.assessment || {})),
    strengthen: multiCounts(records, "strengthen"),

    trainingDuration: counts(records.map((r) => r.trainingDuration)),
    evalEffective: counts(records.map((r) => r.evalEffective)),
    facedChallenges: counts(records.map((r) => r.facedChallenges)),
    flexibility: counts(records.map((r) => r.flexibility)),

    comparedSimilar: counts(records.map((r) => r.comparedSimilar)),
    recommend: counts(records.map((r) => r.recommend)),
    strengths: multiCounts(records, "strengths"),
    improve: multiCounts(records, "improve"),

    texts,
  };
}
