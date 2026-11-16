import json
from pathlib import Path
from core.exceptions import ScanLoadError, ScanSaveError, FileDeletionError
import shutil
import os

from core.decorators import retry

def determine_cache_path():
    cache_dir = Path.home() / ".heap"

    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir / f"cache.hs"

class FileManager:
    def __init__(self):
        self.cache_path = determine_cache_path()

    @retry(times=3)
    def json_save(self, dic, scan_type, base_dir):

        data = {}

        if scan_type == "duplicates":
            for key, files in dic.items():
                if isinstance(key, tuple):
                    str_key = f"{key[0]}_{key[1]}"  # (size, hash) ---> "size_hash"
                    data[str_key] = files
                else:
                    raise TypeError(f"Expected tuple got: {type(key)}")
        elif scan_type == "space":
            for key, files in dic.items():
                data[str(key)] = files

        envelope = {
            "scan_type": scan_type,
            "base_dir": base_dir,
            "data": data
        }

        try:
            with open(self.cache_path, "w", encoding="utf-8") as write:
                json.dump(envelope, write, indent=4)
            print(f"SCAN SAVED TO {str(self.cache_path)}")
        except PermissionError:
            raise ScanSaveError("No required permissions to save scan to the drive.")
        except OSError as e:
            raise ScanSaveError(f"OS Error during write: {e}")
        except Exception as e:
            raise ScanSaveError(f"Unexpected write error JSON: {e}")

    @retry(times=3, delay=0.2)
    def json_load(self):

        if not self.cache_path.exists():
            raise ScanLoadError("Scan file does not exist. Please run a scan first.")

        try:
            with open(self.cache_path, "r", encoding="utf-8") as read:
                envelope = json.load(read)
        except json.JSONDecodeError:
            raise ScanLoadError("Scan file is empty, damaged, or does not exist.")
        except Exception as e:
            raise ScanLoadError(f"Unexpected scan save reading error: {e}")

        if not isinstance(envelope, dict):
            raise ScanLoadError("Wrong data format in the file")


        scan_type = envelope.get("scan_type")
        base_dir = envelope.get("base_dir")
        raw_data = envelope.get("data", {})

        if scan_type is None or raw_data is None:
            raise ScanLoadError("Lack of required data in read file (scan_type or data)")

        data = {}

        if scan_type == "duplicates":
            try:
                for key, files in raw_data.items():
                    size_str, file_hash = key.split("_")
                    data[(int(size_str), file_hash)] = files
            except Exception as e:
                raise ScanLoadError(f"Damaged duplicates scan structure: {e}")
        elif scan_type == "space":
            try:
                for key, files in raw_data.items():
                    data[int(key)] = files
            except Exception as e:
                raise ScanLoadError(f"Damaged space scan structure: {e}")

        return scan_type, data, base_dir

    def delete_cache(self):
        try:
            if self.cache_path.exists():
                self.cache_path.unlink()
                print("CACHE HAS BEEN DELETED")
        except Exception as e:
            print(f"Unable to delete cache: {e}")

    def delete_file(self, file_path):
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
        except FileNotFoundError:
            raise FileDeletionError("not_found")
        except PermissionError:
            raise FileDeletionError("File is being used, or lack of permissions")
        except Exception as e:
            raise FileDeletionError(str(e))


