# dataQuest

The code in this repository implements a pipeline to extract specific articles from a large corpus.

Currently, this tool is tailored for the [Delpher Kranten](https://www.delpher.nl/nl/kranten) corpus, but it can be adapted for other corpora as well.

Articles can be filtered based on individual or multiple features such as title, year, decade, or a set of keywords. To select the most relevant articles, we utilize models such as tf-idf. These models are configurable and extendable.


## Getting Started
Clone this repository to your working station to obtain examples and python scripts:
```
git clone https://github.com/UtrechtUniversity/dataQuest.git
```

### Prerequisites
To install and run this project you need to have the following prerequisites installed.
```
- Python [>=3.9, <3.11]
```

### Installation
#### Option 1 - Install dataQuest package
To run the project, ensure to install the dataQuest package that is part of this project.
```
pip install dataQuest
```
#### Option 2 - Run from source code
If you want to run the scripts without installation you need to:  

- Install requirement
```commandline
pip install setuptools wheel
python -m pip install build
```
Change your current working directory to the location of your pyproject.toml file.
```
python -m build
pip install .
```
- Set PYTHONPATH environment: 
On Linux and Mac OS, you might have to set the PYTHONPATH environment variable to point to this directory.

```commandline
export PYTHONPATH="current working directory/dataQuest:${PYTHONPATH}"
```
### Built with
These packages are automatically installed in the step above:
* [scikit-learn](https://scikit-learn.org/stable/)
* [SciPy](https://scipy.org)
* [NumPy](https://numpy.org)
* [spaCy](https://spacy.io)
* [pandas](https://pandas.pydata.org)

## Usage
### 1. Preparation
#### Data Prepration
Before proceeding, ensure that you have the data prepared in the following format: The expected format is a set of JSON files compressed in the .gz format. Each JSON file contains metadata related to a newsletter, magazine, etc., as well as a list of article titles and their corresponding bodies. These files may be organized within different folders or sub-folders.
Below is a snapshot of the JSON file format:
```commandline
{
    "newsletter_metadata": {
        "title": "Newspaper title ..",
        "language": "NL",
        "date": "1878-04-29",
        ...
    },
    "articles": {
        "1": {
            "title": "title of article1 ",
            "body": [
                "paragraph 1 ....",
                "paragraph 2...."
            ]
        },
        "2": {
            "title": "title of article2",
            "body": [
                "text..."  
             ]
        }
    }
}    
```

In our use case, the harvested KB data is in XML format. We have provided the following script to transform the original data into the expected format.
```
from dataQuest.preprocessor.parser import XMLExtractor

extractor = XMLExtractor(Path(input_dir), Path(output_dir))
extractor.extract_xml_string()
```

Navigate to scripts folder and run:
```
python3 convert_input_files.py --input_dir path/to/raw/xml/data --output_dir path/to/converted/json/compressed/output
```
#### Customize input-file

In order to define a corpus with a new data format you should:

- add a new input_file_type to [INPUT_FILE_TYPES](https://github.com/UtrechtUniversity/dataQuest/blob/main/dataQuest/filter/__init__.py)
- implement a class that inherits from [input_file.py](https://github.com/UtrechtUniversity/dataQuest/blob/main/dataQuest/filter/input_file.py).
This class is customized to read a new data format. In our case-study we defined [delpher_kranten.py](https://github.com/UtrechtUniversity/dataQuest/blob/main/dataQuest/filter/delpher_kranten.py).


### 2. Filtering
In this step, you may select articles based on a filter or a collection of filters. Articles can be filtered by title, year, decade, or a set of keywords defined in the ```config.json``` file.
```commandline
 "filters": [
        {
            "type": "AndFilter",
            "filters": [
                {
                    "type": "OrFilter",
                    "filters": [
                        {
                            "type": "YearFilter",
                            "start_year": 1800,
                            "end_year": 1910
                        },
                        {
                            "type": "DecadeFilter",
                            "decade": 1960
                        }
                    ]
                },
                {
                    "type": "NotFilter",
                    "filter": {
                        "type": "ArticleTitleFilter",
                        "article_title": "Advertentie"
                    },
                    "level": "article"
                },
                {
                    "type": "KeywordsFilter",
                    "keywords": ["sustainability", "green"]
                }
            ]
        }
    ]

```
run the following to filter the articles:
```commandline
python3 scripts/step1_filter_articles.py --input-dir "path/to/converted/json/compressed/output/" --output-dir "output_filter/" --input-type "delpher_kranten" --glob "*.gz"
```
In our case, input-type is "delpher_kranten", and input data is a set of compresed json files with ```.gz``` extension.

The output of this script is a JSON file for each selected article in the following format:
```commandline
{
    "file_path": "output/transfered_data/00/KRANTEN_KBPERS01_000002100.json.gz",
    "article_id": "5",
    "Date": "1878-04-29",
    "Title": "Opregte Haarlemsche Courant"
}
```
### 3. Categorization by timestamp
The output files generated in the previous step are categorized based on a specified [period-type](https://github.com/UtrechtUniversity/dataQuest/blob/main/dataQuest/temporal_categorization/__init__.py), 
such as ```year``` or ```decade```. This categorization is essential for subsequent steps, especially if you intend to apply tf-idf or other models to specific periods. In our case, we applied tf-idf per decade.

```commandline
python3 scripts/step2_categorize_by_timestamp.py --input-dir "output_filter/" --glob "*.json" --period-type "decade"  --output-dir "output_timestamped/"

```
The output consists of a .csv file for each period, such as one file per decade, containing the ```file_path``` and ```article_id``` of selected articles.

### 4. Select final articles
This step is applicable when articles are filtered (in step 2) using a set of keywords. 
By utilizing tf-idf, the most relevant articles related to the specified topic (defined by the provided keywords) are selected.

Before applying tf-idf, articles containing any of the specified keywords in their title are selected.

From the rest of articles, to choose the most relevant ones, you can specify one of the following criteria in [config.py](https://github.com/UtrechtUniversity/dataQuest/blob/main/config.json):

- Percentage of selected articles with the top scores
- Maximum number of selected articles with the top scores 
- Threshold for the value of cosine similarity between the embeddings of list of keywords and each article.


```commandline
  "article_selector":
    {
      "type": "percentage",
      "value": "30"
    },
    
    OR
  
  "article_selector":
    {
      "type": "threshold",
      "value": "0.02"
    },
    
    OR
    
   "article_selector":
    {
      "type": "num_articles",
      "value": "200"
    }, 
```

The following script, add a new column, ```selected``` to the .csv files from the previous step.
```commandline
python3 scripts/step3_select_final_articles.py --input-dir "output/output_timestamped/"
```

### 5. Generate output
As the final step of the pipeline, the text of the selected articles is saved in a .csv file, which can be used for manual labeling. The user has the option to choose whether the text should be divided into paragraphs or a segmentation of the text.
This feature can be set in [config.py](https://github.com/UtrechtUniversity/dataQuest/blob/main/config.json).
```commandline
"output_unit": "paragraph"

OR

"output_unit": "full_text"

OR
"output_unit": "segmented_text"
"sentences_per_segment": 10
```

```commandline
python3 scripts/step4_generate_output.py --input-dir "output/output_timestamped/” --output-dir “output/output_results/“  --glob “*.csv”
```
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

Project Link: [https://github.com/UtrechtUniversity/dataQuest](https://github.com/UtrechtUniversity/dataQuest)

