"""
VoxMed_AI - MedlinePlus Data Fetcher
"""

import os
import time
import requests
import xml.etree.ElementTree as ET

DATA_DIR = "data"
BASE_URL = "https://wsearch.nlm.nih.gov/ws/query"

TOPICS = [
    "first aid", "burns", "fever", "choking", "sprains and strains",
    "nosebleeds", "allergic reaction", "wounds and injuries", "poisoning",
    "heat exhaustion", "diabetes", "high blood pressure", "asthma",
    "migraine", "urinary tract infections", "kidney stones", "heart attack",
    "stroke", "pneumonia", "bronchitis", "gastritis", "food poisoning",
    "dehydration", "dengue fever", "malaria", "typhoid fever", "covid 19",
    "flu", "common cold", "tuberculosis", "anemia", "thyroid diseases",
    "arthritis", "back pain", "depression", "anxiety", "insomnia",
    "constipation", "diarrhea", "vomiting", "headache", "dizziness",
    "high cholesterol", "obesity", "skin rash", "eczema", "acne",
    "conjunctivitis", "ear infections", "sinusitis", "tonsillitis",
    "appendicitis", "gallstones", "hemorrhoids", "varicose veins",
    "osteoporosis", "seizures", "chickenpox", "measles", "pink eye",
    "sore throat", "abdominal pain", "chest pain",
]


def fetch_topic(topic):
    params = {"db": "healthTopics", "term": topic, "rettype": "brief"}
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    documents = root.findall(".//document")
    if not documents:
        return None

    doc = documents[0]
    title = doc.get("title", topic)

    summary = ""
    for content in doc.findall("content"):
        if content.get("name") == "FullSummary":
            import re
            raw = content.text or ""
            summary = re.sub("<[^<]+?>", "", raw)
            break

    if not summary:
        return None

    return f"Title: {title}\nSource: MedlinePlus (medlineplus.gov)\n\n{summary.strip()}\n"


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Fetching {len(TOPICS)} topics from MedlinePlus...")

    for topic in TOPICS:
        print(f"  - {topic} ...", end=" ")
        try:
            text = fetch_topic(topic)
        except Exception as e:
            print(f"failed ({e})")
            continue

        if text is None:
            print("no result found")
            continue

        filename = topic.lower().replace(" ", "_") + ".txt"
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"saved -> {filepath}")

        time.sleep(1)

    print("\nDone. Now run: python ingest.py")


if __name__ == "__main__":
    main()