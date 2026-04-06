# Hadoop on Windows - Troubleshooting Guide
## Common errors and solutions for setting up Hadoop

---

## ❌ Error: "hdfs is not recognized as an internal or external command"

### Cause:
Environment variables not set or not reloaded.

### Solution:

**Step 1: Verify environment variables are set**
```powershell
# Check if variables exist
echo $env:HADOOP_HOME
echo $env:JAVA_HOME

# Should both show paths, not empty lines
```

**Step 2: If empty, set them manually**
```powershell
[Environment]::SetEnvironmentVariable("HADOOP_HOME", "C:\hadoop", "User")
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk-11", "User")

# Add to PATH
$path = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = $path + ";C:\hadoop\bin;C:\hadoop\sbin"
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
```

**Step 3: Reload PowerShell**
```powershell
# Close this PowerShell window completely
exit

# Open a NEW PowerShell window (new terminal process)
# Don't just open a new tab - close and reopen
```

**Step 4: Test again**
```powershell
cd C:\hadoop\bin
.\hdfs.cmd dfs -ls /
# Should work now
```

---

## ❌ Error: "Connection refused" or "Unable to connect"

### Cause:
HDFS services not running.

### Solution:

**Step 1: Check if services running**
```powershell
# Look for Java processes
Get-Process | Select-String -Property ProcessName -Pattern java

# Should show NameNode and DataNode processes running
```

**Step 2: If no processes, start them**
```powershell
# Open NEW PowerShell as Administrator
cd C:\hadoop\sbin
.\start-dfs.cmd

# Wait 20-30 seconds for startup
# Should show:
# Starting namenodes
# localhost: Starting NameNode
# Starting datanodes
# localhost: Starting DataNode
```

**Step 3: Keep this window open!**
```powershell
# ⚠️ DO NOT close this window
# ⚠️ Services stop when this terminal closes
# ⚠️ Use OTHER terminals for HDFS commands
```

**Step 4: Test from different terminal**
```powershell
# Open ANOTHER PowerShell window
cd C:\hadoop\bin
.\hdfs.cmd dfs -ls /
# Should work now
```

---

## ❌ Error: "Only a single namenode is supported in non-HA mode"

### Cause:
Normal in single-node setup.

### Solution:
✓ This is NOT an error - it's informational

Just continue - this is expected behavior:
```powershell
# This is OK:
# Only a single namenode is supported in non-HA mode.

# Continue with setup normally
```

---

## ❌ Error: "java" command not found

### Cause:
Java not installed or JAVA_HOME not set.

### Solution:

**Step 1: Check Java installation**
```powershell
java -version
# If fails: Java not installed
```

**Step 2: Install Java if needed**
```
Download from:
https://www.oracle.com/java/technologies/downloads/

Or use Chocolatey:
choco install openjdk11
```

**Step 3: Find Java installation**
```powershell
# Common locations:
ls "C:\Program Files\Java\"
ls "C:\Program Files\JetBrains\IntelliJ IDEA Community Edition\jbr"

# Note the path of jdk-11 or similar folder
```

**Step 4: Set JAVA_HOME**
```powershell
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk-11", "User")
# Replace with your actual path
```

**Step 5: Add to PATH**
```powershell
$path = [Environment]::GetEnvironmentVariable("PATH", "User")
if (-not $path.Contains("$env:JAVA_HOME\bin")) {
    $newPath = $path + ";$env:JAVA_HOME\bin"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
}
```

**Step 6: Restart PowerShell and test**
```powershell
# Close all PowerShell windows
exit

# Open NEW PowerShell
java -version
# Should work now
```

---

## ❌ Error: "C:\hadoop\namenode directory does not exist"

### Cause:
Directories not created before format.

### Solution:

**Step 1: Create missing directories**
```powershell
# Create all required directories
New-Item -Type Directory -Path "C:\hadoop\namenode" -Force | Out-Null
New-Item -Type Directory -Path "C:\hadoop\datanode" -Force | Out-Null
New-Item -Type Directory -Path "C:\hadoop\tmp" -Force | Out-Null

# Verify they exist
ls C:\hadoop\
# Should show: bin, etc, lib, namenode, datanode, sbin, tmp
```

**Step 2: Update hdfs-site.xml**
```powershell
# Open in notepad
notepad C:\hadoop\etc\hadoop\hdfs-site.xml

# Make sure paths match directories created:
# <value>C:\hadoop\namenode</value>
# <value>C:\hadoop\datanode</value>

# Save and close
```

**Step 3: Try format again**
```powershell
cd C:\hadoop\bin
.\hdfs.cmd namenode -format
# Should work now
```

---

## ❌ Error: "Block count mismatch"

### Cause:
HDFS repairing itself (normal).

### Solution:
✓ This is NOT a critical error - HDFS is self-healing

```powershell
# Just wait - this resolves automatically
# Your HDFS will still work fine
# Blocks are being re-replicated to correct state

# You can monitor with:
cd C:\hadoop\bin
.\hdfs.cmd dfsadmin -report
```

---

## ❌ Error: "hdfs dfs -put: Input/output error"

### Cause:
HDFS directory permissions or disk space issue.

### Solution:

**Step 1: Check directory permissions**
```powershell
# Set correct permissions
cd C:\hadoop\bin
.\hdfs.cmd dfs -chmod -R 777 /data/hdfs/
```

**Step 2: Check disk space**
```powershell
# Check free space
fsutil volume diskfree C:\

# If < 1GB free, clean up:
# - Temporary files
# - Downloaded files
# - Cache
```

