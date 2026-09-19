function ATSResult({ result, error }) {
  if (error) {
    return (
      <section className="panel result-panel error-panel">
        <h2>Results</h2>
        <p>{error}</p>
      </section>
    );
  }

  if (!result) {
    return (
      <section className="panel result-panel placeholder-panel">
        <h2>ATS Score</h2>
        <p>Submit your resume and job description to get a score.</p>
      </section>
    );
  }

  return (
    <section className="panel result-panel">
      <h2>ATS Score Overview</h2>

      <div className="score-box">
        <span className="score-label">Match Score</span>
        <strong>{result.ats_score}%</strong>
      </div>

      <div className="result-grid">
        <div>
          <h3>Missing Keywords</h3>
          <ul>
            {result.missing_keywords.length > 0 ? (
              result.missing_keywords.map((keyword) => <li key={keyword}>{keyword}</li>)
            ) : (
              <li>No major missing keywords found.</li>
            )}
          </ul>
        </div>

        <div>
          <h3>Recommendations</h3>
          <ul>
            {result.suggestions.map((suggestion) => (
              <li key={suggestion}>{suggestion}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="tailored-box">
        <h3>Tailored Resume Preview</h3>
        <p>{result.tailored_resume}</p>
      </div>
    </section>
  );
}

export default ATSResult;
