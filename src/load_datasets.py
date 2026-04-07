import os
import json
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

SAMPLE_CASE_TEXTS = [
    "The Supreme Court observed that the conviction under Section 302 IPC based on circumstantial evidence must form a complete chain establishing the guilt of the accused beyond reasonable doubt. The High Court had confirmed the conviction of the appellant who was charged with the murder of his wife. The prosecution case was based entirely on circumstantial evidence including motive, last seen together, and recovery of weapon. The appellant contended that the chain of circumstances was incomplete and the benefit of doubt should be given. After careful examination of the evidence on record, this Court finds that the circumstantial evidence does form a complete chain. The appeal is dismissed.",
    "The bail application under Section 439 CrPC is rejected considering the gravity of the offense charged under Sections 376 and 506 IPC. The petitioner has been charged with serious offenses and the investigation is still ongoing. The learned Sessions Judge had earlier rejected the bail application. The High Court observed that considering the nature of allegations and the evidence collected during investigation, if the petitioner is released on bail, there is every likelihood that the petitioner may tamper with the evidence. The petition is rejected.",
    "This appeal arises out of a judgment of the Delhi High Court whereby the appellant's conviction under Section 420 IPC for cheating was upheld. The appellant had entered into a fraudulent agreement for sale of property. The complainant had paid Rs. 50 lakhs as advance. The trial court convicted the appellant and sentenced him to 5 years rigorous imprisonment. On appeal, the High Court reduced the sentence to 3 years. The Supreme Court, after examining the evidence, found no reason to interfere with the concurrent findings of fact. Appeal dismissed with costs.",
    "The petitioner challenges the order of detention passed under the National Security Act, 1980. The detaining authority had passed the order on grounds of maintenance of public order. The petitioner contends that the grounds of detention are vague and non-specific. After careful examination, this Court finds that the grounds supplied to the detenu are sufficiently specific and enable the detenu to make an effective representation. The writ petition is dismissed.",
    "In the matter of a civil dispute regarding partition of ancestral property under Hindu Succession Act 1956. The plaintiff claims 1/3rd share in the joint family property situated at Rohini, Delhi. The defendant contested the claim stating that the property was self-acquired. After examining the revenue records, sale deeds, and mutation entries, the trial court held that the property was indeed ancestral. The decree for partition is granted in favor of the plaintiff.",
    "The appellant was convicted under Section 304B read with Section 498A IPC for dowry death. The prosecution established that the deceased died within 7 years of marriage and was subjected to cruelty in connection with demand for dowry. Three witnesses including the mother and brother of the deceased deposed about the demand of car and cash as dowry. The medical evidence confirmed death by burn injuries. The conviction is upheld and appeal is dismissed.",
    "This is a petition under Article 226 of the Constitution challenging the termination order issued by the respondent University. The petitioner was appointed as Assistant Professor on ad-hoc basis. The termination was effected without giving any prior notice or opportunity of hearing. The Court finds that principles of natural justice were violated. The termination order is set aside and the petitioner is directed to be reinstated with full back wages.",
    "The accused was charged under Section 307 IPC for attempt to murder. The prosecution case is that the accused attacked the victim with a knife causing grievous injuries. The FIR was lodged after delay of 3 days. The eyewitnesses turned hostile during trial. The medical evidence shows injuries consistent with sharp weapon. However, in absence of reliable ocular evidence and considering the delayed FIR, the benefit of doubt is given to the accused. The accused is acquitted.",
    "The motor accident claim petition was filed by the widow of the deceased who died in a road accident involving a truck. The deceased was 35 years old earning Rs. 40,000 per month. Applying the multiplier of 15, deducting 1/3rd for personal expenses, the tribunal awards compensation of Rs. 60,00,000. The insurance company is directed to pay the amount with 7.5% interest from the date of filing. The claim petition is allowed.",
    "A dispute regarding specific performance of contract for sale of immovable property. The plaintiff entered into an agreement to sell dated 15.03.2015 for purchase of property at Rs. 1.5 crores. The defendant received Rs. 30 lakhs as earnest money but refused to execute the sale deed. The Court finds that the plaintiff was always ready and willing to perform his part of the contract. Decree for specific performance is granted with direction to execute sale deed within 3 months.",
    "Review petition filed against the judgment of this Court in Criminal Appeal challenging conviction under NDPS Act Section 21. The petitioner contends that there was non-compliance with Section 50 of the NDPS Act as the search was conducted without informing the accused of his right to be searched before a Magistrate. After re-examination, the Court finds merit in the contention. The conviction is set aside. The accused is acquitted.",
    "The election petition challenges the election of the returned candidate from Ward No. 15 of the Municipal Corporation on grounds of corrupt practices under Section 123 of the Representation of People Act. The petitioner alleges distribution of money to voters. However, the evidence produced is insufficient to establish corrupt practices beyond reasonable doubt. The election petition is dismissed.",
    "This appeal challenges the assessment order under Section 143(3) of the Income Tax Act for AY 2018-19. The assessing officer had disallowed deduction under Section 80IC claimed by a unit located in Uttarakhand. The ITAT allowed the deduction holding that the assessee had fulfilled all conditions. The Revenue appeals to the High Court. After examining the provision and the facts, the Court finds no infirmity in the ITAT order. Appeal by Revenue is dismissed.",
    "The complainant filed a case under Section 138 of the Negotiable Instruments Act for dishonour of cheque of Rs. 10 lakhs issued by the accused towards repayment of loan. The accused contended that the cheque was issued as security and not towards discharge of any debt. The Magistrate convicted the accused. On appeal, this Court finds that the accused failed to rebut the presumption under Section 139. The conviction is upheld and the accused is directed to pay double the cheque amount as compensation.",
    "Habeas Corpus petition filed by the mother of the detenue who has been detained under the Prevention of Illicit Traffic in Narcotic Drugs Act. The detention order was served on 15.06.2023. The grounds of detention refer to two instances of recovery of contraband substances. The detenue's representation was disposed of after unreasonable delay of 45 days. This Court holds that the inordinate delay in disposing of the representation vitiates the continued detention. The detenue is directed to be released forthwith.",
]

