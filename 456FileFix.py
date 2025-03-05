import os
import shutil
import hashlib
import logging
from tqdm import tqdm
from pathlib import Path
from collections import Counter
import argparse
import json
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure logging to log to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("4NSIKfilefix.log"),
        logging.StreamHandler()
    ]
)

def load_config(config_file: str) -> dict:
    """Load configuration from a JSON file."""
    with open(config_file, 'r') as file:
        return json.load(file)

def organize_files(folders: dict, download_dir: str) -> Counter:
    """Organize files into separate folders based on their extensions."""
    for folder, extensions in folders.items():
        folder_path = Path(download_dir) / folder
        if not folder_path.exists():
            folder_path.mkdir(parents=True)

    file_counts = Counter()
    total_files = len(os.listdir(download_dir))
    start_time = time.time()
    pbar = tqdm(total=total_files, desc="Organizing files", unit="file", unit_scale=True)
    for file in os.listdir(download_dir):
        file_path = Path(download_dir) / file
        if file_path.is_file():
            for folder, extensions in folders.items():
                if any(file.endswith(extension) for extension in extensions):
                    destination_path = Path(download_dir) / folder / file
                    shutil.move(file_path, destination_path)
                    file_counts[folder] += 1
                    logging.info(f"Moved {file} to {folder}")
                    break
        pbar.update(1)
    end_time = time.time()
    elapsed_time = end_time - start_time
    pbar.set_postfix({'Elapsed Time': f'{elapsed_time:.2f}s'})
    pbar.close()
    return file_counts

def remove_duplicates(folders: dict, download_dir: str) -> None:
    """Remove duplicate files from each folder."""
    for folder in folders.keys():
        folder_path = Path(download_dir) / folder
        files = os.listdir(folder_path)
        seen = set()
        start_time = time.time()
        pbar = tqdm(total=len(files), desc=f"Removing duplicates from {folder}", unit="file", unit_scale=True)
        for file in files:
            file_path = folder_path / file
            if file_path.is_file():
                with open(file_path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                if file_hash in seen:
                    os.remove(file_path)
                    logging.info(f"Removed duplicate file {file} from {folder}")
                else:
                    seen.add(file_hash)
            pbar.update(1)
        end_time = time.time()
        elapsed_time = end_time - start_time
        pbar.set_postfix({'Elapsed Time': f'{elapsed_time:.2f}s'})
        pbar.close()

def clean_up_empty_folders(download_dir: str) -> None:
    """Clean up empty folders."""
    for folder in os.listdir(download_dir):
        folder_path = Path(download_dir) / folder
        if folder_path.is_dir() and not os.listdir(folder_path):
            folder_path.rmdir()
            logging.info(f"Removed empty folder {folder}")

def generate_summary(file_counts: Counter) -> None:
    """Generate a summary report."""
    print("\nFile counts:")
    for folder, count in file_counts.items():
        print(f"{folder}: {count}")

    print("\nSummary report:")
    print("Files organized into separate folders.")
    print("Duplicates removed.")
    print("Empty folders cleaned up.")
    print("File counts displayed above.")

def main(args: list[str]) -> None:
    parser = argparse.ArgumentParser(description="Organize and clean up files in Downloads.")
    parser.add_argument('--config', required=True, help="Path to the configuration file.")
    options = parser.parse_args(args)
    
    config = load_config(options.config)
    folders = config['folders']
    download_dir = config['download_dir']

    file_counts = organize_files(folders, download_dir)
    remove_duplicates(folders, download_dir)
    clean_up_empty_folders(download_dir)
    generate_summary(file_counts)

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
