# Extract Hadoop 3.3.6 on Windows

You have: `C:\Users\ngoya\Downloads\hadoop-3.3.6.tar.gz`

## Option 1: Windows 11 Built-in Extraction (Easiest)

```powershell
# Open PowerShell as Administrator

# Navigate to Downloads
cd C:\Users\ngoya\Downloads\

# Verify tar.gz file exists
ls hadoop-3.3.6.tar.gz

# Extract it (Windows 11 can do this natively)
tar -xzf hadoop-3.3.6.tar.gz

# Wait 2-5 minutes for extraction...

# Verify extraction
ls hadoop-3.3.6\
# Should show: bin, etc, lib, libexec, sbin, share, etc.
```

## Option 2: Using 7-Zip (if Windows 10 or extraction fails)

```powershell
# Install 7-Zip if not already installed
choco install 7zip

# Or download from: https://www.7-zip.org/

# Then extract (right-click):
# 1. Right-click hadoop-3.3.6.tar.gz
# 2. Select "7-Zip" → "Extract Here"
# 3. Wait for completion
```

## Option 3: Using WSL (Windows Subsystem for Linux)

```bash
# If you have WSL installed
wsl
cd /mnt/c/Users/ngoya/Downloads/
tar -xzf hadoop-3.3.6.tar.gz
exit
```

---

## After Extraction

```powershell
# Move to a simpler location
Move-Item C:\Users\ngoya\Downloads\hadoop-3.3.6 C:\hadoop

# Verify
ls C:\hadoop\
# Should show: bin, etc, lib, libexec, sbin, share

# Check important files exist
ls C:\hadoop\bin\hdfs.cmd
ls C:\hadoop\etc\hadoop\core-site.xml
# Both should exist
```

---

## Then Continue Setup

Once extracted to `C:\hadoop`, run the setup:

```powershell
# Edit this script and set:
# $HADOOP_PATH = "C:\hadoop"

C:\Users\ngoya\big data project\Judicial-AI-System\setup_hadoop.ps1
```

---

**Total time: 5-10 minutes**
