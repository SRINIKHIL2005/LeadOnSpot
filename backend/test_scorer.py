import unittest

from scorer import calculate_score


class CalculateScoreTests(unittest.TestCase):
    def test_hot_lead_founder_at_it_company(self):
        lead = {
            "name": "Rahul Sharma",
            "company_name": "ABC Technologies",
            "website": "www.abctechnologies.com",
            "job_title": "Founder",
            "industry": "IT Services",
            "company_location": "Bangalore",
            "company_size": "50–100",
            "lead_source": "Website",
            "requirement": "Looking for CRM software to manage sales pipeline and customer data",
            "email": "rahul@example.com",
            "phone": "+91 9876543210",
        }
        self.assertEqual(calculate_score(lead)["classification"], "Hot")

    def test_warm_lead_manager_at_small_company(self):
        lead = {
            "name": "Priya Mehta",
            "company_name": "Retail Co",
            "job_title": "Manager",
            "industry": "Retail",
            "company_size": "20–50",
            "lead_source": "Cold Call",
            "requirement": "Need a tool",
            "email": "priya@retailco.com",
        }
        self.assertEqual(calculate_score(lead)["classification"], "Warm")

    def test_cold_lead_intern_with_minimal_data(self):
        lead = {
            "name": "Amit",
            "job_title": "Intern",
            "company_size": "1–5",
            "lead_source": "Outbound",
        }
        self.assertEqual(calculate_score(lead)["classification"], "Cold")

    def test_hot_lead_ceo_at_enterprise(self):
        lead = {
            "name": "Sarah Johnson",
            "company_name": "FinTech Corp",
            "job_title": "CEO",
            "industry": "Fintech",
            "company_size": "500–1000",
            "lead_source": "Referral",
            "requirement": (
                "Looking to implement a CRM and sales automation platform to replace legacy system"
            ),
            "email": "sarah@fintechcorp.com",
            "phone": "+1 555 0100",
            "website": "www.fintechcorp.com",
        }
        self.assertEqual(calculate_score(lead)["classification"], "Hot")

    def test_same_input_produces_same_score(self):
        lead = {
            "name": "Test User",
            "job_title": "Director",
            "industry": "Software",
            "company_size": "100–200",
            "lead_source": "LinkedIn",
            "requirement": "Need CRM software",
            "email": "test@test.com",
        }
        first = calculate_score(lead)
        second = calculate_score(lead)
        self.assertEqual(first["final_score"], second["final_score"])
        self.assertEqual(first["classification"], second["classification"])

    def test_missing_fields_are_scored_as_cold(self):
        lead = {"name": "Unknown", "email": "x@x.com"}
        self.assertEqual(calculate_score(lead)["classification"], "Cold")


if __name__ == "__main__":
    unittest.main()
