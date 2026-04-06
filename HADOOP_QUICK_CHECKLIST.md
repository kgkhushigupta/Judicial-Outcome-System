# Hadoop Setup - Quick Start Checklist
## Complete this checklist to get Hadoop running on Windows

---

## 📋 PRE-SETUP (5 minutes)

- [ ] **Find your Hadoop folder**
  - Look in: `C:\`, `C:\Users\ngoya\Downloads\`, `C:\Program Files\`
  - Note the exact path: `___________________________`
  - Expected: folder named `hadoop`, `hadoop-3.2.0`, or `hadoop-3.3.0`

- [ ] **Verify Java is installed**
  - Open PowerShell and run: `java -version`
  - Should show: `-version "11.0.x"` or similar
  - If NOT found: Download from adoptopenjdk.net

- [ ] **Find your Java folder**
  - Typical locations:
    - `C:\Program Files\Java\jdk-11`
    - `C:\Program Files\JetBrains\IntelliJ IDEA Community Edition\jbr`
  - Note the exact path: `___________________________`

---

## 🔧 SETUP (10 minutes)

### Option A: Automatic Setup (Recommended)
- [ ] **Edit script file**
  - Open: `setup_hadoop.ps1`
  - Find lines with `$HADOOP_PATH` and `$JAVA_PATH`
  - Replace with YOUR actual paths
  - Save file

- [ ] **Run setup script**
  - Right-click PowerShell → "Run as Administrator"
  - Run: `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process`
  - Run: `C:\Users\ngoya\big data project\Judicial-AI-System\setup_hadoop.ps1`
  - Wait for completion

### Option B: Manual Setup
If script doesn't work, follow these steps manually:

- [ ] **Set HADOOP_HOME environment variable**
  - Right-click PowerShell → "Run as Administrator"
  - Run: `[Environment]::SetEnvironmentVariable("HADOOP_HOME", "C:\hadoop", "User")`
  - (Replace `C:\hadoop` with YOUR path)

- [ ] **Set JAVA_HOME environment variable**
  - Run: `[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk-11", "User")`
  - (Replace path with YOUR Java location)

- [ ] **Add to PATH**
  ```powershell
  $path = [Environment]::GetEnvironmentVariable("PATH", "User")
  $newPath = $path + ";C:\hadoop\bin;C:\hadoop\sbin"
  [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
  ```

- [ ] **Create directories**
  ```powershell
  New-Item -Type Directory -Path "C:\hadoop\namenode" -Force | Out-Null
  New-Item -Type Directory -Path "C:\hadoop\datanode" -Force | Out-Null
  New-Item -Type Directory -Path "C:\hadoop\tmp" -Force | Out-Null
  ```

- [ ] **Close this PowerShell window**
  - Run: `exit`
  - This reloads environment variables

---

## ⚙️ CONFIGURATION (5 minutes)

- [ ] **Configure core-site.xml**
  - Open: `C:\hadoop\etc\hadoop\core-site.xml` (with Notepad)
  - Find: `<configuration>` and `</configuration>`
  - Add between them:
    ```xml
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
    ```
  - Save: Ctrl+S

- [ ] **Configure hdfs-site.xml**
  - Open: `C:\hadoop\etc\hadoop\hdfs-site.xml` (with Notepad)
  - Find: `<configuration>` and `</configuration>`
  - Add between them:
    ```xml
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
    ```
  - Save: Ctrl+S

---

## 🚀 LAUNCH HADOOP (5 minutes)

### Terminal 1: Format & Start HDFS

- [ ] **Open PowerShell as Administrator** (NEW window)

- [ ] **Navigate to Hadoop**
  - Run: `cd C:\hadoop\bin`

- [ ] **Format NameNode** (only do this ONCE!)
  - Run: `.\hdfs.cmd namenode -format`
  - Wait for completion
  - You should see: "successfully formatted"
  - ⚠️ DO NOT run this command again!

- [ ] **Start HDFS Services** (Terminal 2)
  - Open another PowerShell as Administrator (NEW window)
  - Run: `cd C:\hadoop\sbin`
  - Run: `.\start-dfs.cmd`
  - Wait 10-30 seconds
  - You should see:
    - "Starting namenodes"
    - "Starting datanodes"
    - "Starting secondary namenodes"
  - Leave this window OPEN - it's running the services!

---

## ✅ VERIFICATION (5 minutes)

### Terminal 3: Test HDFS Commands

- [ ] **Open third PowerShell as Administrator** (NEW window)

- [ ] **Navigate to Hadoop**
  - Run: `cd C:\hadoop\bin`

- [ ] **Test 1: List root**
  - Run: `.\hdfs.cmd dfs -ls /`
  - Expected: `Found 0 items` (or empty)
  - If ERROR: Check that `start-dfs.cmd` window is still running

- [ ] **Test 2: Check status**
  - Run: `.\hdfs.cmd dfsadmin -report`
  - Expected: See "Live datanodes (1):"
  - If ERROR: Check `start-dfs.cmd` are still running

- [ ] **Test 3: Create directory**
  - Run: `.\hdfs.cmd dfs -mkdir -p /data/hdfs/input`

- [ ] **Test 4: Verify created**
  - Run: `.\hdfs.cmd dfs -ls /`
  - Expected: See `/data/hdfs` listed
  - ✅ If you see output, HDFS is working!

---

## 📥 LOAD DATA (10 minutes)

- [ ] **Upload data files to HDFS**
  - Make sure your parquet files are in: `C:\Users\ngoya\big data project\Judicial-AI-System\data\hdfs\input\`
  - Run: `.\hdfs.cmd dfs -put "C:\Users\ngoya\big data project\Judicial-AI-System\data\hdfs\input\*.parquet" /data/hdfs/input/`
  - Wait for upload to complete...

- [ ] **Verify files uploaded**
  - Run: `.\hdfs.cmd dfs -ls /data/hdfs/input/`
  - Expected: See all your .parquet files listed
  - ✅ If files are there, upload successful!

---

## 🎯 RUN PIPELINE (5 minutes)

- [ ] **Run the complete pipeline**
  - Open PowerShell (any window)
  - Run: `cd "C:\Users\ngoya\big data project\Judicial-AI-System"`
  - Run: `python -c "from src.data_import_preprocessing import run_complete_pipeline; run_complete_pipeline()"`
  - Watch output...
  - ✅ Pipeline completes without errors!

---

## 📋 FINAL CHECKLIST

- [ ] Process data successfully
- [ ] Data cleaned and validated (99%+ quality)
- [ ] Processed files in: `/data/hdfs/processed/`
- [ ] Logs show no errors
- [ ] Ready for NLP phase

---

## 🛑 STOPPING HADOOP

When done for the day:

- [ ] **Stop HDFS Services**
  - In the `start-dfs.cmd` window: Press `Ctrl + C`
  - Or run in new window: `cd C:\hadoop\sbin` then `.\stop-dfs.cmd`

- [ ] **Restart services next time**
  - Same process: open Terminal 1, then Terminal 2, then Terminal 3

---

## 🆘 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| "hdfs.cmd not found" | Close ALL PowerShell windows and reopen one |
| "Connection refused" | Make sure `start-dfs.cmd` window is still running |
| "Only single namenode" | This is OK, continue |
| "Java not found" | Check JAVA_HOME is set: `echo $env:JAVA_HOME` |
| "Found 0 items" but no error | This is OK, HDFS is working |
| "Permission denied" | Run PowerShell as Administrator |

---

## 📚 REFERENCE

- Full Guide: `HADOOP_SETUP_COMPLETE.md`
- Setup Script: `setup_hadoop.ps1`
- Web Interface: http://localhost:50070/ (while HDFS running)
- Project Root: `C:\Users\ngoya\big data project\Judicial-AI-System`

---

**Total Time: ~30 minutes**

✅ When this entire checklist is complete, Hadoop is ready for your pipeline! 🎉
