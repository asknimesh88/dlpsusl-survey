import fs from "node:fs";
import path from "node:path";
import Dashboard from "./components/Dashboard";

// One entry per specialisation. Adding a third module means dropping its
// responses file in public/data and appending a row here.
const MODULES = [
  {
    id: "animal",
    label: "Animal Bio-Resource",
    full: "Animal Bio-Resource Technology & Management",
    file: "responses.json",
  },
  {
    id: "aquatic",
    label: "Aquatic Bio-Resource",
    full: "Aquatic Bio-Resource Technology & Management",
    file: "responses-aquatic.json",
    note:
      "Only eight graduates answered, so a single person shifts any percentage by about 12 points. " +
      "Read the figures as indicative and the written answers as the firmer signal.",
  },
];

export default function Home() {
  const dir = path.join(process.cwd(), "public", "data");

  const modules = MODULES.map(({ file, ...meta }) => {
    const { responses, courseColumns } = JSON.parse(fs.readFileSync(path.join(dir, file), "utf-8"));
    const years = [...new Set(responses.map((r) => r.year))].sort();
    return {
      ...meta,
      records: responses,
      courseColumns,
      lede: `What ${responses.length} graduates from ${years[0]} to ${years[years.length - 1]} say about the degree that trained them.`,
    };
  });

  return <Dashboard modules={modules} />;
}
