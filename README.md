# INTEREST

The code in this repository is implemented to investigate how the sentiment of the news articles changes over decades regarding the topics such as fossil fuel, green energy, etc. The interest python package offers a variety of methods for analysing the sentiment of the news articles. From traditional dictionary-based approaches to cutting-edge similarity-based techniques. The methods are tested on a large dataset of news articles harvested from the national library of the Netherlans ([KB](https://www.kb.nl)).

## Getting Started
Clone this repository to your working station to obtain example notebooks and python scripts:
```
git clone https://github.com/UtrechtUniversity/historical-news-sentiment.git
```

### Prerequisites
To install and run this project you need to have the following prerequisites installed.
```
- Python [>=3.9, <3.11]
```

### Installation
To run the project, ensure to install the interest package that is part of this project.
```
pip install interest
```

### Built with
These packages are automatically installed in the step above:
* [scikit-learn](https://scikit-learn.org/stable/)
* [SciPy](https://scipy.org)

## Usage
### 1. Preparation
Harvested KB data is in xml format. Before proceeding, ensure that you have the data prepared. This entails organizing your data into a specific directory structure. Within this directory, you should have several folders for each newsletter, each containing JSON files compressed in the .gz format. These compressed JSON files encapsulate metadata pertaining to newsletters, alongside lists comprising article titles and their corresponding bodies.
```
from interest.preprocessor.parser import XMLExtractor

extractor = XMLExtractor(Path(input_dir), Path(output_dir))
extractor.extract_xml_string()
```

Navigate to scripts folder and run:
```
python3 convert_input_files.py --input_dir path/to/raw/xml/data --output_dir path/to/converted/json/compressed/output
```

### 2. Filtering
To be compeleted...

## About the Project
**Date**: February 2024

**Researcher(s)**:

Pim Huijnen (p.huijnen@uu.nl)

**Research Software Engineer(s)**:

- Parisa Zahedi (p.zahedi@uu.nl)
- Shiva Nadi (s.nadi@uu.nl)
- Matty Vermet (m.s.vermet@uu.nl)


### License

The code in this project is released under [MIT license](LICENSE).

## Contributing

Contributions are what make the open source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

To contribute:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

Pim Huijnen - p.huijnen@uu.nl

Project Link: [https://github.com/UtrechtUniversity/historical-news-sentiment](https://github.com/UtrechtUniversity/historical-news-sentiment)