import ChatBot from "./components/ChatBot";
import "./App.css";

const STATS = [
  { value: "70th",   label: "NIRF Ranking",   sub: "Engineering Category" },
  { value: "NAAC A+", label: "Accreditation", sub: "Highest Grade" },
  { value: "50+",    label: "Programs",        sub: "UG & PG Courses" },
  { value: "95%",    label: "Placement Rate",  sub: "Top Recruiters" },
];

const DEPARTMENTS = [
  { icon: "💻", name: "CSE / AI & ML / Data Science", desc: "Python, ML, Deep Learning, Cloud Computing" },
  { icon: "📡", name: "ECE / EEE / IT",               desc: "Embedded Systems, 5G, Power Systems, IoT" },
  { icon: "⚙️", name: "Civil / Mechanical Engg.",     desc: "AutoCAD, Smart Cities, CAD/CAM, Robotics" },
  { icon: "🧬", name: "BioTech / BioMedical",         desc: "Genetics, Medical Devices, Pharmaceuticals" },
  { icon: "🌾", name: "Food Tech / B.Sc Agriculture", desc: "FMCG, Food Safety, Agri-Science, R&D" },
  { icon: "🧪", name: "Chemical / Textile Engg.",     desc: "Process Safety, CHEMCAD, Industry 4.0" },
];

const HIGHLIGHTS = [
  { icon: "🏆", title: "ABET Accredited",       desc: "Internationally recognized engineering programs accepted worldwide" },
  { icon: "🌍", title: "Open to All States",    desc: "Diverse student community from across India welcoming all backgrounds" },
  { icon: "🤝", title: "Industry Partnerships", desc: "Strong ties with top tech & core companies ensuring great placements" },
  { icon: "🔬", title: "Research Labs",         desc: "State-of-the-art AI, ML, Biotech and Food Tech research facilities" },
];

export default function App() {
  return (
    <div className="page">

      {/* ── Navbar ── */}
      <nav className="navbar">
        <div className="nav-brand">
          <div className="nav-logo">V</div>
          <div>
            <div className="nav-title">Vignan's</div>
            <div className="nav-title">Foundation of Science, Technology & Research</div>
          </div>
        </div>
        <div className="nav-links">
          <a href="#programs">Programs</a>
          <a href="#highlights">Why Vignan</a>
          <a href="#contact">Contact</a>
          <a href="#" className="nav-apply-btn">Apply Now</a>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="hero">
        <div className="hero-bg-pattern" aria-hidden="true" />
        <div className="hero-left">
          <div className="hero-badge">🎓 Admissions Open 2025–26</div>
          <h1 className="hero-title">
            Shape Your Future at<br />
            <span className="hero-accent">Vignan's University</span>
          </h1>
          <p className="hero-desc">
            NAAC A+ &nbsp;|&nbsp; NIRF Ranked 70th in Engineering &nbsp;|&nbsp; ABET Accredited<br />
            World-class education with an industry-driven curriculum.
          </p>
          <div className="hero-btns">
            <a href="#programs" className="btn-primary">Explore Programs</a>
            <a href="#contact"  className="btn-secondary">Contact Admissions</a>
          </div>
        </div>
        <div className="hero-right">
          <div className="hero-card">
            <div className="hc-icon">📚</div>
            <div className="hc-text">
              <div className="hc-title">Ask our AI Assistant</div>
              <div className="hc-sub">Instant answers about admissions</div>
            </div>
            <span className="hc-arrow">→</span>
          </div>
          <div className="hero-card">
            <div className="hc-icon">⚡</div>
            <div className="hc-text">
              <div className="hc-title">Quick EAMCET Guidance</div>
              <div className="hc-sub">Check eligibility & cutoffs</div>
            </div>
            <span className="hc-arrow">→</span>
          </div>
          <div className="hero-card highlight-card-special">
            <div className="hc-icon">🗓️</div>
            <div className="hc-text">
              <div className="hc-title">Admissions close June</div>
              <div className="hc-sub">Don't miss the deadline!</div>
            </div>
            <span className="hc-arrow">→</span>
          </div>
        </div>
      </section>

      {/* ── Stats Bar ── */}
      <section className="stats-bar">
        {STATS.map((s) => (
          <div className="stat-item" key={s.label}>
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
            <div className="stat-sub">{s.sub}</div>
          </div>
        ))}
      </section>

      {/* ── Departments ── */}
      <section className="section" id="programs">
        <div className="section-header">
          <div className="section-badge">Our Programs</div>
          <h2 className="section-title">Departments & Courses</h2>
          <p className="section-desc">Industry-aligned programs designed for the careers of tomorrow</p>
        </div>
        <div className="dept-grid">
          {DEPARTMENTS.map((d) => (
            <div className="dept-card" key={d.name}>
              <div className="dept-card-icon">{d.icon}</div>
              <div className="dept-card-name">{d.name}</div>
              <div className="dept-card-desc">{d.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Why Vignan ── */}
      <section className="section section-alt" id="highlights">
        <div className="section-header">
          <div className="section-badge">Why Choose Us</div>
          <h2 className="section-title">The Vignan Advantage</h2>
          <p className="section-desc">A legacy of excellence, innovation and industry-ready graduates</p>
        </div>
        <div className="hl-grid">
          {HIGHLIGHTS.map((h) => (
            <div className="hl-card" key={h.title}>
              <div className="hl-icon">{h.icon}</div>
              <div className="hl-title">{h.title}</div>
              <div className="hl-desc">{h.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA Banner ── */}
      <section className="cta-banner">
        <h2 className="cta-title">Have questions about admissions?</h2>
        <p className="cta-desc">Our AI-powered assistant is available 24/7 to guide you through courses, eligibility, deadlines and more.</p>
        <div className="cta-tip">👉 Click the chat button at the bottom-right to get started!</div>
      </section>

      {/* ── Contact ── */}
      <section className="section" id="contact">
        <div className="section-header">
          <div className="section-badge">Get In Touch</div>
          <h2 className="section-title">Admissions Office</h2>
        </div>
        <div className="contact-grid">
          <div className="contact-card">
            <div className="contact-icon">📍</div>
            <div className="contact-label">Address</div>
            <div className="contact-val">Vadlamudi, Guntur District,<br />Andhra Pradesh — 522213</div>
          </div>
          <div className="contact-card">
            <div className="contact-icon">📞</div>
            <div className="contact-label">Phone</div>
            <div className="contact-val">+91-0863-2344700</div>
          </div>
          <div className="contact-card">
            <div className="contact-icon">✉️</div>
            <div className="contact-label">Email</div>
            <div className="contact-val">admissions@vignan.ac.in</div>
          </div>
          <div className="contact-card">
            <div className="contact-icon">🌐</div>
            <div className="contact-label">Website</div>
            <div className="contact-val">www.vignan.ac.in</div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="footer">
        <div className="footer-brand">
          <div className="footer-logo">V</div>
          <div>
            <div className="footer-name">Vignan's Foundation for Science, Technology & Research</div>
            <div className="footer-copy">© 2025 Vignan's FSTR University. All rights reserved.</div>
          </div>
        </div>
      </footer>

      {/* ── Floating Chatbot ── */}
      <ChatBot />
    </div>
  );
}