SAMPLE_LABELS = [0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1]

DDL_STATES = {
    1: "Delhi", 2: "Maharashtra", 3: "Tamil Nadu", 4: "Karnataka", 5: "Uttar Pradesh",
    6: "West Bengal", 7: "Gujarat", 8: "Rajasthan", 9: "Madhya Pradesh", 10: "Kerala"
}

DDL_DISPOSITIONS = [
    "Convicted", "Acquitted", "Dismissed", "Allowed", "Stayed",
    "Compounded", "Transferred", "Withdrawn", "Expired", "Abated"
]

DDL_ACT_SECTIONS = [
    ("IPC", "302"), ("IPC", "307"), ("IPC", "376"), ("IPC", "420"), ("IPC", "498A"),
    ("CrPC", "439"), ("CPC", "9"), ("NI Act", "138"), ("NDPS", "21"), ("IT Act", "143"),
    ("HMA", "13"), ("MVA", "166"), ("NSA", "3"), ("RP Act", "123"), ("IEA", "45")
]

PETITIONER_NAMES = [
    "Rajesh Kumar", "Priya Sharma", "Mohammed Iqbal", "Lakshmi Devi", "Suresh Reddy",
    "Fatima Begum", "Anil Mehta", "Geeta Rani", "Harpreet Singh", "Anita Das",
    "Ram Prasad", "Sita Kumari", "Abdul Rehman", "Kavitha Nair", "Deepak Joshi"
]

JUDGE_POSITIONS = [
    "District Judge", "Additional District Judge", "Civil Judge (Senior Division)",
    "Chief Judicial Magistrate", "Metropolitan Magistrate", "Sessions Judge"
]


