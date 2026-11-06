export default function App() {
  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand-mark" aria-hidden="true">M</div>
        <div>
          <p className="eyebrow">World simulation laboratory</p>
          <h1>Mnemosyne</h1>
        </div>
        <span className="status">Foundation in progress</span>
      </header>

      <section className="welcome" aria-labelledby="welcome-title">
        <p className="eyebrow">The observatory</p>
        <h2 id="welcome-title">A world is waiting to be imagined.</h2>
        <p className="intro">
          This desktop shell is ready for the first world creation and simulation
          features. Backend services are developed separately and will connect here.
        </p>
        <div className="service-row">
          <span className="service-dot" />
          <span>Application shell initialized</span>
        </div>
      </section>
      <footer>Mnemosyne · Local development</footer>
    </main>
  );
}
