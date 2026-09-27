"""
Generates realistic benchmark datasets for testing the entity resolution pipeline.
Includes realistic noise: typos, legal suffixes, address formats, US/IN/FR markets, singletons.
"""

import os
import random
import csv

BUSINESS_TEMPLATES = [
    ("Apex Technologies Corp", "1042 Market Street Suite 400, San Francisco, CA 94103", "US"),
    ("Summit Retail Solutions Inc", "550 West 34th Street, New York, NY 10001", "US"),
    ("BlueWave Logistics LLC", "820 Logistics Parkway, Dallas, TX 75261", "US"),
    ("Horizon Financial Group", "200 South Wacker Dr 15th Fl, Chicago, IL 60606", "US"),
    ("NextGen Health Services", "1200 Beacon St, Boston, MA 02446", "US"),
    ("Starlight Hospitality Co", "777 Las Vegas Blvd S, Las Vegas, NV 89109", "US"),
    ("Pinnacle Construction & Engineering", "410 Industrial Rd, Seattle, WA 98101", "US"),
    ("Vanguard Media Solutions", "9000 Sunset Blvd, West Hollywood, CA 90069", "US"),
    ("Quantum Software Labs", "3000 Sand Hill Road, Menlo Park, CA 94025", "US"),
    ("Evergreen Agro Products", "1500 Farm Road 50, Des Moines, IA 50301", "US"),
    ("Tata Consultancy Services Ltd", "Nirlon Knowledge Park Goregaon East, Mumbai 400063", "India"),
    ("Infosys Technologies Ltd", "Electronics City Hosur Road, Bengaluru 560100", "India"),
    ("Reliance Retail Private Limited", "Court House Lokmanya Tilak Marg Dhobi Talao, Mumbai 400002", "India"),
    ("Wipro Enterprises Pvt Ltd", "Doddakannelli Sarjapur Road, Bangalore 560035", "India"),
    ("Bharti Airtel Telecommunications", "Plot No 16 Udyog Vihar Phase IV, Gurgaon 122015", "India"),
    ("Apollo Hospitals Enterprise Ltd", "21 Greams Lane Off Greams Road, Chennai 600006", "India"),
    ("Larsen & Toubro Construction", "Mount Poonamallee Road Manapakkam, Chennai 600089", "India"),
    ("Mahindra & Mahindra Automotive", "Gateway Building Apollo Bunder, Mumbai 400001", "India"),
    ("HCL Technologies Private Ltd", "Technology Hub Plot 3A Sector 126, Noida 201304", "India"),
    ("Sun Pharmaceutical Industries Ltd", "Sun House Plot No 201 B 1 Western Express Highway Goregaon East, Mumbai 400063", "India"),
    # France entities for test set
    ("Dassault Aviation SA", "78 Quai Marcel Dassault, Saint-Cloud 92214", "France"),
    ("Carrefour Hypermarche SAS", "93 Avenue de Paris, Massy 91300", "France"),
    ("TotalEnergies Solutions SE", "2 Place Jean Millier La Defense 6, Courbevoie 92400", "France"),
    ("L'Oreal Produits Professionnels", "14 Rue Royale, Paris 75008", "France"),
    ("Sanofi Sante Publique", "46 Avenue de la Grande Armee, Paris 75017", "France"),
]

def mutate_name(name):
    variations = [
        name.replace("Technologies", "Tech").replace("Corp", "Corporation"),
        name.replace("Solutions", "Sol").replace("Inc", "Incorporated"),
        name.replace("Private Limited", "Pvt Ltd").replace("&", "and"),
        name.replace("Enterprises", "Ent").replace("Pvt Ltd", "Private Ltd"),
        name.replace("Ltd", "Limited").replace("Co", "Company"),
        name.replace("SA", "Societe Anonyme").replace("SAS", "S.A.S."),
        name.lower(),
        name.upper()
    ]
    return random.choice(variations)

def mutate_address(addr):
    variations = [
        addr.replace("Street", "St").replace("Suite", "Ste"),
        addr.replace("Road", "Rd").replace("Dr", "Drive"),
        addr.replace("Boulevard", "Blvd").replace("Avenue", "Ave"),
        addr.replace("Floor", "Fl").replace("Near", "Opposite"),
        addr.replace("Bangalore", "Bengaluru"),
        addr.lower()
    ]
    return random.choice(variations)

