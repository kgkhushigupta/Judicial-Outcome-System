# Windows Setup - No HDFS Required ✓
## Judicial AI System - Windows Quick Setup

---

## ✅ Good News!

You **don't need HDFS, Hadoop, or any complex setup** on Windows for development!

```
✓ Python only (already installed)
✓ Local file system (already available)
✓ No HDFS, no Hadoop, no WSL needed
✓ Complete pipeline works out-of-the-box
```

---

## 🚀 Windows Quick Start (3 Steps)

### Step 1: Open PowerShell

```powershell
# Press: Windows Key + R
# Type: powershell
# Press: Enter

# You'll see something like:
# PS C:\Users\YourName>
```

### Step 2: Navigate to Project

```powershell
cd "c:\Users\ngoya\big data project\Judicial-AI-System"

# Verify you're in the right place:
Get-Location
# Should show: C:\Users\ngoya\big data project\Judicial-AI-System
```

### Step 3: Install & Run

```powershell
# First time only - install Python packages (30 seconds):
pip install pandas numpy scikit-learn pyspark neo4j faiss-cpu torch

# Then run the pipeline:
python -c "from src.data_import_preprocessing import run_complete_pipeline; run_complete_pipeline()"

# Done! Check the output.
```

**That's it!** ✓

---

## ❌ Why You Got the HDFS Error

```
# This command:
hdfs dfs -ls /

# Failed because:
- HDFS is a Linux/production tool
- It's NOT installed on your Windows system
- You DON'T need it for development!
```

---

## ✅ What You Actually Need

For the **complete Judicial AI system**, you only need:

| Component | Windows | Reason |
|-----------|---------|--------|
| **Python 3.8+** | ✓ Yes | Core language |
| **pip** | ✓ Yes | Package installer |
| **Pandas/NumPy** | ✓ Yes | Data processing |
| **PySpark** | ~ Optional | For parallel processing |
| **Java** | ~ Optional | Only if using Spark |
| **HDFS** | ✗ Not needed | For local development |
| **Hadoop** | ✗ Not needed | For production only |

---

## 📂 File Storage - Local vs HDFS

### Local File System (What You're Using)

```
C:\Users\ngoya\big data project\Judicial-AI-System\
    └─ data\
       └─ hdfs\
           ├─ input\           ← Your dataset files go here
           │   ├─ legal_cases.parquet
           │   ├─ sentencing.parquet
           │   ├─ judge_decisions.parquet
           │   ├─ crime_stats.parquet
           │   └─ court_proceedings.parquet
           └─ processed\       ← Cleaned files go here (auto-generated)
               ├─ dataset_1_cleaned.parquet
               ├─ dataset_1_cleaned.csv
               ├─ dataset_1_cleaned.json
               └─ ... (15 files total)
```

**Note:** The folder is called `hdfs/` but it's just a **local folder name** - NOT actual HDFS!

### HDFS (Distributed - Production Only)

```
/data/hdfs/input/               ← Files stored on Hadoop cluster
/data/hdfs/processed/           ← Across multiple servers
```

---

## 🎯 Complete Windows Setup (First Time Only)

Copy and paste this entire block:

```powershell
# ============================================================================
# WINDOWS SETUP - Run this once, then you're done forever
# ============================================================================

# Step 1: Navigate to project
cd "c:\Users\ngoya\big data project\Judicial-AI-System"

# Step 2: Install Python packages (takes ~1-2 minutes)
Write-Host "Installing Python packages..." -ForegroundColor Cyan
pip install pandas numpy scikit-learn pyspark neo4j faiss-cpu torch -q

# Step 3: Create required directories
Write-Host "Creating directories..." -ForegroundColor Cyan
New-Item -Type Directory -Path "data\hdfs\input", "data\hdfs\processed", "logs", "output" -Force | Out-Null

# Step 4: Verify setup
Write-Host "`nVerifying setup..." -ForegroundColor Cyan
$files = Get-ChildItem "data\hdfs\input" -ErrorAction SilentlyContinue
if ($files) {
    Write-Host "✓ Dataset files found in data\hdfs\input\" -ForegroundColor Green
    $files | Select-Object Name
} else {
    Write-Host "! No dataset files found in data\hdfs\input\" -ForegroundColor Yellow
    Write-Host "  Place your .parquet files there before running" -ForegroundColor Yellow
}

# Step 5: Show structure
Write-Host "`n✓ Setup complete! Your project structure:" -ForegroundColor Green
ls -Directory data\hdfs

Write-Host "`nNext: Run the pipeline with:" -ForegroundColor Cyan
Write-Host 'python -c "from src.data_import_preprocessing import run_complete_pipeline; run_complete_pipeline()"'
```

---

## 🏃 Run the Pipeline (Every Time)

```powershell
cd "c:\Users\ngoya\big data project\Judicial-AI-System"

python -c "from src.data_import_preprocessing import run_complete_pipeline; run_complete_pipeline()"
```

**That's it!** ✓

---

## 📊 Understanding Local File System

### Where Files Go

```
Before Running:
  data/hdfs/input/
    ├─ legal_cases.parquet         (YOUR input files)
    ├─ sentencing.parquet
    ├─ judge_decisions.parquet
    ├─ crime_stats.parquet
    └─ court_proceedings.parquet

