# OWASP Juice Shop: Playwright Test Scripts

SOFTEST BTIS1 (20252) - Group 1
De La Salle - College of Saint Benilde

## Workflows Automated
- **Script 1:** 'test_wf1_registration_login.py' - Workflow 1: User Registration & Login (TC-001 to TC-005)
- **Script 2:** 'test_wf2_browsing_search.py' - Workflow 2: Product Browsing & Search (TC-006 to TC-010)

## How to Run
### 1. Install dependencies
pip install pytest playwright
python -m playwright install chromium

### 2. Run Script 1
pytest test_wf1_registration_login.py -v -s

### 3. Run Script 2
pytest test_wf2_browsing_search.py -v -s