def generate_datasets(train_dir, test_dir):
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    
    # 1. Training set (US and India)
    train_templates = [t for t in BUSINESS_TEMPLATES if t[2] in ("US", "India")]
    
    s1_train, s2_train, s3_train = [], [], []
    ground_truth = []
    
    s2_counter = 1
    s3_counter = 1
    
    for i, (name, addr, country) in enumerate(train_templates, 1):
        s1_id = f"S1-{i:05d}"
        s1_train.append((s1_id, name, addr, country))
        
        matches = []
        # Case 1: Match in S2
        if random.random() > 0.3:
            s2_id = f"S2-{s2_counter:05d}"
            s2_counter += 1
            s2_train.append((s2_id, mutate_name(name), mutate_address(addr), country))
            matches.append(s2_id)
            
        # Case 2: Match in S3
        if random.random() > 0.4:
            s3_id = f"S3-{s3_counter:05d}"
            s3_counter += 1
            s3_train.append((s3_id, mutate_name(name), mutate_address(addr), country))
            matches.append(s3_id)
            
        # Some entities remain singletons (empty matches)
        ground_truth.append((s1_id, ",".join(matches)))
        
    # Add some distractor records in S2 and S3 (unmatched businesses)
    for _ in range(10):
        s2_id = f"S2-{s2_counter:05d}"
        s2_counter += 1
        s2_train.append((s2_id, f"Random Unmatched Business {s2_counter}", "100 Broadway, New York, NY", "US"))
        
        s3_id = f"S3-{s3_counter:05d}"
        s3_counter += 1
        s3_train.append((s3_id, f"Distinct Distractor Entity {s3_counter}", "MG Road, Pune 411001", "India"))
        
    # Write Train TSVs
    for filename, data, header in [
        (os.path.join(train_dir, "train_source1.tsv"), s1_train, ["entity_id", "business_name", "business_address", "country"]),
        (os.path.join(train_dir, "train_source2.tsv"), s2_train, ["entity_id", "business_name", "business_address", "country"]),
        (os.path.join(train_dir, "train_source3.tsv"), s3_train, ["entity_id", "business_name", "business_address", "country"]),
        (os.path.join(train_dir, "train_ground_truth.tsv"), ground_truth, ["source1_entity_id", "matched_entity_ids"]),
    ]:
        with open(filename, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(header)
            w.writerows(data)
            
    print(f"Generated training data in {train_dir}: S1={len(s1_train)}, S2={len(s2_train)}, S3={len(s3_train)}")
    
    # 2. Test set (US, India, and France)
    test_templates = BUSINESS_TEMPLATES  # includes France
    s1_test, s2_test, s3_test = [], [], []
    s2_t_counter = 1
    s3_t_counter = 1
    
    for i, (name, addr, country) in enumerate(test_templates, 1):
        s1_id = f"S1-{i:05d}"
        s1_test.append((s1_id, name, addr, country))
        
        # Matches in S2 / S3
        if random.random() > 0.25:
            s2_id = f"S2-{s2_t_counter:05d}"
            s2_t_counter += 1
            s2_test.append((s2_id, mutate_name(name), mutate_address(addr), country))
            
        if random.random() > 0.35:
            s3_id = f"S3-{s3_t_counter:05d}"
            s3_t_counter += 1
            s3_test.append((s3_id, mutate_name(name), mutate_address(addr), country))
            
    # Add distractor test records
    for _ in range(8):
        s2_id = f"S2-{s2_t_counter:05d}"
        s2_t_counter += 1
        s2_test.append((s2_id, f"Test Non-matching Vendor {s2_t_counter}", "Boulevard Haussmann, Paris 75009", "France"))
        
    for filename, data, header in [
        (os.path.join(test_dir, "test_source1.tsv"), s1_test, ["entity_id", "business_name", "business_address", "country"]),
        (os.path.join(test_dir, "test_source2.tsv"), s2_test, ["entity_id", "business_name", "business_address", "country"]),
        (os.path.join(test_dir, "test_source3.tsv"), s3_test, ["entity_id", "business_name", "business_address", "country"]),
    ]:
        with open(filename, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(header)
            w.writerows(data)
            
    print(f"Generated test data in {test_dir}: S1={len(s1_test)}, S2={len(s2_test)}, S3={len(s3_test)}")

if __name__ == "__main__":
    generate_datasets("dataset/train", "dataset/test")
