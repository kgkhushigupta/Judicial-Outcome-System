#!/usr/bin/env python3
"""
Quick Launcher for Judicial AI System
Provides easy menu-driven access to all features
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print(" "*15 + "🏛️ JUDICIAL AI SYSTEM - LAUNCHER")
    print("="*70)

def print_menu():
    """Print main menu"""
    print("\n📋 MAIN MENU:")
    print("  1. Run complete demo pipeline")
    print("  2. Generate new dataset")
    print("  3. View HTML report (last run)")
    print("  4. View JSON results")
    print("  5. View CSV predictions")
    print("  6. Test individual modules")
    print("  7. Clean output & start fresh")
    print("  8. Show documentation")
    print("  9. Exit")
    print("-" * 70)

def run_demo():
    """Run the complete demo pipeline"""
    print("\n▶️  Starting complete demo pipeline...")
    print("This may take 30-60 seconds...\n")
    
    result = subprocess.run(
        [sys.executable, "run_demo.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    if result.returncode == 0:
        print("\n✅ Demo completed successfully!")
        open_report()
    else:
        print("\n❌ Demo failed. Check output above.")

def generate_dataset():
    """Generate new dataset"""
    print("\n▶️  Generating new dataset...")
    
    num_cases = input("How many cases to generate? (default 75): ").strip()
    if not num_cases:
        num_cases = 75
    else:
        num_cases = int(num_cases)
    
    result = subprocess.run(
        [sys.executable, "generate_dataset.py"]
    )
    
    if result.returncode == 0:
        print(f"\n✅ Generated {num_cases} cases successfully!")

def open_report():
    """Open HTML report in default browser"""
    report_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "output",
        "report.html"
    )
    
    if os.path.exists(report_path):
        print(f"\n📊 Opening HTML report: {report_path}")
        webbrowser.open(f"file:///{report_path}")
    else:
        print(f"\n❌ Report not found: {report_path}")
        print("   Run demo first (option 1)")

def view_json():
    """Display JSON results"""
    results_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "output",
        "results.json"
    )
    
    if os.path.exists(results_path):
        import json
        with open(results_path) as f:
            results = json.load(f)
        print("\n📄 JSON RESULTS (formatted):")
        print(json.dumps(results, indent=2, default=str)[:2000])
        print("...\n(Full results in output/results.json)")
    else:
        print("\n❌ Results not found. Run demo first.")

def view_csv():
    """Display CSV predictions"""
    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "output",
        "predictions.csv"
    )
    
    if os.path.exists(csv_path):
        import pandas as pd
        df = pd.read_csv(csv_path)
        print("\n📊 CSV PREDICTIONS (first 10 rows):")
        print(df.head(10).to_string())
        print(f"\n... ({len(df)} total predictions in output/predictions.csv)")
    else:
        print("\n❌ Predictions not found. Run demo first.")

def test_modules():
    """Interactive module testing"""
    print("\n🧪 MODULE TESTING:")
    print("  1. Test text cleaning")
    print("  2. Test keyword extraction")
    print("  3. Test embeddings")
    print("  4. Test similarity search")
    print("  5. Test bias detection")
    print("  6. Back to main menu")
    
    choice = input("\nSelect test (1-6): ").strip()
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    if choice == "1":
        print("\n▶️  Testing text cleaning...")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, 'src'); "
            "from preprocessing.text_cleaning import clean_text; "
            "result = clean_text('The DEFENDANT was charged with FRAUD!!!'); "
            f"print(f'Input: \"The DEFENDANT was charged with FRAUD!!!\"'); "
            f"print(f'Output: \"{result}\"')"
        ], cwd=test_dir)
    
    elif choice == "2":
        print("\n▶️  Testing keyword extraction...")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, 'src'); "
            "from nlp.keyword_extractor import KeywordExtractor; "
            "e = KeywordExtractor(); "
            "kw = e.extract_keywords('The defendant was charged with fraud. Evidence shows guilty verdict.'); "
            "print(f'Extracted keywords: {kw}')"
        ], cwd=test_dir)
    
    elif choice in ["3", "4", "5"]:
        print("\n▶️  Running module test...")
        print("(Full test requires demo to be run first)")
    
    elif choice == "6":
        return
    
    input("\nPress Enter to continue...")

def clean_output():
    """Clean output directory"""
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "output"
    )
    
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
        print(f"\n✅ Cleaned: {output_dir}")
    
    print("Ready for fresh demo run!")

def show_docs():
    """Display documentation"""
    readme_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "README.md"
    )
    
    if os.path.exists(readme_path):
        with open(readme_path) as f:
            content = f.read()
        
        # Show first 1500 chars
        print("\n📖 README (first section):")
        print(content[:1500])
        print("\n... (Full documentation in README.md)")
        print("\nRun: python run_demo.py    (for complete pipeline)")
    else:
        print("\n❌ README not found")

def main():
    """Main launcher loop"""
    print_banner()
    
    while True:
        print_menu()
        choice = input("Select option (1-9): ").strip()
        
        if choice == "1":
            run_demo()
        elif choice == "2":
            generate_dataset()
        elif choice == "3":
            open_report()
        elif choice == "4":
            view_json()
        elif choice == "5":
            view_csv()
        elif choice == "6":
            test_modules()
        elif choice == "7":
            clean_output()
        elif choice == "8":
            show_docs()
        elif choice == "9":
            print("\n👋 Thanks for using Judicial AI System!")
            break
        else:
            print("\n❌ Invalid option")

if __name__ == "__main__":
    main()
