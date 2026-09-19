import { useEffect, useState } from 'react';

const API_BASE = 'http://127.0.0.1:8000';

const DEMO_RESUME = `Senior Full Stack Engineer with 7+ years of experience designing and delivering scalable web applications, APIs, and cloud-driven products. Skilled in React, TypeScript, Node.js, Python, RESTful architecture, AWS deployment, and cross-functional leadership. Delivered user-facing features, improved performance, and mentored developers across multiple product teams.`;

const DEMO_JOB = `We are looking for a Senior Full Stack Engineer with strong experience in React, TypeScript, Python, REST APIs, cloud deployment, and building scalable software products. The ideal candidate excels in cross-functional teamwork, system performance optimization, and production-ready engineering practices.`;

const ENDPOINTS = {
  health: ['/api/health', '/health'],
  upload: ['/api/upload-resume', '/upload-resume'],
  analyze: ['/api/analyze', '/api/resume/analyze', '/analyze'],
  rewrite: ['/api/rewrite', '/rewrite'],
  recruiterView: ['/api/recruiter-view', '/recruiter-view'],
  pdf: ['/api/generate-pdf', '/generate-pdf'],
};

const normalizeScore = (value) => {
  const num = Number(value);
  if (!Number.isFinite(num)) return 0;
  return Math.max(0, Math.min(100, Math.round(num)));
};

