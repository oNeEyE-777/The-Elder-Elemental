
import express, { Request, Response } from "express";
import path from "node:path";
import fs from "node:fs";
import {
  Skill,
  Effect,
  SetItem,
  CpStar,
  Build
} from "./types";

const app = express();
const port = process.env.PORT || 3001;

// Resolve repo root assuming backend/ lives directly under the repo root.
const repoRoot = path.resolve(__dirname, "..", "..");

function loadJsonFile<T>(relativePath: string): T {
  const fullPath = path.join(repoRoot, relativePath);
  const raw = fs.readFileSync(fullPath, "utf8");
  return JSON.parse(raw) as T;
}

// Health check
app.get("/api/health", (_req: Request, res: Response) => {
  res.json({ status: "ok", service: "eso-build-engine-backend" });
});

// Data summary: prove JSON wiring from data/ works.
app.get("/api/data/summary", (_req: Request, res: Response) => {
  try {
    const skills = loadJsonFile<{ skills: Skill[] }>("data/skills.json");
    const effects = loadJsonFile<{ effects: Effect[] }>("data/effects.json");
    const sets = loadJsonFile<{ sets: SetItem[] }>("data/sets.json");
    const cpStars = loadJsonFile<{ cpstars: CpStar[] }>("data/cp-stars.json");

    const payload = {
      skillsCount: skills.skills.length,
      effectsCount: effects.effects.length,
      setsCount: sets.sets.length,
      cpStarsCount: cpStars.cpstars.length
    };

    console.log("DATA SUMMARY PAYLOAD:", payload);

    res.json(payload);
  } catch (err) {
    console.error("Failed to load data JSONs", err);
    res.status(500).json({ error: "Failed to load data JSONs" });
  }
});

// Full data for selector UIs: skills, sets, CP stars.
app.get("/api/data", (_req: Request, res: Response) => {
  try {
    const skills = loadJsonFile<{ skills: Skill[] }>("data/skills.json");
    const sets = loadJsonFile<{ sets: SetItem[] }>("data/sets.json");
    const cpStars = loadJsonFile<{ cpstars: CpStar[] }>("data/cp-stars.json");

    res.json({
      skills: skills.skills,
      sets: sets.sets,
      cpStars: cpStars.cpstars
    });
  } catch (err) {
    console.error("Failed to load data for /api/data", err);
    res.status(500).json({ error: "Failed to load data" });
  }
});

// General build loader by id (stem), e.g. "permafrost-marshal".
app.get("/api/builds/:id", (req: Request, res: Response) => {
  const id = req.params.id;

  // Only allow simple file stems to avoid path tricks.
  const safeId = id.replace(/[^a-zA-Z0-9\-]/g, "");
  if (!safeId) {
    return res.status(400).json({ error: "Invalid build id" });
  }

  const buildPath = path.join("builds", `${safeId}.json`);

  try {
    const build = loadJsonFile<Build>(buildPath);
    res.json(build);
  } catch (err) {
    console.error(`Failed to load build for id=${safeId}`, err);
    res.status(404).json({ error: "Build not found" });
  }
});

// Explicit Permafrost Marshal route as a stable alias.
app.get("/api/builds/permafrost-marshal", (_req: Request, res: Response) => {
  try {
    const build = loadJsonFile<Build>("builds/permafrost-marshal.json");
    res.json(build);
  } catch (err) {
    console.error("Failed to load Permafrost Marshal build", err);
    res.status(500).json({ error: "Failed to load Permafrost Marshal build" });
  }
});

app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`ESO Build Engine backend listening on http://localhost:${port}`);
});
