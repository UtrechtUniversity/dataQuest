
import os
import tarfile
import gzip
import json
import xml.etree.ElementTree as ET
from typing import Dict, Union, Any, Optional, List
import logging


class XMLExtractor:
    """Class for extracting XML content and metadata from nested .tgz files."""  # noqa: E501
    def __init__(self, root_dir: str, output_dir: str):
        """
        Initializes the XMLExtractor object.

        Parameters:
            root_dir (str): The root directory containing .tgz files.
            output_dir (str): The output directory for saving extracted JSON files.  # noqa: E501
        """
        self.root_dir = root_dir
        self.output_dir = output_dir
        self.fields = [
            "title", "language", "issuenumber", "date", "identifier",
            "temporal", "recordRights", "publisher", "spatial", "source",
            "recordIdentifier", "type", "isPartOf"
        ]

    def extract_xml_string(self) -> None:
        """
        Extracts XML content and metadata from .tgz files in the root directory.  # noqa: E501
        """
        for folder_name in os.listdir(self.root_dir):
            folder_path = os.path.join(self.root_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue
            if not folder_name.isdigit():  # Exclude in_progress, manifests, and ocr_complete folders and log files.  # noqa: E501
                continue
            self.process_folder(folder_name, folder_path)

    def process_folder(self, folder_name: str, folder_path: str) -> None:
        """
        Processes .tgz files within a folder.

        Parameters:
            folder_name (str): Name of the folder being processed.
            folder_path (str): Path to the folder being processed.
        """
        for tgz_filename in os.listdir(folder_path):
            if not tgz_filename.endswith('.tgz'):
                continue
            tgz_file_path = os.path.join(folder_path, tgz_filename)
            base_name = os.path.splitext(tgz_filename)[0]
            output_folder = os.path.join(self.output_dir, folder_name)
            os.makedirs(output_folder, exist_ok=True)
            try:
                with tarfile.open(tgz_file_path, "r:gz") as outer_tar:
                    news_dict = self.process_tar(outer_tar)
            except tarfile.TarError as e:
                logging.error(f"Error extracting {tgz_filename}: {e}")
                continue
            output_file = os.path.join(output_folder, f"{base_name}.json.gz")
            self.save_as_json_compressed(news_dict, output_file)
            # self.save_as_json(news_dict, output_file)

    def process_tar(self, outer_tar: tarfile.TarFile) -> Dict[str, Union[Dict[str, str], Dict[int, Dict[str, str]]]]:  # noqa: E501
        """
        Processes a .tgz file and extracts XML content and metadata.

        Parameters:
            outer_tar (tarfile.TarFile): The .tgz file being processed.

        Returns:
            Dict[str, Union[Dict[str, str], Dict[int, Dict[str, str]]]]: A dictionary containing extracted content and metadata.  # noqa: E501
        """
        news_dict: Dict[str, Any] = {"newsletter_metadata": {}, "articles": {}}
        id = 0
        for entry in outer_tar:
            try:
                if entry.name.endswith(".xml"):
                    file = outer_tar.extractfile(entry)
                    if file is not None:
                        content = file.read()
                        xml_content = content.decode('utf-8', 'ignore')
                        article = self.extract_article(xml_content, entry.name)
                        id += 1
                        news_dict["articles"][id] = article

                elif entry.name.endswith(".gz"):
                    gz_member = next(member for member in outer_tar.getmembers() if member.name.endswith('.gz'))  # noqa: E501
                    with outer_tar.extractfile(gz_member) as gz_file:  # type: ignore  # noqa: E501
                        with gzip.open(gz_file, 'rt') as xml_file:
                            xml_string = xml_file.read()
                            if isinstance(xml_string, bytes):
                                xml_string = xml_string.decode('utf-8')
                            newsletter_metadata = self.extract_meta(xml_string)
                            news_dict["newsletter_metadata"] = newsletter_metadata  # noqa: E501
                else:
                    continue
            except Exception as e:
                logging.error(f"Error processing file {entry.name}: {e}")
        return news_dict

    @staticmethod
    def save_as_json_compressed(data: Dict[str, Union[Dict[str, str], Dict[int, Dict[str, str]]]], output_file: str) -> None:  # noqa: E501
        """
        Saves data as compressed JSON using gzip.

        Parameters:
            data (Dict[str, Union[Dict[str, str], Dict[int, Dict[str, str]]]]): Data to be saved as JSON.  # noqa: E501
            output_file (str): Path to the output JSON file.
        """
        try:
            with gzip.open(output_file, 'wt') as json_file:
                json.dump(data, json_file, indent=4)
        except Exception as e:
            logging.error(f"Error saving compressed JSON to {output_file}: {e}")  # noqa: E501

    # @staticmethod
    # def save_as_json(data: Dict[str, Union[Dict[str, str], Dict[int, Dict[str, str]]]], output_file: str) -> None:  # noqa: E501
    #     """
    #     Saves data as JSON to a specified file.

    #     Parameters:
    #         data (Dict[str, Union[Dict[str, str], Dict[int, Dict[str, str]]]]): Data to be saved as JSON.  # noqa: E501
    #         output_file (str): Path to the output JSON file.
    #     """
    #     try:
    #         with open(output_file, 'w') as json_file:
    #             json.dump(data, json_file, indent=4)
    #     except Exception as e:
    #         logging.error(f"Error saving JSON to {output_file}: {e}")

    @staticmethod
    def extract_article(xml_content: str, file_name: str) -> Dict[str, Union[str, List[Optional[str]]]]:  # noqa: E501
        """
        Extracts article title and body from XML content.

        Parameters:
            xml_content (str): XML content of the article.
            file_name (str): Name of the XML file.

        Returns:
            Dict[Optional[str], list[str]]: A dictionary containing the extracted title and body of the article.
              body contains a list of paragraphs.  # noqa: E501
        """
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            logging.error(f"Failed to parse XML from file: {file_name}")
            return {}

        title_values = [element.text for element in root.iter() if element.tag.endswith('title')]  # noqa: E501
        if len(title_values) > 1:
            logging.warning("More than one titles are extracted for the article.")  # noqa: E501
        if not title_values:
            logging.warning("No title is extracted for the article.")
            title = ""
        else:
            title = title_values[0] if title_values[0] is not None else ""
            # title = title_values[0]

        body_values = [element.text for element in root.iter() if element.tag.endswith('p')]  # noqa: E501
        if not body_values:
            logging.warning("No body is extracted.")
            body = []
        # elif len(body_values) > 1:
        #     logging.warning("There are more than one paragraphs in the article.")  # noqa: E501
        #     body = ' '.join(body_values)
        else:
            # body = body_values[0]
            body = body_values

        return {"title": title, "body": body}

    def extract_meta(self, xml_string: str) -> Dict[str, Union[str, None]]:
        """
        Extracts metadata from XML string.

        Parameters:
            xml_string (str): XML string containing metadata.

        Returns:
            Dict[str, Union[str, None]]: A dictionary containing the extracted metadata.  # noqa: E501
        """
        newsletter_metadata: Dict[str, Union[str, None]] = {}

        try:
            root = ET.fromstring(xml_string)
        except ET.ParseError:
            logging.error("Failed to parse XML from file")
            return newsletter_metadata

        for field in self.fields:
            field_values = [element.text for element in root.iter() if element.tag.endswith(field)]  # noqa: E501
            if len(field_values) > 1:
                logging.warning(f"More than one {field}s are extracted from metadata.")  # noqa: E501
            if not field_values:
                logging.warning(f"No {field} is extracted.")
                newsletter_metadata[field] = None
            else:
                filtered_field_values = [value for value in field_values if value is not None]  # noqa: E501
                newsletter_metadata[field] = filtered_field_values[0] if field != "spatial" else ", ".join(filtered_field_values)  # noqa: E501

                # newsletter_metadata[field] = field_values[0] if field != "spatial" else ", ".join(field_values)  # noqa: E501

        return newsletter_metadata
