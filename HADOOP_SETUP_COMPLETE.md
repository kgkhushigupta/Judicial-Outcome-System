# Hadoop Installation & Setup - Complete Guide
## Windows Setup for HDFS (Distributed File System)

---

## ✅ Prerequisites

Before starting, you need:
1. ✓ Hadoop folder downloaded (you mentioned you have this)
2. ✓ Java 11+ installed
3. ✓ PowerShell (on Windows)
4. ✓ Administrator access

---

## 🔍 Step 0: Find Your Hadoop Folder

```powershell
# Check if Hadoop is in your system
ls C:\                              # Main drive
ls C:\Users\ngoya\Downloads\        # Downloads folder
ls C:\Users\ngoya\AppData\          # App data

# Likely names:
# - C:\hadoop
# - C:\hadoop-3.2.0
# - C:\hadoop-3.3.0
# - C:\download\hadoop-x.x.x

# Once found, note the EXACT path
# Example: C:\hadoop
```

---

## 👉 Step 1: Verify Java Installation

```powershell
# Check Java version
java -version

# Should output something like:
# openjdk version "11.0.x"

# If Java not found, install it first:
# Download from: https://www.oracle.com/java/technologies/downloads/
# Or use: choco install openjdk11
# Or visit: adoptopenjdk.net
```

---

## 🔧 Step 2: Set Environment Variables

```powershell
# Open PowerShell as Administrator:
# 1. Press Windows Key
# 2. Type "powershell"
# 3. Right-click → Run as Administrator

# Set HADOOP_HOME (replace with your actual path!)
[Environment]::SetEnvironmentVariable("HADOOP_HOME", "C:\hadoop", "User")

# Set JAVA_HOME (find your Java installation)
# Typical paths:
#   C:\Program Files\Java\jdk-11
#   C:\Program Files\JetBrains\IntelliJ IDEA Community Edition\jbr
#   C:\openjdk

[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk-11", "User")

# Add to PATH
$path = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = $path + ";C:\hadoop\bin;C:\hadoop\sbin"
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")

# Verify (in NEW PowerShell window):
echo $env:HADOOP_HOME
echo $env:JAVA_HOME
```

---

## 📝 Step 3: Configure Hadoop (core-site.xml)

```powershell
# Navigate to config
cd C:\hadoop\etc\hadoop

# Open core-site.xml
notepad core-site.xml

# FIND THIS:
#   <configuration>
#   </configuration>

# ADD THIS between the tags:
<property>
    <name>fs.defaultFS</name>
    <value>hdfs://localhost:9000</value>
</property>

<property>
    <name>hadoop.tmp.dir</name>
    <value>C:\hadoop\tmp</value>
</property>

<property>
    <name>io.native.lib.available</name>
    <value>false</value>
</property>

# Save: Ctrl+S, then close
```

---

## 📝 Step 4: Configure HDFS (hdfs-site.xml)

```powershell
# Still in C:\hadoop\etc\hadoop
# Open hdfs-site.xml
notepad hdfs-site.xml

# FIND THIS:
#   <configuration>
#   </configuration>

# ADD THIS between the tags:
<property>
    <name>dfs.replication</name>
    <value>1</value>
</property>

<property>
    <name>dfs.namenode.name.dir</name>
    <value>C:\hadoop\namenode</value>
</property>

<property>
    <name>dfs.datanode.data.dir</name>
    <value>C:\hadoop\datanode</value>
</property>

<property>
    <name>dfs.namenode.rpc-bind-host</name>
    <value>0.0.0.0</value>
</property>

# Save: Ctrl+S, then close
```

---

## 📁 Step 5: Create Required Directories

```powershell
# Create Hadoop directories
New-Item -Type Directory -Path "C:\hadoop\namenode" -Force | Out-Null
New-Item -Type Directory -Path "C:\hadoop\datanode" -Force | Out-Null
New-Item -Type Directory -Path "C:\hadoop\tmp" -Force | Out-Null

# Verify
ls C:\hadoop\

# Should show: bin, etc, lib, namenode, datanode, tmp, sbin, etc.
```

---

## 🏗️ Step 6: Format NameNode (FIRST TIME ONLY!)