async function requestJson(urls, options = {}) {
  let lastError = null;

  for (const endpoint of urls) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
          ...(options.headers || {}),
        },
      });

      if (response.status === 404) {
        continue;
      }

      if (!response.ok) {
        let payload = {};
        try {
          payload = await response.json();
        } catch {
          payload = {};
        }

        throw new Error(payload.detail || payload.message || `Request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError || new Error('Unable to reach the backend service.');
}

async function requestBinary(urls, options = {}) {
  let lastError = null;

  for (const endpoint of urls) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
          ...(options.headers || {}),
        },
      });

      if (response.status === 404) {
        continue;
      }

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `Download failed with status ${response.status}`);
      }

      return response;
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError || new Error('Unable to download the tailored resume PDF.');
}

function App() {
  const [resumeText, setResumeText] = useState(DEMO_RESUME);
  const [jobDescription, setJobDescription] = useState(DEMO_JOB);
  const [result, setResult] = useState(null);
  const [rewrite, setRewrite] = useState(null);
  const [recruiterView, setRecruiterView] = useState(null);
  const [backendStatus, setBackendStatus] = useState('Checking backend...');
  const [loading, setLoading] = useState(false);
  const [rewriteLoading, setRewriteLoading] = useState(false);
  const [recruiterLoading, setRecruiterLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState('ats');

  useEffect(() => {
    const checkHealth = async () => {
      const attempts = 3;

      for (let attempt = 1; attempt <= attempts; attempt += 1) {
        try {
          const response = await fetch(`${API_BASE}${ENDPOINTS.health[1]}`, {
            method: 'GET',
            headers: { Accept: 'application/json' },
          });

          if (response.ok) {
            setBackendStatus('Backend available');
            return;
          }
        } catch {
          // retry while the backend starts up
        }

        if (attempt < attempts) {
          await new Promise((resolve) => setTimeout(resolve, 500));
        }
      }

      setBackendStatus('Backend unavailable');
    };

    checkHealth();
  }, []);

  const handleAnalyze = async (customResume = resumeText, customJobDescription = jobDescription) => {
    if (!customResume.trim() || !customJobDescription.trim()) {
      setError('Please provide a resume and job description before analyzing.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const analysisData = await requestJson(ENDPOINTS.analyze, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_text: customResume,
          job_description: customJobDescription,
        }),
      });

      const analysisResult = {
        atsScore: normalizeScore(analysisData.ats_score ?? analysisData.match_percentage ?? 0),
        matchedKeywords: analysisData.matched_keywords ?? [],
        missingKeywords: analysisData.missing_keywords ?? [],
        detectedSections: analysisData.detected_sections ?? [],
        formattingFeedback: analysisData.formatting_feedback ?? [],
        improvementSuggestions: analysisData.improvement_suggestions ?? analysisData.suggestions ?? [],
        tailoredResume: analysisData.tailored_resume ?? customResume,
      };

      setResult(analysisResult);

      try {
        const rewriteData = await requestJson(ENDPOINTS.rewrite, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            resume_text: customResume,
            job_description: customJobDescription,
            tone: 'professional',
          }),
        });

        const rewrittenBullets = rewriteData.rewritten_bullets ?? [];
        const rewrittenText = rewriteData.tailored_resume || rewrittenBullets.join('\n\n') || analysisResult.tailoredResume;

        setRewrite({
          before: customResume,
          after: rewrittenText,
          bullets: rewrittenBullets,
        });
    
        setResult((prev) => ({
          ...prev,
          tailoredResume: rewrittenText,
        }));
      } catch {
        setRewrite({
          before: customResume,
          after: analysisResult.tailoredResume,
          bullets: [],
        });
      }
    } catch (err) {
      setError(err.message || 'The analysis request failed. Please try again.');
      setResult(null);
      setRewrite(null);
    } finally {
      setLoading(false);
    }
  };

  const handleRewriteOnly = async () => {
    if (!resumeText.trim() || !jobDescription.trim()) {
      setError('Please provide both the resume text and job description before rewriting.');
      return;
    }

    setRewriteLoading(true);
    setError('');

    try {
      const rewriteData = await requestJson(ENDPOINTS.rewrite, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_text: resumeText,
          job_description: jobDescription,
          tone: 'professional',
        }),
      });

      const rewrittenBullets = rewriteData.rewritten_bullets ?? [];
      const rewrittenText = rewriteData.tailored_resume || rewrittenBullets.join('\n\n') || resumeText;

      setRewrite({
        before: resumeText,
        after: rewrittenText,
        bullets: rewrittenBullets,
      });

      if (result) {
        setResult((prev) => ({
          ...prev,
          tailoredResume: rewrittenText,
        }));
      }
    } catch (err) {
      setError(err.message || 'Could not generate the AI rewrite.');
    } finally {
      setRewriteLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadData = await requestJson(ENDPOINTS.upload, {
        method: 'POST',
        body: formData,
      });

      const extractedText = uploadData.extracted_text || '';
      if (extractedText) {
        setResumeText(extractedText);
        if (jobDescription.trim()) {
          await handleAnalyze(extractedText, jobDescription);
        }
      } else {
        setError('The uploaded resume could not be parsed. Please paste the text manually.');
      }
    } catch (err) {
      setError(err.message || 'The resume upload failed.');
    } finally {
      setUploadLoading(false);
      event.target.value = '';
    }
  };

  const handleRecruiterView = async () => {
    if (!resumeText.trim() || !jobDescription.trim()) {
      setError('Please provide both a resume and a job description before opening Recruiter View.');
      return;
    }

    setRecruiterLoading(true);
    setError('');

    try {
      const recruiterData = await requestJson(ENDPOINTS.recruiterView, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_text: resumeText,
          job_description: jobDescription,
        }),
      });

      setRecruiterView(recruiterData);
      setViewMode('recruiter');
    } catch (err) {
      setError(err.message || 'Could not generate the recruiter view.');
    } finally {
      setRecruiterLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!result?.tailoredResume && !resumeText) {
      setError('Generate an ATS analysis before downloading a tailored resume PDF.');
      return;
    }

    setDownloadLoading(true);
    setError('');

    try {
      const pdfResponse = await requestBinary(ENDPOINTS.pdf, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: result?.tailoredResume || resumeText,
          title: 'Tailored Resume',
        }),
      });

      const blob = await pdfResponse.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'tailored_resume.pdf';
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || 'Failed to generate the PDF download.');
    } finally {
      setDownloadLoading(false);
    }
  };

  const applyDemo = () => {
    setResumeText(DEMO_RESUME);
    setJobDescription(DEMO_JOB);
    setError('');
    handleAnalyze(DEMO_RESUME, DEMO_JOB);
  };

  return (
    <div className="dashboard-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI Hiring Assistant</p>
          <h1>Resume Tailor & ATS Score Checker</h1>
        </div>
        <div className="status-pill">{backendStatus}</div>
      </header>

      <main className="dashboard-grid">
        <section className="panel left-panel">
          <div className="panel-header">
            <h2>Resume Workspace</h2>
            <button type="button" className="secondary-button" onClick={applyDemo}>
              Try Demo
            </button>
          </div>

          <div className="upload-box">
            <label className="file-upload">
              <input type="file" accept=".pdf,.docx" onChange={handleFileUpload} />
              <span>{uploadLoading ? 'Uploading...' : 'Upload PDF or DOCX'}</span>
            </label>
            <small>Accepted formats: PDF, DOCX</small>
          </div>

          <label className="field-label">
            Resume content
            <textarea
              value={resumeText}
              onChange={(event) => setResumeText(event.target.value)}
              placeholder="Paste your resume or upload a PDF/DOCX file..."
            />
          </label>

          <label className="field-label">
            Job description
            <textarea
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Paste the target job description here..."
            />
          </label>

          <div className="button-row">
            <button type="button" onClick={() => handleAnalyze()} disabled={loading || uploadLoading}>
              {loading ? 'Analyzing...' : 'Analyze Resume'}
            </button>
            <button type="button" className="secondary-button" onClick={handleRewriteOnly} disabled={rewriteLoading || loading}>
              {rewriteLoading ? 'Rewriting...' : 'Generate AI Rewrite'}
            </button>
          </div>
        </section>

        <section className="panel score-panel">
          <div className="score-header">
            <div>
              <p className="eyebrow compact">ATS Match</p>
              <h2>Overall Score</h2>
            </div>
            <div className="score-circle">
              {result ? `${result.atsScore}/100` : '—'}
            </div>
          </div>

          {error && <div className="alert error">{error}</div>}

          {!result && !loading && (
            <div className="empty-state">
              Upload a resume and paste a job description to get your ATS score and rewrite recommendations.
            </div>
          )}

          {result && (
            <>
              <div className="metric-grid">
                <div className="metric-card success">
                  <span>Matched keywords</span>
                  <strong>{result.matchedKeywords.length}</strong>
                </div>
                <div className="metric-card warning">
                  <span>Missing keywords</span>
                  <strong>{result.missingKeywords.length}</strong>
                </div>
                <div className="metric-card info">
                  <span>Detected sections</span>
                  <strong>{result.detectedSections.length}</strong>
                </div>
              </div>

              <div className="keyword-group">
                <h3>Matched keywords</h3>
                <div className="chip-list">
                  {result.matchedKeywords.length ? (
                    result.matchedKeywords.map((keyword) => <span key={keyword} className="chip ok">{keyword}</span>)
                  ) : (
                    <span className="muted-text">No keyword overlap detected.</span>
                  )}
                </div>
              </div>

              <div className="keyword-group">
                <h3>Missing keywords</h3>
                <div className="chip-list">
                  {result.missingKeywords.length ? (
                    result.missingKeywords.map((keyword) => <span key={keyword} className="chip warn">{keyword}</span>)
                  ) : (
                    <span className="muted-text">No major missing keywords found.</span>
                  )}
                </div>
              </div>
            </>
          )}
        </section>
      </main>

      {result && (
        <>
          {viewMode === 'ats' ? (
            <section className="panel insight-panel">
              <div className="panel-header">
                <h2>Career Insights</h2>
                <div className="button-row compact-button-row">
                  <button type="button" className="secondary-button" onClick={handleRecruiterView} disabled={recruiterLoading}>
                    {recruiterLoading ? 'Loading Recruiter View...' : 'Recruiter View'}
                  </button>
                  <button type="button" className="secondary-button" onClick={handleDownloadPdf} disabled={downloadLoading}>
                    {downloadLoading ? 'Preparing PDF...' : 'Download Tailored Resume PDF'}
                  </button>
                </div>
              </div>

              <div className="insight-grid">
                <article className="info-card">
                  <h3>Resume section detection</h3>
                  <div className="chip-list">
                    {result.detectedSections.length ? (
                      result.detectedSections.map((section) => <span key={section} className="chip neutral">{section}</span>)
                    ) : (
                      <span className="muted-text">No sections detected.</span>
                    )}
                  </div>
                </article>

                <article className="info-card">
                  <h3>Formatting feedback</h3>
                  <ul className="bullet-list">
                    {result.formattingFeedback.length ? (
                      result.formattingFeedback.map((item) => <li key={item}>{item}</li>)
                    ) : (
                      <li>No formatting warnings.</li>
                    )}
                  </ul>
                </article>

                <article className="info-card wide">
                  <h3>Improvement suggestions</h3>
                  <ul className="bullet-list">
                    {result.improvementSuggestions.length ? (
                      result.improvementSuggestions.map((item) => <li key={item}>{item}</li>)
                    ) : (
                      <li>Resume is well aligned with the target role.</li>
                    )}
                  </ul>
                </article>
              </div>

              {rewrite && (
                <div className="compare-section">
                  <h3>AI rewrite comparison</h3>
                  <div className="compare-grid">
                    <div className="compare-card compare-card--before">
                      <h4>Before</h4>
                      <p>{rewrite.before}</p>
                    </div>
                    <div className="compare-card compare-card--after">
                      <h4>After</h4>
                      {rewrite.bullets.length ? (
                        <ul className="rewrite-list">
                          {rewrite.bullets.map((bullet) => <li key={bullet}>{bullet}</li>)}
                        </ul>
                      ) : (
                        <div className="resume-preview">{rewrite.after}</div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </section>
          ) : (
            <section className="panel recruiter-panel">
              <div className="panel-header">
                <h2>Recruiter View</h2>
                <button type="button" className="secondary-button" onClick={() => setViewMode('ats')}>
                  Back to ATS Analysis
                </button>
              </div>

              {recruiterView && (
                <div className="recruiter-layout">
                  <div className="recruiter-main">
                    <div className="recruiter-header">
                      <div>
                        <p className="eyebrow compact">Candidate Snapshot</p>
                        <h3>{recruiterView.candidate_name}</h3>
                      </div>
                    </div>

                    <div className="recruiter-contact-row">
                      {recruiterView.contact.phone && <span>Phone: {recruiterView.contact.phone}</span>}
                      {recruiterView.contact.email && <span>Email: {recruiterView.contact.email}</span>}
                    </div>

                    <div className="recruiter-section">
                      <h4>Professional Summary</h4>
                      <p>{recruiterView.summary}</p>
                    </div>

                    <div className="recruiter-section">
                      <h4>Most Relevant Role</h4>
                      <div className="recruiter-role-pill">{recruiterView.professional_title}</div>
                    </div>

                    <div className="recruiter-section">
                      <h4>Key Skills</h4>
                      <div className="chip-list">
                        {recruiterView.key_skills.map((skill) => (
                          <span key={skill} className="chip ok">{skill}</span>
                        ))}
                      </div>
                    </div>

                    <div className="recruiter-section">
                      <h4>Recent Work Experience</h4>
                      <ul className="recruiter-list">
                        {recruiterView.relevant_experience.map((item) => <li key={item}>{item}</li>)}
                      </ul>
                    </div>

                    <div className="recruiter-section">
                      <h4>Important Achievements</h4>
                      <ul className="recruiter-list">
                        {recruiterView.achievements.length ? (
                          recruiterView.achievements.map((item) => <li key={item}>{item}</li>)
                        ) : (
                          <li>No specific achievement text detected in the provided resume.</li>
                        )}
                      </ul>
                    </div>

                    <div className="recruiter-section">
                      <h4>Education</h4>
                      <ul className="recruiter-list">
                        {recruiterView.education.length ? (
                          recruiterView.education.map((item) => <li key={item}>{item}</li>)
                        ) : (
                          <li>No education section detected.</li>
                        )}
                      </ul>
                    </div>
                  </div>

                  <aside className="recruiter-side-panel">
                    <h3>6-Second Recruiter Scan</h3>

                    <div className="scan-block">
                      <h4>First impression</h4>
                      <p>{recruiterView.scan_summary.first_impression}</p>
                    </div>

                    <div className="scan-block">
                      <h4>Most noticeable strengths</h4>
                      <ul className="recruiter-list compact-list">
                        {recruiterView.strengths.map((item) => <li key={item}>{item}</li>)}
                      </ul>
                    </div>

                    <div className="scan-block">
                      <h4>Important matching skills</h4>
                      <div className="chip-list">
                        {recruiterView.matched_keywords.map((keyword) => (
                          <span key={keyword} className="chip ok">{keyword}</span>
                        ))}
                      </div>
                    </div>

                    <div className="scan-block">
                      <h4>Important missing information</h4>
                      <div className="chip-list">
                        {recruiterView.missing_keywords.length ? (
                          recruiterView.missing_keywords.map((keyword) => (
                            <span key={keyword} className="chip warn">{keyword}</span>
                          ))
                        ) : (
                          <span className="muted-text">No critical gaps detected.</span>
                        )}
                      </div>
                    </div>

                    <div className="scan-block">
                      <h4>Recruiter attention</h4>
                      <ul className="attention-list">
                        <li className="attention-good">{recruiterView.scan_summary.keyword_visibility}</li>
                        <li className="attention-good">{recruiterView.scan_summary.experience_relevance}</li>
                        <li className="attention-good">{recruiterView.scan_summary.section_completeness}</li>
                        {recruiterView.attention_items.map((item) => (
                          <li key={item} className="attention-warn">{item}</li>
                        ))}
                      </ul>
                    </div>
                  </aside>
                </div>
              )}
            </section>
          )}
        </>
      )}
    </div>
  );
}

export default App;