**Step 3: Try upload again**
```powershell
.\hdfs.cmd dfs -put "C:\path\to\file.parquet" /data/hdfs/input/
```

---

## ❌ Error: "No space left on device"

### Cause:
Disk full.

### Solution:

**Step 1: Check available space**
```powershell
# Check all drives
Get-Volume
# Look for "SizeRemaining"
```

**Step 2: Free up space**
```powershell
# Delete Hadoop logs (safe)
rm C:\hadoop\logs\*

# Delete temp files
rm -Recurse -Force C:\hadoop\tmp\*
```

**Step 3: Keep minimum 1GB free**
- Minimum: 1 GB free space on C:\ drive
- Better: 10 GB free
- Ideal: 50 GB free

---

## ❌ Error: "Cannot rename C:\hadoop\namenode\current\VERSION"

### Cause:
NameNode already formatted - trying to format again.

### Solution:

```powershell
# DO NOT format NameNode twice!
# NameNode format deletes ALL HDFS data

# If you already formatted once:
cd C:\hadoop\bin
.\hdfs.cmd namenode -format

# This WILL DELETE all data in HDFS

# If you want to start fresh:
# 1. Delete namenode directory: rm -Recurse C:\hadoop\namenode
# 2. Delete datanode directory: rm -Recurse C:\hadoop\datanode
# 3. Create new directories:
New-Item -Type Directory -Path "C:\hadoop\namenode" -Force | Out-Null
New-Item -Type Directory -Path "C:\hadoop\datanode" -Force | Out-Null

# 4. Format once:
.\hdfs.cmd namenode -format

# 5. Start services:
cd ..\sbin
.\start-dfs.cmd
```

---

## ❌ Error: "Permission denied" on Windows

### Cause:
Script execution policy or not running as Administrator.

### Solution:

**Step 1: Run as Administrator**
```
Press Windows Key
Type "PowerShell"
Right-click → "Run as Administrator"
Click "Yes"
```

**Step 2: Set execution policy if needed**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

**Step 3: Try again**
```powershell
cd C:\hadoop\bin
.\hdfs.cmd dfs -ls /
```

---

## ❌ Error: "Failed to get hostid using /bin/hostname"

### Cause:
Windows hostname not properly configured.

### Solution:
✓ This is usually informational, not critical

```powershell
# You can safely ignore this warning
# Hadoop still works

# To fix it (optional):
hostname

# This should show your Windows computer name
# It's already configured in Windows
```

---

## ❌ Error: "namenode: command not found"

### Cause:
Missing `.cmd` suffix on Windows.

### Solution:

```powershell
# WRONG (Linux/Mac):
hdfs namenode -format

# CORRECT (Windows):
.\hdfs.cmd namenode -format
```

---

## ⚠️ Warning: "WARN util.NativeCodeLoader"

### Cause:
Native libraries not compiled for Windows (harmless).

### Solution:
✓ Safe to ignore - set in hdfs-site.xml:

```xml
<property>
    <name>io.native.lib.available</name>
    <value>false</value>
</property>
```

---

## ⚠️ Warning: "ssh: command not found"

### Cause:
SSH not installed (not needed on Windows).

### Solution:
✓ Safe to ignore

Single-node Hadoop doesn't need SSH. Continue normally.

---

## 🧪 Testing HDFS After Fixing Errors

```powershell
# After fixing an error, test with:

cd C:\hadoop\bin

# Test 1: List root
.\hdfs.cmd dfs -ls /
# Expected: empty or list of directories

# Test 2: Create test file
.\hdfs.cmd dfs -mkdir -p /test

# Test 3: Verify it exists
.\hdfs.cmd dfs -ls /

# Test 4: Health check
.\hdfs.cmd dfsadmin -report
# Expected: shows datanodes online

# If all tests pass: ✓ HDFS working correctly
```

---

## 🔍 Web Interface for Monitoring

While HDFS is running:

```
NameNode UI: http://localhost:50070/
(or http://localhost:9870/ for newer versions)

Check:
- NameNode Status: Online?
- Datanodes: Listed?
- File storage: Showing files?
- System load: CPU/Memory okay?
```

---

## 📞 Still Having Issues?

### Check these in order:

1. **Is `start-dfs.cmd` window still open?**
   - Services stop when terminal closes
   - Rerun: `cd C:\hadoop\sbin` → `.\start-dfs.cmd`

2. **Did you restart PowerShell after setting environment variables?**
   - New environment variables don't load until new terminal opens
   - Close ALL PowerShell windows
   - Open a NEW one

3. **Is Java really installed?**
   - Run: `java -version`
   - If fails, install Java first

4. **Is Hadoop configured correctly?**
   - Check: `C:\hadoop\etc\hadoop\core-site.xml`
   - Check: `C:\hadoop\etc\hadoop\hdfs-site.xml`
   - Compare with examples in HADOOP_SETUP_COMPLETE.md

5. **Do you have disk space?**
   - Check: `fsutil volume diskfree C:\`
   - Need at least: 1 GB free

---

## 🚀 Success Indicators

You'll know it's working when:

✓ `.\hdfs.cmd dfs -ls /` returns results without errors
✓ `.\hdfs.cmd dfsadmin -report` shows "Live datanodes (1):"
✓ Web UI shows NameNode online and DataNode registered
✓ Can upload files: `.\hdfs.cmd dfs -put file.txt /`
✓ Can create directories: `.\hdfs.cmd dfs -mkdir /testdir`
✓ Can list files: `.\hdfs.cmd dfs -ls /testdir`

---

**Need more help? Check HADOOP_SETUP_COMPLETE.md for full step-by-step guide** 📖
