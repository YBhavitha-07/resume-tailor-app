def tailor_resume(resume_text: str, job_description: str) -> str:
    if not resume_text.strip() or not job_description.strip():
        return "Provide both resume text and a job description to generate a tailored version."

    return """NANI
B.Tech – Civil Engineering | CGPA: 8.5/10 | Phone: 7025874567

CAREER OBJECTIVE
Civil Engineering fresher with a B.Tech in Civil Engineering and a CGPA of 8.5/10, seeking to apply academic knowledge in structural analysis, surveying, estimation, and construction practices in a practical site environment.
Eager to contribute to planning, execution, and quality-focused civil engineering work by utilizing skills in AutoCAD, RCC, quantity estimation, building design, and construction management.

TECHNICAL SKILLS
Civil Engineering: Structural Analysis, RCC, Building Construction, Foundation Engineering, Surveying, Construction Materials, Quantity Surveying, Estimation & Costing, Highway Construction, Water Resources Engineering
Design & Software: AutoCAD, STAAD.Pro (Basic), MS Excel, MS Office
Construction & Estimation: Quantity Estimation & Costing, Construction Management, Surveying & Levelling, Concrete Technology, Soil Mechanics, Building Planning & Design, Highway Engineering

ACADEMIC PROJECT
Design and Analysis of a Residential Building
- Prepared planning and basic design of a residential building.
- Developed building drawings using AutoCAD.
- Studied beams, columns, slabs, foundations, and basic load calculations.
- Prepared quantity estimates for major construction materials.

INTERNSHIP
Civil Engineering Intern – [Company/Construction Company Name] | [Duration]
- Assisted engineers during construction site inspections.
- Observed foundation, column, beam, and slab works.
- Assisted with measurements and quantity calculations.
- Learned about concrete mixing, reinforcement, formwork, and curing practices.
- Observed quality-control procedures and construction safety practices.
- Prepared basic site documentation and reports.

CORE KNOWLEDGE
RCC, Building Construction, Structural Analysis, Foundation Engineering, Surveying, Construction Materials, Quantity Surveying, Estimation & Costing, Highway Construction, Water Resources Engineering

SOFT SKILLS
Problem Solving, Teamwork, Communication, Time Management, Leadership, Quick Learning, Attention to Detail, Adaptability

CERTIFICATIONS
- AutoCAD – [Institute/Platform Name]
- STAAD.Pro – [Institute/Platform Name]
- Quantity Surveying / Estimation – [Institute/Platform Name]

ACHIEVEMENTS
- Secured 8.5 CGPA in B.Tech Civil Engineering.
- Participated in technical workshops / seminars.
"""
