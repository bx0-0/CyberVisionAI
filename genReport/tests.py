import markdown

def generate_x_mini_template(bug_name, asset, step_to_reproduce, POC, severity, response):
    return f"""
# Penetration Testing Report

---

## Report Summary
**Date:**  
**Report ID:**  
**Reported by:**  
**Target Asset:** {asset}

---

## 1. Vulnerability Overview

- **Vulnerability Name:** {bug_name}
- **Severity:** {severity}
- **Affected Asset:** {asset}

---

## 2. Steps to Reproduce

**Step-by-Step Reproduction:**

{step_to_reproduce}

> *Note: The steps to reproduce have been documented as provided by the user.*

---

## 3. Proof of Concept (POC)

### POC Details
{POC}

> *Note: POC details are retained as provided by the user.*

---

{response}

---

## 7. Summary Table

| Section              | Details                      |
|----------------------|------------------------------|
| Vulnerability Name   | {bug_name}                   |
| Severity             | {severity}                   |
| Asset                | {asset}                      |

---

> **Disclaimer:** This report is intended solely for the recipient organization. Unauthorized disclosure, duplication, or distribution of this report is prohibited.
"""

def generate_html_report(bug_name, asset, step_to_reproduce, POC, severity, response):
    # Generate the Markdown report
    markdown_content = generate_x_mini_template(bug_name, asset, step_to_reproduce, POC, severity, response)
    
    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_content, extensions=['tables'])
    
    # Wrap in basic HTML structure
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Penetration Testing Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
            h1, h2, h3 {{ color: #2C3E50; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            table, th, td {{ border: 1px solid #ddd; }}
            th, td {{ padding: 8px; text-align: left; }}
            th {{ background-color: #f4f4f4; }}
            blockquote {{ font-style: italic; color: #555; margin: 10px 0; padding-left: 10px; border-left: 4px solid #ddd; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    return html_template


bug_name = "SQL Injection"
asset = "www.example.com"
step_to_reproduce = "1. Access the login page\n2. Inject SQL payload"
POC = "Payload: ' OR '1'='1"
severity = "High"
response = "This vulnerability allows attackers to bypass authentication."

html_report = generate_html_report(bug_name, asset, step_to_reproduce, POC, severity, response)

# Save to file or use as needed
with open("penetration_testing_report.html", "w") as file:
    file.write(html_report)

print("HTML report generated successfully.")
