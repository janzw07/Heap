import hashlib
import sys
from collections import defaultdict
import psutil
import os
from pathlib import Path

def get_drive_options():
    all_partitions = psutil.disk_partitions(all=True)

    is_mac = sys.platform == 'darwin'

    ignored_fstypes = {
        'squashfs', 'tmpfs', 'devfs', 'autofs', 'overlay', 'shm',
        'sysfs', 'proc', 'devtmpfs', 'cd9660', 'nullfs', 'mapfs', ''
    }

    ignored_prefixes = (
        '/System/Volumes/',
        '/private/var',
        '/boot/efi',
        '/snap',
        '/dev',
        '/net',
        '/home',
    )

    drives = []
    for p in all_partitions:

        #skip drive if not valid

        if p.fstype in ignored_fstypes:
            continue

        if p.mountpoint.startswith(ignored_prefixes) and p.mountpoint != '/System/Volumes/Data':
            continue

        if is_mac and not (p.mountpoint == '/' or p.mountpoint == '/System/Volumes/Data' or p.mountpoint.startswith('/Volumes/')):
            continue


        drives.append(p)

    drive_data = {}

    is_mac = sys.platform == 'darwin'
    gb = (1000 ** 3) if is_mac else (1024 ** 3)

    for drive in drives:
        try:
            usage = psutil.disk_usage(drive.mountpoint)

            if is_mac and (drive.mountpoint == '/' or drive.mountpoint.startswith('/System/Volumes')): #for mac
                display_name = "Macintosh HD"

            elif drive.mountpoint == '/':
                display_name = "OS Drive"
            else:
                display_name = drive.mountpoint


            drive_data[display_name] = {
                "mountpoint": drive.mountpoint,
                "total": usage.total / gb,
                "used": usage.used / gb,
                "free": usage.free / gb
            }
        except (PermissionError, OSError):
            continue

    return drive_data


def compute_file_hash(file_path, chunk_size=65536):
    hasher = hashlib.md5()

    try:
        with open(file_path, 'rb') as file:
            while chunk := file.read(chunk_size):
                hasher.update(chunk)

            return hasher.hexdigest()
    except (PermissionError, OSError):
        return None


class DiskAnalyzer:
    def __init__(self, drive, directory):
        self.drive = drive
        self.dir = directory

        self.cancel_scan = False

    def file_generator(self, current_dir=None):

        if current_dir is None:
            current_dir = self.dir

        try:
            with os.scandir(current_dir) as entries:
                for entry in entries:

                    if entry.is_file(follow_symlinks=False):
                        yield entry.stat().st_size, entry.path

                    elif entry.is_dir(follow_symlinks=False):
                        yield from self.file_generator(entry.path)

        except PermissionError:
            pass
        except FileNotFoundError:
            pass
        except OSError as e:
            print(f"Skipped {current_dir} because of an error {e}")




    def duplicate_search(self, progress_callback=None, progress_save=None):

        self.cancel_scan = False

        if progress_callback:
            progress_callback(current=0, total=0)

        files_by_size = defaultdict(list)

        for size, path in self.file_generator():
            if self.cancel_scan:
                return None

            files_by_size[size].append(path)

        #filtering by paths
        potential_duplicates = {size:paths for size, paths in files_by_size.items() if len(paths) > 1}

        #final dict of duplicates
        duplicates = {}

        total_items = len(potential_duplicates) #total of our progress_bar if determinate
        processed=0

        #filtering by hash
        for size, paths in potential_duplicates.items():

            if self.cancel_scan:
                return None

            #declaration of progress
            if progress_callback:
                progress_callback(current=processed, total=total_items)

            processed += 1

            files_by_hash = defaultdict(list) #empty

            for path in paths:
                file_hash = compute_file_hash(path) #compute hash for each file

                if file_hash is not None:
                    files_by_hash[file_hash].append(path)

            for file_hash, files in files_by_hash.items():
                if len(files) > 1:
                    duplicates[(size,file_hash)] = files

        #declaring again
        if progress_callback:
            progress_callback(current=total_items, total=total_items)

        # sorting by size
        duplicates = dict(sorted(duplicates.items(), key=lambda x: x[0][0], reverse=True))

        if not self.cancel_scan:
            progress_save(data=duplicates, scan_type="duplicates") #to save scan

        return duplicates

    def space_scan(self, progress_callback=None, progress_save=None):

        self.cancel_scan = False

        if progress_callback:
            progress_callback(current=0, total=0)

        #for all items dirs files etc
        item_sizes = defaultdict(int)

        scan_root = Path(self.dir)
        scan_root_depth = len(scan_root.parts)

        for size, path in self.file_generator():
            if self.cancel_scan:
                return None

            item_sizes[path] += size #adding size for each path to evaluate its weight

            for parent in Path(path).parents:
                if len(parent.parts) > scan_root_depth:
                    item_sizes[str(parent)] += size #adding size for parents of our path, because they have to carry weight of their children

        grouped_by_size = defaultdict(list)

        for path, total_size in item_sizes.items():
            if self.cancel_scan:
                return None

            grouped_by_size[total_size].append(path)

        total_files = len(grouped_by_size)

        if progress_callback:
            progress_callback(current=0, total=total_files)

        #sorting by size
        sorted_by_size = dict(sorted(grouped_by_size.items(), key=lambda x: x[0], reverse=True))

        if progress_callback:
            progress_callback(current=total_files, total=total_files)

        if not self.cancel_scan:
            progress_save(data=sorted_by_size, scan_type="space")

        return sorted_by_size









