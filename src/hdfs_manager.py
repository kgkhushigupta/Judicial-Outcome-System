import subprocess
import os
import shutil
import logging

logger = logging.getLogger(__name__)

class HDFSManager:
    def __init__(self, base_uri="hdfs:///judicial"):
        self.base_uri = base_uri
        self.local_hdfs_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "hdfs")
        os.makedirs(self.local_hdfs_root, exist_ok=True)
        self.hdfs_available = self._check_hdfs()

    def _check_hdfs(self):
        try:
            result = subprocess.run("hdfs dfs -ls /", shell=True, capture_output=True, timeout=5)
            if result.returncode == 0:
                logger.info("[HDFS] HDFS cluster detected and connected.")
                return True
        except Exception:
            pass
        logger.info("[HDFS] No HDFS cluster found. Using local filesystem fallback at %s", self.local_hdfs_root)
        return False

    def upload(self, local_path, hdfs_path):
        if not os.path.exists(local_path):
            logger.warning("[HDFS] Source file not found: %s", local_path)
            return False
        if self.hdfs_available:
            cmd = f'hdfs dfs -put -f "{local_path}" {self.base_uri}/{hdfs_path}'
            result = subprocess.run(cmd, shell=True, capture_output=True)
            if result.returncode == 0:
                logger.info("[HDFS] Uploaded %s -> %s/%s", local_path, self.base_uri, hdfs_path)
                return True
            else:
                logger.warning("[HDFS] Upload failed, falling back to local: %s", result.stderr.decode())
        dest = os.path.join(self.local_hdfs_root, hdfs_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(local_path, dest)
        logger.info("[HDFS-LOCAL] Copied %s -> %s", local_path, dest)
        return True

    def download(self, hdfs_path, local_path):
        if self.hdfs_available:
            cmd = f'hdfs dfs -get -f {self.base_uri}/{hdfs_path} "{local_path}"'
            result = subprocess.run(cmd, shell=True, capture_output=True)
            if result.returncode == 0:
                return True
        src = os.path.join(self.local_hdfs_root, hdfs_path)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            shutil.copy2(src, local_path)
            return True
        return False

    def mkdir(self, hdfs_path):
        if self.hdfs_available:
            cmd = f"hdfs dfs -mkdir -p {self.base_uri}/{hdfs_path}"
            subprocess.run(cmd, shell=True, capture_output=True)
        local_dir = os.path.join(self.local_hdfs_root, hdfs_path)
        os.makedirs(local_dir, exist_ok=True)

    def exists(self, hdfs_path):
        if self.hdfs_available:
            cmd = f"hdfs dfs -test -e {self.base_uri}/{hdfs_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True)
            return result.returncode == 0
        return os.path.exists(os.path.join(self.local_hdfs_root, hdfs_path))

    def list_files(self, hdfs_path=""):
        if self.hdfs_available:
            cmd = f"hdfs dfs -ls {self.base_uri}/{hdfs_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
        local_dir = os.path.join(self.local_hdfs_root, hdfs_path)
        if os.path.exists(local_dir):
            entries = os.listdir(local_dir)
            return "\n".join(entries)
        return ""

    def get_status(self):
        return {
            "hdfs_available": self.hdfs_available,
            "base_uri": self.base_uri if self.hdfs_available else f"local://{self.local_hdfs_root}",
            "storage_mode": "HDFS Distributed" if self.hdfs_available else "Local Filesystem Fallback"
        }
