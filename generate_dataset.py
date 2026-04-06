"""
Generate Realistic Judicial Dataset for Demo
Creates 75+ diverse legal cases with realistic attributes
"""

import csv
import random
import os

# Realistic legal case templates
CRIMES = [
    "Aggravated Assault", "Armed Robbery", "Burglary", "Drug Trafficking",
    "Embezzlement", "Fraud", "Homicide", "Identity Theft", "Larceny", "Money Laundering",
    "Rape", "Racketeering", "Theft", "Vehicle Theft", "Vehicular Manslaughter",
    "White Collar Crime", "Cybercrime", "Tax Evasion", "Arson", "Perjury"
]

REGIONS = ["North", "South", "East", "West", "Central", "Northeast", "Southeast", "Midwest"]
COURTS = ["District Court", "Superior Court", "Supreme Court", "Federal Court", "Tax Court"]
OUTCOMES = ["Guilty", "Acquitted", "Mistrial", "Plea Agreement", "Dismissed"]

CASE_TEMPLATES = [
    {
        "facts": "The defendant was found in possession of {crime} materials near the victim's residence. "
                 "Security footage showed the defendant at the crime scene at {time}. "
                 "DNA evidence from the scene matched the defendant's profile with 99.9% accuracy.",
        "legal_issues": "{crime} charges, Evidence admissibility, Chain of custody, {legal_point}"
    },
    {
        "facts": "Multiple witnesses testified that they saw the defendant {action} at the location of the alleged {crime}. "
                 "The defendant's phone records show location data consistent with prosecution's timeline. "
                 "Defendant claims alibi but witnesses contradict this account.",
        "legal_issues": "Eyewitness testimony reliability, Digital forensics, Alibi defense, {legal_point}"
    },
    {
        "facts": "Financial records show unauthorized transfers totaling ${amount} from victim's account to defendant's account. "
                 "Email correspondence reveals defendant's knowledge of the {crime}. "
                 "Defendant admits to transactions but claims these were authorized by victim.",
        "legal_issues": "{crime} charges, Financial fraud, Intent to commit {crime}, {legal_point}"
    },
    {
        "facts": "Defendant was arrested with {item} seconds after the alleged {crime}. "
                 "Forensic analysis shows defendant's fingerprints on the {item}. "
                 "Defendant's clothing contained residue consistent with the crime scene.",
        "legal_issues": "Circumstantial evidence, Forensic analysis, Timeline analysis, {legal_point}"
    },
    {
        "facts": "Witness testimony alleges defendant committed {crime} in presence of multiple people. "
                 "Police body camera captures defendant's initial confession on scene. "
                 "Defendant later recants statement, claiming coercion.",
        "legal_issues": "Confession validity, Miranda Rights, Police conduct, {legal_point}"
    }
]

LEGAL_POINTS = [
    "Probative value of evidence",
    "Right to counsel",
    "Inadmissible hearsay",
    "Search and seizure",
    "Due process",
    "Burden of proof",
    "Expert witness qualification",
    "Cross-examination reliability"
]

OUTCOMES_DATA = {
    "Guilty": {"confidence": (0.7, 0.99), "reason": "Sufficient evidence presented"},
    "Acquitted": {"confidence": (0.6, 0.95), "reason": "Reasonable doubt established"},
    "Mistrial": {"confidence": (0.5, 0.85), "reason": "Procedural irregularities"},
    "Plea Agreement": {"confidence": (0.6, 0.9), "reason": "Defendant acceptance"}
}

def generate_case(case_id):
    """Generate a single realistic judicial case"""
    crime = random.choice(CRIMES)
    region = random.choice(REGIONS)
    court = random.choice(COURTS)
    outcome = random.choice(OUTCOMES)
    template = random.choice(CASE_TEMPLATES)
    legal_point = random.choice(LEGAL_POINTS)
    
    # Format the template
    facts = template["facts"].format(
        crime=crime.lower(),
        time=random.choice(["08:00 PM", "10:30 PM", "11:45 PM", "1:30 AM", "3:00 AM"]),
        action=random.choice(["walking", "running", "entering", "leaving", "disposing of evidence"]),
        amount=random.randint(5000, 500000),
        item=random.choice(["weapon", "contraband", "stolen goods", "evidence"])
    )
    
    legal_issues = template["legal_issues"].format(
        crime=crime.lower(),
        legal_point=legal_point
    )
    
    # Determine case outcome details
    outcome_data = OUTCOMES_DATA.get(outcome, {"confidence": (0.6, 0.85), "reason": "Court decision"})
    confidence = random.uniform(outcome_data["confidence"][0], outcome_data["confidence"][1])
    
    return {
        "case_id": f"CASE_{case_id:04d}",
        "title": f"{region} vs {crime} Case {case_id}",
        "year": random.randint(2015, 2024),
        "region": region,
        "court": court,
        "crime": crime,
        "facts": facts,
        "legal_issues": legal_issues,
        "outcome": outcome,
        "confidence": round(confidence, 2),
        "judge": f"Judge_{random.randint(1, 50)}",
        "prosecution": f"Prosecutor_{random.randint(1, 30)}",
        "defense": f"Attorney_{random.randint(1, 40)}",
        "sentence_months": random.randint(6, 480) if outcome == "Guilty" else 0,
        "appeal_filed": random.choice(["Yes", "No"]),
        "sentiment": random.choice(["Favorable", "Unfavorable", "Neutral"])
    }

def generate_dataset(num_cases=75, output_file="data/judicial_cases.csv"):
    """Generate complete dataset"""
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    cases = []
    print(f"Generating {num_cases} judicial cases...")
    
    for i in range(1, num_cases + 1):
        case = generate_case(i)
        cases.append(case)
        if i % 15 == 0:
            print(f"  Generated {i}/{num_cases} cases...")
    
    # Write to CSV
    if cases:
        keys = cases[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(cases)
    
    print(f"✓ Dataset saved to {output_file} ({num_cases} cases)")
    return output_file

if __name__ == "__main__":
    generate_dataset(75)