def load_all_datasets(hdfs_mgr, sample_size=500):
    os.makedirs("data/raw", exist_ok=True)

    ildc_path = "data/raw/ildc.csv"
    if not os.path.exists(ildc_path):
        try:
            from datasets import load_dataset
            logger.info("[Dataset] Attempting to load ILDC from HuggingFace...")
            ildc = load_dataset("Exploration-Lab/IL-TUR", split="single_train")
            df_ildc = pd.DataFrame(ildc).head(sample_size)
            if "text" not in df_ildc.columns:
                raise ValueError("Missing 'text' column")
            logger.info("[Dataset] Loaded %d ILDC cases from HuggingFace.", len(df_ildc))
        except Exception as e:
            logger.warning("[Dataset] HuggingFace load failed: %s. Generating corpus.", str(e))
            np.random.seed(42)
            texts = []
            labels = []
            for i in range(sample_size):
                base = SAMPLE_CASE_TEXTS[i % len(SAMPLE_CASE_TEXTS)]
                label = SAMPLE_LABELS[i % len(SAMPLE_LABELS)]
                texts.append(base)
                labels.append(label)
            df_ildc = pd.DataFrame({"text": texts, "label": labels})
        df_ildc.to_csv(ildc_path, index=False)
    else:
        logger.info("[Dataset] ILDC already exists at %s", ildc_path)

    ddl_path = "data/raw/ddl.csv"
    if not os.path.exists(ddl_path):
        np.random.seed(42)
        n_rows = 3000
        state_codes = np.random.choice(list(DDL_STATES.keys()), n_rows)
        years = np.random.choice(range(2010, 2019), n_rows)
        dispositions = np.random.choice(DDL_DISPOSITIONS, n_rows)
        pet_names = np.random.choice(PETITIONER_NAMES, n_rows)
        resp_names = ["State of " + DDL_STATES[s] for s in state_codes]
        act_sec = [DDL_ACT_SECTIONS[np.random.randint(0, len(DDL_ACT_SECTIONS))] for _ in range(n_rows)]
        judges = np.random.choice(JUDGE_POSITIONS, n_rows)

        df_ddl = pd.DataFrame({
            "state_code": state_codes,
            "state_name": [DDL_STATES[s] for s in state_codes],
            "year": years,
            "type_name": np.random.choice(["Criminal", "Civil", "Motor Accident", "Family", "Revenue"], n_rows),
            "disp_name": dispositions,
            "judge_position": judges,
            "petitioner_name": pet_names,
            "respondent_name": resp_names,
            "act": [a[0] for a in act_sec],
            "section": [a[1] for a in act_sec],
            "gender_proxy": np.random.choice(["Male", "Female"], n_rows, p=[0.65, 0.35]),
            "socioeconomic_proxy": np.random.choice(["Urban", "Rural", "Semi-Urban"], n_rows, p=[0.4, 0.35, 0.25]),
            "outcome": np.random.choice([0, 1], n_rows, p=[0.45, 0.55])
        })
        df_ddl.to_csv(ddl_path, index=False)
        logger.info("[Dataset] Generated DDL dataset with %d rows.", n_rows)
    else:
        logger.info("[Dataset] DDL already exists at %s", ddl_path)

    ipc_path = "data/ipc_statutes.json"
    if not os.path.exists(ipc_path):
        ipc_data = [
            {"section": "302", "title": "Punishment for murder", "description": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.", "punishment": "Death or imprisonment for life, and fine"},
            {"section": "304", "title": "Punishment for culpable homicide not amounting to murder", "description": "Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment for a term which may extend to ten years, and shall also be liable to fine.", "punishment": "Imprisonment for life, or up to 10 years, and fine"},
            {"section": "304B", "title": "Dowry death", "description": "Where the death of a woman is caused by any burns or bodily injury or occurs otherwise than under normal circumstances within seven years of her marriage.", "punishment": "Imprisonment not less than 7 years, may extend to life imprisonment"},
            {"section": "307", "title": "Attempt to murder", "description": "Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder.", "punishment": "Imprisonment up to 10 years, and fine; if hurt caused, imprisonment for life"},
            {"section": "376", "title": "Punishment for rape", "description": "Whoever commits rape shall be punished with rigorous imprisonment of either description for a term which shall not be less than ten years.", "punishment": "Rigorous imprisonment not less than 10 years, may extend to life imprisonment, and fine"},
            {"section": "420", "title": "Cheating and dishonestly inducing delivery of property", "description": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property.", "punishment": "Imprisonment up to 7 years, and fine"},
            {"section": "498A", "title": "Cruelty by husband or relatives of husband", "description": "Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty.", "punishment": "Imprisonment up to 3 years, and fine"},
            {"section": "506", "title": "Punishment for criminal intimidation", "description": "Whoever commits the offence of criminal intimidation.", "punishment": "Imprisonment up to 2 years, or fine, or both"},
            {"section": "34", "title": "Acts done by several persons in furtherance of common intention", "description": "When a criminal act is done by several persons in furtherance of the common intention of all.", "punishment": "Each person liable as if done by him alone"},
            {"section": "120B", "title": "Punishment of criminal conspiracy", "description": "Whoever is a party to a criminal conspiracy to commit an offence punishable with death or imprisonment for life.", "punishment": "Same as abetment of the offence"},
            {"section": "149", "title": "Every member of unlawful assembly guilty of offence committed in prosecution of common object", "description": "If an offence is committed by any member of an unlawful assembly in prosecution of the common object.", "punishment": "Same as if committed by that member"},
            {"section": "295A", "title": "Deliberate and malicious acts, intended to outrage religious feelings", "description": "Whoever, with deliberate and malicious intention of outraging the religious feelings of any class of citizens of India.", "punishment": "Imprisonment up to 3 years, or fine, or both"},
            {"section": "354", "title": "Assault or criminal force to woman with intent to outrage her modesty", "description": "Whoever assaults or uses criminal force to any woman, intending to outrage or knowing it to be likely that he will thereby outrage her modesty.", "punishment": "Imprisonment not less than 1 year, may extend to 5 years, and fine"},
            {"section": "379", "title": "Punishment for theft", "description": "Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.", "punishment": "Imprisonment up to 3 years, or fine, or both"},
            {"section": "406", "title": "Punishment for criminal breach of trust", "description": "Whoever commits criminal breach of trust shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.", "punishment": "Imprisonment up to 3 years, or fine, or both"},
        ]
        with open(ipc_path, "w", encoding="utf-8") as f:
            json.dump(ipc_data, f, indent=2)
        logger.info("[Dataset] Created IPC statutes with %d sections.", len(ipc_data))

    hc_path = "data/raw/hc.csv"
    if not os.path.exists(hc_path):
        np.random.seed(42)
        n = 500
        hc_data = pd.DataFrame({
            "case_type": np.random.choice(["Bail Application", "Criminal Appeal", "Writ Petition", "Civil Revision", "Motor Accident Claim"], n),
            "year": np.random.choice(range(2010, 2024), n),
            "state": np.random.choice(["Delhi", "Mumbai", "Chennai", "Kolkata", "Bangalore", "Hyderabad", "Lucknow", "Jaipur"], n),
            "outcome": np.random.choice(["Allowed", "Dismissed", "Partly Allowed", "Remanded"], n, p=[0.35, 0.40, 0.15, 0.10]),
            "case_name": [f"High Court Case #{i+1}" for i in range(n)]
        })
        hc_data.to_csv(hc_path, index=False)
        logger.info("[Dataset] Generated High Court dataset with %d cases.", n)

    ltc_path = "data/raw/ltc.csv"
    if not os.path.exists(ltc_path):
        np.random.seed(42)
        n = 300
        case_types = ["Criminal", "Civil", "Constitutional", "Family", "Revenue", "Motor Accident"]
        ltc_texts = [
            "Murder and criminal conspiracy charges under IPC",
            "Civil suit for recovery of money and damages",
            "Writ petition challenging constitutional validity of statute",
            "Matrimonial dispute regarding custody of minor child",
            "Revenue dispute regarding assessment of property tax",
            "Motor accident claim for compensation due to negligence"
        ]
        ltc_data = pd.DataFrame({
            "text": [ltc_texts[i % len(ltc_texts)] for i in range(n)],
            "label": [case_types[i % len(case_types)] for i in range(n)]
        })
        ltc_data.to_csv(ltc_path, index=False)
        logger.info("[Dataset] Generated Legal Text Classification dataset with %d entries.", n)

    hdfs_mgr.mkdir("raw")
    hdfs_mgr.upload("data/raw/ildc.csv", "raw/ildc.csv")
    hdfs_mgr.upload("data/raw/ddl.csv", "raw/ddl.csv")
    hdfs_mgr.upload("data/ipc_statutes.json", "raw/ipc_statutes.json")
    hdfs_mgr.upload("data/raw/hc.csv", "raw/hc.csv")
    hdfs_mgr.upload("data/raw/ltc.csv", "raw/ltc.csv")

    logger.info("[Dataset] All datasets loaded and uploaded to HDFS.")
    return {
        "ildc": ildc_path,
        "ddl": ddl_path,
        "ipc": ipc_path,
        "hc": hc_path,
        "ltc": ltc_path
    }
