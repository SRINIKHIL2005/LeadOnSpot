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
    const formError = validateForm(form);
    if (formError) {
      setValidationError(formError);
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

function validateForm(form) {
  const name = form.name.trim().normalize("NFC");
  if (name && (
    !/\p{L}/u.test(name) ||
    !/^[\p{L}\p{M}\s'’.-]+$/u.test(name)
  )) {
    return "Name must contain letters; numbers and symbols are not allowed.";
  }

  const textFields = [
    ["company_name", "Company name"],
    ["website", "Website"],
    ["job_title", "Job title"],
    ["industry", "Industry"],
    ["company_location", "Company location"],
    ["lead_source", "Lead source"],
    ["requirement", "Requirement"],
  ];

  for (const [key, label] of textFields) {
    const value = form[key].trim();
    if (!value) continue;
    if (/^[+-]?0+(?:[.,]0+)?$/.test(value)) {
      return `${label} cannot be zero; enter real information or leave it blank.`;
    }
    if (!/\p{L}/u.test(value)) {
      return `${label} must contain letters.`;
    }
  }

  const companySize = form.company_size.trim();
  if (companySize) {
    if (!/^\d[\d,]*(?:\s*(?:-|–|—|to)\s*\d[\d,]*)?\s*\+?(?:\s+(?:employees?|people|staff))?$/i.test(companySize)) {
      return "Enter a company size as a count or range, such as 50-100 employees.";
    }
    const employeeCounts = companySize.replace(/,/g, "").match(/\d+/g) || [];
    if (!employeeCounts.some((count) => Number(count) > 0)) {
      return "Company size must include a positive employee count, such as 50-100.";
    }
  }

  const phone = form.phone.trim();
  if (phone) {
    const digits = phone.replace(/\D/g, "");
    if (!/^[+0-9(). /-]+$/.test(phone) || digits.length < 7 || digits.length > 15) {
      return "Enter a valid phone number containing 7 to 15 digits.";
    }
  }

  const website = form.website.trim();
  if (website) {
    const domain = website.replace(/^https?:\/\//i, "").split("/")[0].split(":")[0];
    if (
      !domain.includes(".") ||
      /\s/.test(website) ||
      !/^[a-z0-9.-]+$/i.test(domain)
    ) {
      return "Enter a valid website, such as www.example.com.";
    }
  }

  const email = form.email.trim();
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return "Enter a valid email address.";
  }

  const filledFields = Object.values(form).filter((value) => value.trim()).length;
  if (filledFields < 2) {
    return "Please enter at least two fields to score a lead.";
  }

  return "";
}
