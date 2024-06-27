from dataQuest.preprocessor.parser import XMLExtractor
from argparse import ArgumentParser
from pathlib import Path
import logging


logging.basicConfig(filename='extractor.log', level=logging.DEBUG)



def parse_arguments():
    parser = ArgumentParser(
        prog="convert_input_files.py",
        description="Convert nested gzip files to compressed json")
    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    return parser.parse_args()

if __name__=="__main__":
    args = parse_arguments()
    extractor = XMLExtractor(Path(args.input_dir), Path(args.output_dir))
    extractor.extract_xml_string()