```powershell
# IMPORTANT: Close PowerShell and open a NEW one
# This reloads the environment variables!

# Navigate
cd C:\hadoop\bin

# Format (only do this ONCE!)
.\hdfs.cmd namenode -format

# Expected output:
# 2026-04-02 10:30:45,xxx INFO namenode.NameNode: registered UNIX signal handlers
# ...
# Storage directory C:\hadoop\namenode has been successfully formatted.

# DO NOT run this command again!
# If you do, it will delete all HDFS data!
```

---

## 🚀 Step 7: Start HDFS Services

```powershell
# IMPORTANT: Keep this window open!

# Navigate
cd C:\hadoop\sbin

# Start services
.\start-dfs.cmd

# Wait 10-30 seconds...
# You should see:
# Starting namenodes
# localhost: Starting NameNode
# Starting datanodes
# localhost: Starting DataNode
# Starting secondary namenodes

# Don't close this window - it's running the services!
```

---

## ✅ Step 8: Verify HDFS is Working

```powershell
# OPEN A NEW PowerShell window (leave start-dfs.cmd running in first one)

# Navigate
cd C:\hadoop\bin

# Test 1: List root
.\hdfs.cmd dfs -ls /

# Expected:
# Found 0 items

# Test 2: Check system status
.\hdfs.cmd dfsadmin -report

# Expected:
# Live datanodes (1):
# localhost:50010

# Test 3: Create test directory
.\hdfs.cmd dfs -mkdir -p /test

# Test 4: Check it was created
.\hdfs.cmd dfs -ls /

# Expected:
# drwxr-xr-x   - ngoya supergroup          0 2026-04-02 10:35 /test

# All tests passed? ✓ HDFS is working!
```

---

## 📤 Step 9: Create HDFS Directories for Our Pipeline

```powershell
# In the same new PowerShell window:
cd C:\hadoop\bin

# Create directories
.\hdfs.cmd dfs -mkdir -p /data/hdfs/input
.\hdfs.cmd dfs -mkdir -p /data/hdfs/processed

# Set permissions
.\hdfs.cmd dfs -chmod -R 777 /data/hdfs/

# Verify
.\hdfs.cmd dfs -ls /data/hdfs/

# Expected:
# drwxrwxrwx   - ngoya supergroup          0 2026-04-02 10:36 /data/hdfs/input
# drwxrwxrwx   - ngoya supergroup          0 2026-04-02 10:36 /data/hdfs/processed
```

---

## 📥 Step 10: Upload Your Dataset Files

```powershell
# Navigate
cd C:\hadoop\bin

# Copy files from local to HDFS
.\hdfs.cmd dfs -put "C:\Users\ngoya\big data project\Judicial-AI-System\data\hdfs\input\*.parquet" /data/hdfs/input/

# Wait for upload to complete...

# Verify files uploaded
.\hdfs.cmd dfs -ls /data/hdfs/input/

# Expected:
# -rw-r--r--   1 ngoya supergroup    1048576 2026-04-02 10:37 /data/hdfs/input/legal_cases.parquet
# -rw-r--r--   1 ngoya supergroup    2097152 2026-04-02 10:37 /data/hdfs/input/sentencing.parquet
# -rw-r--r--   1 ngoya supergroup    1572864 2026-04-02 10:37 /data/hdfs/input/judge_decisions.parquet
# -rw-r--r--   1 ngoya supergroup    5242880 2026-04-02 10:37 /data/hdfs/input/crime_stats.parquet
# -rw-r--r--   1 ngoya supergroup    8388608 2026-04-02 10:37 /data/hdfs/input/court_proceedings.parquet

# Check total size
.\hdfs.cmd dfs -du -h /data/hdfs/input/
```

---

## 🎯 Step 11: Test HDFS with Our Pipeline

```powershell
# Navigate to project
cd "C:\Users\ngoya\big data project\Judicial-AI-System"

# Now run the pipeline
python -c "from src.data_import_preprocessing import run_complete_pipeline; run_complete_pipeline()"

# It will read from HDFS and create output files in /data/hdfs/processed/
```

---

## 🛑 Stopping Hadoop Services

