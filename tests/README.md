Running tests and generating reports

Prerequisites:
- pytest
- pytest-html (for the HTML report)
- allure-pytest and the Allure CLI (optional) to generate a richer Allure report

Installing dependencies (Windows / conda)

1) Activate your conda env (e.g., ai-backend)

```
conda activate ai-backend
pip install pytest pytest-html allure-pytest playwright faker requests
playwright install
```

2) Optional: install Allure CLI on Windows (Chocolatey)

```
choco install allure
```


Quick commands:

Run register tests and produce HTML + Allure results:

```
cd "D:\Data Mining\hus-ai-translator"
pytest tests -k register --headed --slow-mo=200
```

If you have the Allure CLI installed, you can generate the Allure report:

```
allure generate tests/register/logs/allure-results -o tests/register/logs/allure-report --clean
allure open tests/register/logs/allure-report
```

Windows users: use the helper script at `scripts/run_tests_with_reports.bat`.
Python UI smoke tests (Playwright + pytest)

Setup:

1. Create and activate a Python environment (venv or conda)

2. Install requirements:

   pip install -r requirements.txt

3. Install Playwright browsers:

   python -m playwright install

Run tests:

   pytest -q

The sample test expects the frontend dev server to be running at http://localhost:3000
