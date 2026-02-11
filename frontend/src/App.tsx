import React, { useEffect, useState } from "react";
import type { BuildPermafrost } from "./types";

interface HealthResponse {
  status: string;
  service: string;
}

const App: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);

  const [build, setBuild] = useState<BuildPermafrost | null>(null);
  const [buildError, setBuildError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then(async (res) => {
        if (!res.ok) {
          throw new Error(`Health request failed with ${res.status}`);
        }
        return res.json();
      })
      .then((data: HealthResponse) => {
        setHealth(data);
        setHealthError(null);
      })
      .catch((err: unknown) => {
        const message =
          err instanceof Error ? err.message : "Unknown error fetching health";
        setHealthError(message);
        setHealth(null);
      });

    fetch("/api/builds/permafrost-marshal")
      .then(async (res) => {
        if (!res.ok) {
          throw new Error(`Build request failed with ${res.status}`);
        }
        return res.json();
      })
      .then((data: BuildPermafrost) => {
        setBuild(data);
        setBuildError(null);
      })
      .catch((err: unknown) => {
        const message =
          err instanceof Error ? err.message : "Unknown error fetching build";
        setBuildError(message);
        setBuild(null);
      });
  }, []);

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", padding: "1.5rem" }}>
      <h1>The Elder Elemental – ESO Build Engine UI</h1>

      <section style={{ marginTop: "1.5rem" }}>
        <h2>Backend health</h2>
        {health && (
          <p>
            Status: <strong>{health.status}</strong> (service: {health.service})
          </p>
        )}
        {healthError && (
          <p style={{ color: "red" }}>
            Failed to reach backend health: {healthError}
          </p>
        )}
        {!health && !healthError && <p>Checking backend health…</p>}
      </section>

      <section style={{ marginTop: "1.5rem" }}>
        <h2>Permafrost Marshal (read-only)</h2>
        {build && (
          <div>
            <p>
              <strong>Name:</strong> {build.name}
            </p>
            <p>
              <strong>Class core:</strong> {build.classcore}
            </p>
            <p>
              <strong>Subclasses:</strong> {build.subclasses.join(", ")}
            </p>
            <p>
              <strong>Role tags:</strong> {build.roletags.join(", ")}
            </p>
            <p>
              <strong>CP total:</strong> {build.cptotal}
            </p>
            <p>
              <strong>Attributes:</strong> {build.attributes.health} Health /{" "}
              {build.attributes.magicka} Magicka / {build.attributes.stamina}{" "}
              Stamina
            </p>
            <p>
              <strong>Pillars:</strong> resist target{" "}
              {build.pillars.resist.targetresistshown}, speed profile{" "}
              {build.pillars.speed.profile}, health focus{" "}
              {build.pillars.health.focus}
            </p>
          </div>
        )}
        {buildError && (
          <p style={{ color: "red" }}>
            Failed to load Permafrost Marshal build: {buildError}
          </p>
        )}
        {!build && !buildError && <p>Loading build…</p>}
      </section>
    </div>
  );
};

export default App;