```powershell
# When done for the day:

# In the PowerShell window running start-dfs.cmd:
# Press: Ctrl + C

# Or run in new window:
cd C:\hadoop\sbin
.\stop-dfs.cmd

# Wait for services to stop completely
```

---

## ⚠️ Troubleshooting

### Problem: "hdfs.cmd not found"
```powershell
# Solution: PATH not set correctly
# Verify:
echo $env:HADOOP_HOME

# If empty, environment variables not loaded
# Close PowerShell completely and reopen
```

### Problem: "Connection refused" when running commands
```powershell
# Solution: HDFS services not running
# Make sure start-dfs.cmd window is still open
# Or run:
cd C:\hadoop\sbin
.\start-dfs.cmd
```

### Problem: "Only a single namenode is supported in non-HA mode"
```powershell
# Solution: This is OK - just means no redundancy
# Continue with the process
```

### Problem: "java not found in format namenode"
```powershell
# Solution: JAVA_HOME not correct
# Check:
echo $env:JAVA_HOME

# Should point to Java installation
# If wrong, update it:
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk-11", "User")

# Close PowerShell and reopen
```

### Problem: "C:\hadoop\namenode directory does not exist"
```powershell
# Solution: Create directories manually
New-Item -Type Directory -Path "C:\hadoop\namenode" -Force
New-Item -Type Directory -Path "C:\hadoop\datanode" -Force
New-Item -Type Directory -Path "C:\hadoop\tmp" -Force

# Then format namenode again:
cd C:\hadoop\bin
.\hdfs.cmd namenode -format
```

### Problem: "Block count mismatch"
```powershell
# Solution: This is OK, just means HDFS repairing itself
# It will resolve automatically
# Continue using HDFS normally
```

---

## 📊 Monitor HDFS Web Interface

```powershell
# While HDFS is running, open browser:
# http://localhost:50070/

# Or (newer Hadoop):
# http://localhost:9870/

# You should see:
# - NameNode status
# - Datanodes
# - File storage
# - System load
```

---

## ✅ Verification Checklist

After complete setup, verify:

- [ ] Java installed: `java -version` works
- [ ] HADOOP_HOME set: `echo $env:HADOOP_HOME` shows path
- [ ] JAVA_HOME set: `echo $env:JAVA_HOME` shows path
- [ ] core-site.xml configured with fs.defaultFS
- [ ] hdfs-site.xml configured with paths
- [ ] Directories created: namenode, datanode, tmp exist
- [ ] NameNode formatted (one-time): `hdfs namenode -format` completed
- [ ] Services running: start-dfs.cmd window open
- [ ] HDFS commands work: `hdfs dfs -ls /` returns results
- [ ] Test directory created: `/test` or `/data/hdfs/input` exists
- [ ] Files uploaded: `hdfs dfs -ls /data/hdfs/input/` shows parquet files

---

## 🚀 Now Run Your Pipeline!

```powershell
# With HDFS running, execute the pipeline:
cd "C:\Users\ngoya\big data project\Judicial-AI-System"

python -c "from src.data_import_preprocessing import run_complete_pipeline; run_complete_pipeline()"

# Pipeline will:
# 1. Read from HDFS: /data/hdfs/input/*.parquet
# 2. Clean and process data
# 3. Write to HDFS: /data/hdfs/processed/
# 4. Export to local: data/hdfs/processed/
```

---

## 📚 Quick Reference Commands

```powershell
# Check HDFS status
cd C:\hadoop\bin
.\hdfs.cmd dfsadmin -report

# List files
.\hdfs.cmd dfs -ls /data/hdfs/input/

# Check disk usage
.\hdfs.cmd dfs -du -h /data/hdfs/

# Upload file
.\hdfs.cmd dfs -put C:\local\file.txt /hdfs/path/

# Download file
.\hdfs.cmd dfs -get /hdfs/path/file.txt C:\local\

# Delete file
.\hdfs.cmd dfs -rm /hdfs/path/file.txt

# Create directory
.\hdfs.cmd dfs -mkdir -p /hdfs/path/

# All Java processes
Get-Process | grep java
```

---

**Hadoop is now fully set up and ready for your Judicial AI System!** 🎉
