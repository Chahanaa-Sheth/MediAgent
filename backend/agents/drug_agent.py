import requests

def drug_interaction_agent(drug_name):

    url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{drug_name}&limit=1"

    try:

        response = requests.get(url)

        data = response.json()

        result = data["results"][0]

        warnings = result.get("warnings", ["No warnings found"])

        adverse = result.get(
            "adverse_reactions",
            ["No adverse reactions found"]
        )

        return f"""
DRUG ANALYSIS FOR: {drug_name}

WARNINGS:
{warnings[0]}

ADVERSE REACTIONS:
{adverse[0]}
"""

    except Exception:

        return "No FDA data found for this drug."