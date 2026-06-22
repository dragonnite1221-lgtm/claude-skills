# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_subject_rights_tracker_base import *  # noqa: F403,E402


class RightsTrackerMixin2:
    def generate_response_template(self, request_id: str) -> Optional[str]:
        """Generate response template for a request."""
        req = self.get_request(request_id)
        if not req:
            return None

        right_info = RIGHTS_TYPES.get(req["type"], {})
        template = f"""
Subject: Response to Your {right_info.get('name', 'Data Subject')} Request ({req['id']})

Dear {req['subject']['name']},

Thank you for your request dated {req['dates']['received'][:10]} exercising your {right_info.get('name', 'data protection right')} under {right_info.get('article', 'GDPR')}.

We have processed your request and respond as follows:

[RESPONSE DETAILS HERE]

"""
        if req["type"] == "access":
            template += """
As required under Article 15, we provide the following information:

1. Purposes of Processing:
   [List purposes]

2. Categories of Personal Data:
   [List categories]

3. Recipients:
   [List recipients or categories]

4. Retention Period:
   [Specify period or criteria]

5. Your Rights:
   - Right to rectification (Art. 16)
   - Right to erasure (Art. 17)
   - Right to restriction (Art. 18)
   - Right to object (Art. 21)
   - Right to lodge complaint with supervisory authority

6. Source of Data:
   [Specify if not collected from you directly]

7. Automated Decision-Making:
   [Confirm if applicable and provide meaningful information]

Enclosed: Copy of your personal data
"""
        elif req["type"] == "erasure":
            template += """
We confirm that your personal data has been erased from our systems, except where:
- We are legally required to retain it
- It is necessary for legal claims
- [Other applicable exceptions]

We have also notified the following recipients of the erasure:
[List recipients]
"""
        elif req["type"] == "portability":
            template += """
Please find attached your personal data in [JSON/CSV] format.

This includes all data:
- Provided by you
- Processed based on your consent or contract
- Processed by automated means

You may transmit this data to another controller or request direct transmission where technically feasible.
"""

        template += f"""
If you have any questions about this response, please contact our Data Protection Officer at [DPO EMAIL].

If you are not satisfied with our response, you have the right to lodge a complaint with the supervisory authority:
[SUPERVISORY AUTHORITY DETAILS]

Yours sincerely,
[CONTROLLER NAME]
Data Protection Team

Reference: {req['id']}
"""
        return template
