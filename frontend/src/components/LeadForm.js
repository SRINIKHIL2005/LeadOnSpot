import { useState } from "react";

const INITIAL = {
  name: "", company_name: "", website: "", job_title: "",
  industry: "", company_location: "", company_size: "",
  lead_source: "", requirement: "", email: "", phone: "",
};

const FIELDS = [
  { key: "name", label: "Full Name", placeholder: "Rahul Sharma" },
  { key: "company_name", label: "Company Name", placeholder: "ABC Technologies" },
  { key: "website", label: "Website", placeholder: "www.abctechnologies.com" },
  { key: "job_title", label: "Job Title", placeholder: "Founder" },
  { key: "industry", label: "Industry", placeholder: "IT Services" },
  { key: "company_location", label: "Company Location", placeholder: "Bangalore" },
  { key: "company_size", label: "Company Size", placeholder: "50–100 Employees" },
  { key: "lead_source", label: "Lead Source", placeholder: "Website" },
  { key: "email", label: "Email", placeholder: "rahul@example.com", type: "email" },
  { key: "phone", label: "Phone", placeholder: "+91 9876543210", type: "tel" },
];

export default function LeadForm({ onSubmit, loading }) {
  const [form, setForm] = useState(INITIAL);
  const [validationError, setValidationError] = useState("");

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setValidationError("");
  }

  function handleSubmit(e) {
    e.preventDefault();
    const trimmedName = form.name.trim().normalize("NFC");
    if (trimmedName && !isValidName(trimmedName)) {
      setValidationError(
        "Name must contain letters; numbers and symbols are not allowed."
      );
      return;
    }

    const filledFields = Object.values(form).filter((value) => value.trim()).length;
    if (filledFields < 2) {
      setValidationError("Please enter at least two fields to score a lead.");
      return;
    }

    setValidationError("");
    onSubmit(
      Object.fromEntries(
        Object.entries(form).map(([key, value]) => [key, value.trim()])
      )
    );
  }

  function handleReset() {
    setForm(INITIAL);
    setValidationError("");
  }

  function fillSample() {
    setForm({
      name: "Rahul Sharma",
      company_name: "ABC Technologies",
      website: "www.abctechnologies.com",
      job_title: "Founder",
      industry: "IT Services",
      company_location: "Bangalore",
      company_size: "50–100",
      lead_source: "Website",
      requirement: "Looking for CRM software to manage sales pipeline and customer data",
      email: "rahul@example.com",
      phone: "+91 9876543210",
    });
  }

  return (
    <div className="form-card">
      <div className="form-header">
        <h2>Enter Lead Information</h2>
        <button type="button" className="btn-sample" onClick={fillSample}>
          Load Sample Lead
        </button>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {FIELDS.map(({ key, label, placeholder, type }) => (
            <div className="field-group" key={key}>
              <label htmlFor={key}>{label}</label>
              <input
                id={key}
                name={key}
                type={type || "text"}
                placeholder={placeholder}
                maxLength={key === "name" ? 100 : undefined}
                aria-invalid={key === "name" && Boolean(validationError)}
                value={form[key]}
                onChange={handleChange}
              />
            </div>
          ))}
          <div className="field-group full-width">
            <label htmlFor="requirement">Requirement</label>
            <textarea
              id="requirement"
              name="requirement"
              placeholder="Looking for CRM software to manage sales pipeline..."
              value={form.requirement}
              onChange={handleChange}
              rows={3}
            />
          </div>
        </div>
        {validationError && (
          <div className="error-box" role="alert">
            {validationError}
          </div>
        )}
        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={handleReset}>
            Clear
          </button>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Scoring..." : "Score This Lead →"}
          </button>
        </div>
      </form>
    </div>
  );
}

function isValidName(value) {
  const allowedPunctuation = new Set([" ", "'", "’", "-", "."]);
  const chars = Array.from(value);
  return (
    chars.some((char) => char.toLowerCase() !== char.toUpperCase()) &&
    chars.every(
      (char) =>
        char.toLowerCase() !== char.toUpperCase() ||
        /^\p{M}$/u.test(char) ||
        allowedPunctuation.has(char)
    )
  );
}
