# Hadoop Setup Script for Windows PowerShell
# Run this script as Administrator to automatically set up Hadoop

# ============================================================
# BEFORE RUNNING: UPDATE THESE PATHS!
# ============================================================

$HADOOP_PATH = "C:\hadoop"                    # Change to your Hadoop folder
$JAVA_PATH = "C:\Program Files\Java\jdk-11"  # Change to your Java folder
$PROJECT_PATH = "C:\Users\ngoya\big data project\Judicial-AI-System"
$DATA_PATH = "$PROJECT_PATH\data\hdfs\input"

# ============================================================
# Script starts here - no edits needed below
# ============================================================

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Hadoop Setup Script for Windows" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Step 0: Verify paths exist
Write-Host "Step 1: Verifying paths..." -ForegroundColor Yellow

if (-not (Test-Path $HADOOP_PATH)) {
    Write-Host "ERROR: Hadoop path not found: $HADOOP_PATH" -ForegroundColor Red
    Write-Host "Please update `$HADOOP_PATH in this script" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $JAVA_PATH)) {
    Write-Host "WARNING: Java path may not exist: $JAVA_PATH" -ForegroundColor Yellow
    Write-Host "Please verify Java is installed and update `$JAVA_PATH" -ForegroundColor Yellow
}

if (-not (Test-Path $DATA_PATH)) {
    Write-Host "WARNING: Data path not found: $DATA_PATH" -ForegroundColor Yellow
    Write-Host "Make sure dataset files are present" -ForegroundColor Yellow
}

Write-Host "✓ Paths verified" -ForegroundColor Green
Write-Host ""

# Step 1: Set environment variables
Write-Host "Step 2: Setting environment variables..." -ForegroundColor Yellow

[Environment]::SetEnvironmentVariable("HADOOP_HOME", $HADOOP_PATH, "User")
Write-Host "  ✓ HADOOP_HOME = $HADOOP_PATH" -ForegroundColor Green

[Environment]::SetEnvironmentVariable("JAVA_HOME", $JAVA_PATH, "User")
Write-Host "  ✓ JAVA_HOME = $JAVA_PATH" -ForegroundColor Green

# Add to PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$HADOOP_BIN = "$HADOOP_PATH\bin"
$HADOOP_SBIN = "$HADOOP_PATH\sbin"

if (-not $currentPath.Contains($HADOOP_BIN)) {
    $newPath = $currentPath + ";$HADOOP_BIN;$HADOOP_SBIN"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "  ✓ Added Hadoop bin and sbin to PATH" -ForegroundColor Green
} else {
    Write-Host "  ✓ Hadoop already in PATH" -ForegroundColor Green
}

Write-Host ""

# Step 2: Create directories
Write-Host "Step 3: Creating Hadoop directories..." -ForegroundColor Yellow

New-Item -Type Directory -Path "$HADOOP_PATH\namenode" -Force | Out-Null
Write-Host "  ✓ Created $HADOOP_PATH\namenode" -ForegroundColor Green

New-Item -Type Directory -Path "$HADOOP_PATH\datanode" -Force | Out-Null
Write-Host "  ✓ Created $HADOOP_PATH\datanode" -ForegroundColor Green

New-Item -Type Directory -Path "$HADOOP_PATH\tmp" -Force | Out-Null
Write-Host "  ✓ Created $HADOOP_PATH\tmp" -ForegroundColor Green

Write-Host ""

# Step 3: Verify Java
Write-Host "Step 4: Verifying Java installation..." -ForegroundColor Yellow