After Running (Auto-Generated):
  data/hdfs/processed/
    ├─ dataset_1_cleaned.parquet   ← Phase 1 output
    ├─ dataset_1_cleaned.csv
    ├─ dataset_1_cleaned.json
    ├─ dataset_2_cleaned.*
    ├─ dataset_3_cleaned.*
    ├─ dataset_4_cleaned.*
    └─ dataset_5_cleaned.*

  logs/
    └─ pipeline_2026-04-02.log     ← Execution log

  output/
    ├─ bias_metrics.json           ← Phase 5 output
    ├─ clusters.json               ← Phase 4 output
    ├─ model.pkl                   ← Phase 7 output
    └─ summary_report.json         ← Final report
```

### How It Works

```
1. IMPORT: Read from data/hdfs/input/ (local folder)
   └─ 5 Parquet files → Load to memory

2. PROCESS: Transformations in RAM
   └─ Clean, deduplicate, validate

3. EXPORT: Write to data/hdfs/processed/ (local folder)
   └─ Parquet (Spark), CSV (Excel), JSON (APIs)

All operations are LOCAL - no network, no HDFS needed!
```

---

## 🛠️ Optional: Add Spark (For Parallel Processing)

If you want to use Apache Spark for faster parallel processing:

```powershell
# Step 1: Install Java (if not already installed)
# Download from: https://www.oracle.com/java/technologies/downloads/
# Or use: choco install openjdk11  (if using Chocolatey)

# Step 2: Install Spark
# Download from: https://spark.apache.org/downloads.html
# Extract to: C:\spark-3.2.0

# Step 3: Set environment variables
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk-11", "User")
[Environment]::SetEnvironmentVariable("SPARK_HOME", "C:\spark-3.2.0", "User")
$path = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = $path + ";C:\spark-3.2.0\bin"
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")

# Step 4: Restart PowerShell and verify
spark-submit --version

# Now you can run Phase 2 (optional):
spark-submit --master local[4] --driver-memory 4g src/preprocessing/spark_preprocessing.py
```

---

## ⚡ Quick Commands Reference

```powershell
# Navigate to project
cd "c:\Users\ngoya\big data project\Judicial-AI-System"

# Run everything
python -c "from src.data_import_preprocessing import run_complete_pipeline; run_complete_pipeline()"

# Check dataset files
ls data/hdfs/input/

# Check output files
ls data/hdfs/processed/

# Check logs
ls logs/

# View the latest log
Get-Content (ls logs/ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# Check results
ls output/
```

---

## ✅ Verification Checklist

After setup, verify you have:

- [ ] PowerShell open at: `C:\Users\ngoya\big data project\Judicial-AI-System`
- [ ] Python installed: `python --version` shows 3.8+
- [ ] Packages installed: `pip list | grep pandas`
- [ ] Dataset files in: `data\hdfs\input\` (parquet files)
- [ ] Directories exist: `ls data\hdfs`, `ls logs`, `ls output`

If all checked ✓, you're ready to run!

---

## 🚨 Troubleshooting Windows Issues

| Problem | Solution |
|---------|----------|
| **"Python not found"** | Reinstall Python from python.org, make sure to add to PATH |
| **"pip not found"** | Check: `python -m pip --version` |
| **"Module not found"** | Run: `pip install pandas numpy scikit-learn` |
| **"Permission denied"** | Right-click PowerShell → Run as Administrator |
| **"Path not found"** | Use: `cd` to navigate to correct folder |
| **Slow performance** | Normal for first run (models load). Subsequent runs are faster |

---

## 💡 Pro Tips

### 1. Keep Terminal Open
```powershell
# After running complete pipeline, leave the terminal open
# You can run individual phases again without reinstalling
```

### 2. Monitor Progress
```powershell
# Open a second PowerShell while running, check file sizes:
ls data/hdfs/processed/ | Select-Object Name, Length
```

### 3. Review Results
```powershell
# After complete, view the summary:
Get-Content output/summary_report.json | ConvertFrom-Json | Format-Table
```

### 4. Re-run Individual Phases
```powershell
# Clean and re-run just Phase 1
Remove-Item data/hdfs/processed/* -Force
python -c "from src.data_import_preprocessing import run_complete_pipeline; run_complete_pipeline()"
```

---

## 📚 Next: Understanding the Data

After running successfully, read:

1. **DATA_IMPORT_GUIDE.md** - Learn about the 5 datasets
2. **DATA_PIPELINE_SUMMARY.md** - Visual overview of cleaning
3. **SYSTEM_ARCHITECTURE_FLOW.md** - How everything connects

---

## 🎓 FAQ

**Q: Why is it called "hdfs" if it's local?**
A: The folder structure matches the distributed setup, but uses local storage for development.

**Q: Can I use cloud storage instead?**
A: Yes! The code can be modified to use AWS S3, Azure Blob, or Google Cloud Storage.

**Q: Is my data secure?**
A: Data stays on your local machine - no cloud upload unless you configure it.

**Q: How much disk space do I need?**
A: ~500 MB for input files + ~200 MB for outputs = ~1 GB total recommended.

**Q: Can I run this on Mac?**
A: Yes! Same commands work on Mac. Just use the Mac-appropriate paths.

**Q: Can I run this on Linux?**
A: Yes! You can then add real HDFS if needed for production.

---

## 🚀 You're Ready!

```powershell
# Copy and paste in PowerShell:
cd "c:\Users\ngoya\big data project\Judicial-AI-System" ; python -c "from src.data_import_preprocessing import run_complete_pipeline; run_complete_pipeline()" ; Write-Host "`n✓ Complete!" -ForegroundColor Green
```

**No HDFS. No Hadoop. Just Python. Just Works.** ✓

---

**You're all set! Run the pipeline now!** 🎉
