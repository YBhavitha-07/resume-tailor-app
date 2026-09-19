function ResumeForm({
  resumeText,
  jobDescription,
  setResumeText,
  setJobDescription,
  handleSubmit,
  loading,
}) {
  return (
    <section className="panel">
      <h2>Resume Inputs</h2>
      <form onSubmit={handleSubmit} className="resume-form">
        <label>
          Resume Text
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            rows={12}
            placeholder="Paste your resume here..."
          />
        </label>

        <label>
          Job Description
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            rows={12}
            placeholder="Paste the target job description here..."
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Checking...' : 'Check ATS Match'}
        </button>
      </form>
    </section>
  );
}

export default ResumeForm;
