import fs from "node:fs";
import path from "node:path";
import Dashboard from "./components/Dashboard";

export default function Home() {
  const file = path.join(process.cwd(), "public", "data", "responses.json");
  const { responses, courseColumns } = JSON.parse(fs.readFileSync(file, "utf-8"));

  return <Dashboard records={responses} courseColumns={courseColumns} />;
}
