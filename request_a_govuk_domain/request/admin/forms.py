from django import forms


class ReviewForm(forms.ModelForm):
    class Meta:
        labels = {
            "registrar_details": "Status",
            "registrar_details_notes": "Evidence",
            "domain_name_availability": "Status",
            "domain_name_availability_notes": "Evidence",
            "registrant_org": "Status",
            "registrant_org_notes": "Evidence",
            "registrant_person": "Status",
            "registrant_person_notes": "Evidence",
            "registrant_permission": "Status",
            "registrant_permission_notes": "Evidence",
            "policy_exemption": "Status",
            "policy_exemption_notes": "Evidence",
            "domain_name_rules": "Status",
            "domain_name_rules_notes": "Evidence",
            "registrant_senior_support": "Status",
            "registrant_senior_support_notes": "Evidence",
            "reason": "Reason",
        }
