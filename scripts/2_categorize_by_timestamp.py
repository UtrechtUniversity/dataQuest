import os
from tqdm import tqdm
from shutil import move
import argparse
from typing import Iterable
from pathlib import Path
from interest.temporal_categorization import PERIOD_TYPES
from interest.temporal_categorization.timestamped_data import TimestampedData

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Categorize articles by timestamp.")

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Base directory for reading input files.",
    )
    parser.add_argument(
        "--period-type",
        type=str,
        required=True,
        choices=list(PERIOD_TYPES.keys()),
        help="Time periods",
    )
    parser.add_argument(
        "--glob",
        type=str,
        required=True,
        default="*.json",
        help="Glob pattern for find input files; e.g. '*.json'.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
       required=True,
        help="The directory for storing output files.",
    )

    args = parser.parse_args()

    if not args.input_dir.is_dir():
        parser.error(f"Not a directory: '{str(args.input_dir.absolute())}'")

    time_period_class = PERIOD_TYPES[args.period_type]
    timestamped_objects: Iterable[TimestampedData] = [
        time_period_class(path) for path in args.input_dir.rglob(args.glob)
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for timestamped_object in tqdm(timestamped_objects, desc="Categorize by timestamp", unit="file"):
        timestamp = timestamped_object.categorize()
        # Create the decade folder if it doesn't exist
        timestamp_folder = os.path.join(args.output_dir, str(timestamp))
        if not os.path.exists(timestamp_folder):
            os.makedirs(timestamp_folder)

        # Move the JSON file to the decade folder
        try:
            move(timestamped_object.filename, timestamp_folder)
            print(f"Moved {timestamped_object.filename} to {timestamp_folder}")
        except Exception as e:
            print(f"Error moving {timestamped_object.filename} to {timestamp_folder}: {e}")
