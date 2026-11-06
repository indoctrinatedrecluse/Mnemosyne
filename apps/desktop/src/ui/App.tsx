import { FormEvent, useEffect, useMemo, useState } from "react";

import { createWorld, listWorlds, World } from "../services/api";

const initialForm = {
  name: "",
  description: "",
  seed: "73421",
  calendar_start_year: "1",
  calendar_start_month: "1",
  tick_interval_seconds: "5",
};

export default function App() {
  const [worlds, setWorlds] = useState<World[]>([]);
  const [form, setForm] = useState(initialForm);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const selectedWorld = useMemo(
    () => worlds.find((world) => world.id === selectedId) ?? null,
    [selectedId, worlds],
  );

  async function refreshWorlds() {
    setLoading(true);
    try {
      const result = await listWorlds();
      setWorlds(result);
      setSelectedId((current) => current ?? result[0]?.id ?? null);
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not load worlds.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refreshWorlds();
  }, []);

  async function submitWorld(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const created = await createWorld({
        name: form.name,
        description: form.description || null,
        seed: Number(form.seed),
        calendar_start_year: Number(form.calendar_start_year),
        calendar_start_month: Number(form.calendar_start_month),
        tick_interval_seconds: Number(form.tick_interval_seconds),
      });
      setWorlds((current) => [created, ...current]);
      setSelectedId(created.id);
      setForm(initialForm);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not create the world.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand-mark" aria-hidden="true">M</div>
        <div>
          <p className="eyebrow">World simulation laboratory</p>
          <h1>Mnemosyne</h1>
        </div>
        <span className="status"><span className="status-dot" /> Local observatory</span>
      </header>

      <section className="workspace">
        <div className="page-heading">
          <div>
            <p className="eyebrow">World archive</p>
            <h2>Choose a world to observe.</h2>
          </div>
          <button className="quiet-button" type="button" onClick={() => void refreshWorlds()}>
            Refresh archive
          </button>
        </div>

        {error && <div className="notice" role="alert">{error}</div>}

        <div className="columns">
          <section className="panel archive-panel" aria-labelledby="archive-title">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Saved worlds</p>
                <h3 id="archive-title">World archive</h3>
              </div>
              <span className="count">{worlds.length.toString().padStart(2, "0")}</span>
            </div>

            {loading ? (
              <p className="muted">Reading the archive…</p>
            ) : worlds.length === 0 ? (
              <div className="empty-state">
                <div className="empty-orbit" aria-hidden="true">✦</div>
                <h4>No worlds recorded</h4>
                <p>Create a seeded world to begin the chronicle.</p>
              </div>
            ) : (
              <ul className="world-list">
                {worlds.map((world) => (
                  <li key={world.id}>
                    <button
                      className={`world-row${world.id === selectedId ? " is-selected" : ""}`}
                      type="button"
                      onClick={() => setSelectedId(world.id)}
                    >
                      <span className="world-glyph" aria-hidden="true">✦</span>
                      <span className="world-copy">
                        <strong>{world.name}</strong>
                        <small>Seed {world.seed} · {world.calendar_start_year}.{String(world.calendar_start_month).padStart(2, "0")}</small>
                      </span>
                      <span className="row-arrow" aria-hidden="true">↗</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <div className="detail-column">
            <section className="panel selected-panel" aria-labelledby="selected-title">
              <p className="eyebrow">Current selection</p>
              {selectedWorld ? (
                <>
                  <h3 id="selected-title">{selectedWorld.name}</h3>
                  <p className="world-description">
                    {selectedWorld.description || "No description has been recorded for this world."}
                  </p>
                  <div className="metadata-grid">
                    <div><span>Seed</span><strong>{selectedWorld.seed}</strong></div>
                    <div><span>Calendar start</span><strong>{selectedWorld.calendar_start_year}.{String(selectedWorld.calendar_start_month).padStart(2, "0")}</strong></div>
                    <div><span>Tick interval</span><strong>{selectedWorld.tick_interval_seconds}s</strong></div>
                  </div>
                </>
              ) : (
                <>
                  <h3 id="selected-title">Awaiting a world</h3>
                  <p className="world-description">Create a world to establish its name, seed, and calendar.</p>
                </>
              )}
            </section>

            <section className="panel create-panel" aria-labelledby="create-title">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">Begin a chronicle</p>
                  <h3 id="create-title">Create a world</h3>
                </div>
                <span className="gold-rule" />
              </div>
              <form className="world-form" onSubmit={submitWorld}>
                <label className="field field-wide">
                  <span>World name</span>
                  <input
                    autoComplete="off"
                    maxLength={120}
                    minLength={1}
                    onChange={(event) => setForm({ ...form, name: event.target.value })}
                    placeholder="The Shattered Meridian"
                    required
                    value={form.name}
                  />
                </label>
                <label className="field field-wide">
                  <span>Description <small>optional</small></span>
                  <textarea
                    maxLength={2_000}
                    onChange={(event) => setForm({ ...form, description: event.target.value })}
                    placeholder="A brief note about the world’s character…"
                    rows={2}
                    value={form.description}
                  />
                </label>
                <label className="field">
                  <span>Seed</span>
                  <input max={9007199254740991} min={0} onChange={(event) => setForm({ ...form, seed: event.target.value })} required type="number" value={form.seed} />
                </label>
                <label className="field">
                  <span>Start year</span>
                  <input min={1} onChange={(event) => setForm({ ...form, calendar_start_year: event.target.value })} required type="number" value={form.calendar_start_year} />
                </label>
                <label className="field">
                  <span>Start month</span>
                  <input max={12} min={1} onChange={(event) => setForm({ ...form, calendar_start_month: event.target.value })} required type="number" value={form.calendar_start_month} />
                </label>
                <label className="field">
                  <span>Tick interval <small>seconds</small></span>
                  <input max={86400} min={1} onChange={(event) => setForm({ ...form, tick_interval_seconds: event.target.value })} required type="number" value={form.tick_interval_seconds} />
                </label>
                <button className="primary-button" disabled={saving} type="submit">
                  {saving ? "Recording world…" : "Create world"}
                  <span aria-hidden="true">↗</span>
                </button>
              </form>
            </section>
          </div>
        </div>
      </section>
      <footer>Mnemosyne · World persistence prototype</footer>
    </main>
  );
}