$javaVersion = & java -version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Java is installed:" -ForegroundColor Green
    Write-Host "    $($javaVersion[0])" -ForegroundColor Gray
} else {
    Write-Host "  ✗ Java not found or not working" -ForegroundColor Red
    Write-Host "    Please install Java and update `$JAVA_PATH" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Configure core-site.xml
Write-Host "Step 5: Configuring core-site.xml..." -ForegroundColor Yellow

$coreSiteXml = "$HADOOP_PATH\etc\hadoop\core-site.xml"
if (Test-Path $coreSiteXml) {
    $coreContent = Get-Content $coreSiteXml -Raw
    
    # Check if already configured
    if ($coreContent -like "*fs.defaultFS*") {
        Write-Host "  ✓ core-site.xml already configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ core-site.xml needs manual configuration" -ForegroundColor Yellow
        Write-Host "    Please open: $coreSiteXml" -ForegroundColor Yellow
        Write-Host "    Add this between <configuration> tags:" -ForegroundColor Yellow
        Write-Host "    " -ForegroundColor Yellow
        Write-Host "    <property>" -ForegroundColor Gray
        Write-Host "      <name>fs.defaultFS</name>" -ForegroundColor Gray
        Write-Host "      <value>hdfs://localhost:9000</value>" -ForegroundColor Gray
        Write-Host "    </property>" -ForegroundColor Gray
    }
} else {
    Write-Host "  ✗ core-site.xml not found at $coreSiteXml" -ForegroundColor Red
}

Write-Host ""

# Step 5: Configure hdfs-site.xml
Write-Host "Step 6: Configuring hdfs-site.xml..." -ForegroundColor Yellow

$hdfsSiteXml = "$HADOOP_PATH\etc\hadoop\hdfs-site.xml"
if (Test-Path $hdfsSiteXml) {
    $hdfsContent = Get-Content $hdfsSiteXml -Raw
    
    # Check if already configured
    if ($hdfsContent -like "*dfs.namenode.name.dir*") {
        Write-Host "  ✓ hdfs-site.xml already configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ hdfs-site.xml needs manual configuration" -ForegroundColor Yellow
        Write-Host "    Please open: $hdfsSiteXml" -ForegroundColor Yellow
        Write-Host "    Add this between <configuration> tags:" -ForegroundColor Yellow
        Write-Host "    " -ForegroundColor Yellow
        Write-Host "    <property>" -ForegroundColor Gray
        Write-Host "      <name>dfs.replication</name>" -ForegroundColor Gray
        Write-Host "      <value>1</value>" -ForegroundColor Gray
        Write-Host "    </property>" -ForegroundColor Gray
        Write-Host "    <property>" -ForegroundColor Gray
        Write-Host "      <name>dfs.namenode.name.dir</name>" -ForegroundColor Gray
        Write-Host "      <value>$HADOOP_PATH\namenode</value>" -ForegroundColor Gray
        Write-Host "    </property>" -ForegroundColor Gray
        Write-Host "    <property>" -ForegroundColor Gray
        Write-Host "      <name>dfs.datanode.data.dir</name>" -ForegroundColor Gray
        Write-Host "      <value>$HADOOP_PATH\datanode</value>" -ForegroundColor Gray
        Write-Host "    </property>" -ForegroundColor Gray
    }
} else {
    Write-Host "  ✗ hdfs-site.xml not found at $hdfsSiteXml" -ForegroundColor Red
}

Write-Host ""

# Final summary
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Environment variables set:" -ForegroundColor Green
Write-Host "  - HADOOP_HOME = $HADOOP_PATH" -ForegroundColor Gray
Write-Host "  - JAVA_HOME = $JAVA_PATH" -ForegroundColor Gray
Write-Host "  - PATH extended with Hadoop bin/sbin" -ForegroundColor Gray
Write-Host ""
Write-Host "✓ Directories created:" -ForegroundColor Green
Write-Host "  - $HADOOP_PATH\namenode" -ForegroundColor Gray
Write-Host "  - $HADOOP_PATH\datanode" -ForegroundColor Gray
Write-Host "  - $HADOOP_PATH\tmp" -ForegroundColor Gray
Write-Host ""

Write-Host "🔄 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Close this PowerShell window completely" -ForegroundColor Yellow
Write-Host "2. Open a NEW PowerShell as Administrator" -ForegroundColor Yellow
Write-Host "3. Run: cd $HADOOP_PATH\bin" -ForegroundColor Yellow
Write-Host "4. Run: .\hdfs.cmd namenode -format" -ForegroundColor Yellow
Write-Host "5. Open another PowerShell as Administrator" -ForegroundColor Yellow
Write-Host "6. Run: cd $HADOOP_PATH\sbin" -ForegroundColor Yellow
Write-Host "7. Run: .\start-dfs.cmd" -ForegroundColor Yellow
Write-Host "8. Keep this window open and use another window for HDFS commands" -ForegroundColor Yellow
Write-Host ""

Write-Host "📖 For detailed instructions, see: HADOOP_SETUP_COMPLETE.md" -ForegroundColor Cyan
Write-Host ""
