def symptom_agent(symptom):

    symptom = symptom.lower()

    findings = []

    if "headache" in symptom:
        findings.append(
            "Possible migraine, dehydration, stress, or infection."
        )

    if "fever" in symptom:
        findings.append(
            "Possible viral or bacterial infection."
        )

    if "stomach" in symptom:
        findings.append(
            "Possible gastritis, food poisoning, or digestive issue."
        )

    if "chest pain" in symptom:
        findings.append(
            "Could indicate cardiac or respiratory issue."
        )

    if findings:
        return "\n".join(findings)

    return "No clear symptom match found."