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
To run the project, ensure to install the dataQuest package that is part of this project.
```
pip install dataQuest
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
python3 convert_input_files.py 
   --input_dir path/to/raw/xml/data 
   --output_dir path/to/converted/json/compressed/output
```
#### Customize input-file

In order to add a new corpus to dataQuest you should:

- prepare your input data in the JSON format explained above.
- add a new input_file_type to [INPUT_FILE_TYPES](https://github.com/UtrechtUniversity/dataQuest/blob/main/dataQuest/filter/__init__.py)
- implement a class that inherits from [input_file.py](https://github.com/UtrechtUniversity/dataQuest/blob/main/dataQuest/filter/input_file.py).
This class is customized to read a new data format. In our case-study we defined [delpher_kranten.py](https://github.com/UtrechtUniversity/dataQuest/blob/main/dataQuest/filter/delpher_kranten.py).


### 2. Filter articles
You can select articles based on a single filter or a combination of filters. Articles can be filtered by title, year, 
decade, or a set of keywords defined in the ```config.json``` file. Logical operators such as AND, OR, and NOT can be used to combine filtering expressions.

In the following example, you select articles that include any of the specified keywords AND were published between 1800 and 1910 AND do not 
contain advertisements (e.g., "Advertentie").
```commandline
 "filters": [
        {
            "type": "AndFilter",
                "filters": [
                        {
                            "type": "YearFilter",
                            "start_year": 1800,
                            "end_year": 1910
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
 ],

```
The steps to select the most relevant articles and generate the output:
1. articles are selected based the filters in the config file 


2. selected articles are categorized based on a specified [period-type](https://github.com/UtrechtUniversity/dataQuest/blob/main/dataQuest/temporal_categorization/__init__.py), 
such as ```year``` or ```decade```. This categorization is essential for subsequent steps, especially in case of applying tf-idf or other models to specific periods.


3. Select the most relevant articles related to the specified topic (defined by the provided keywords).
   
   3.1. Select articles that contain any of the specified keywords in their title.
   
   3.2. Utilize TF-IDF (the default model), which can be extended to other models.


4. Select final articles based on criteria defined in [config.py](https://github.com/UtrechtUniversity/dataQuest/blob/main/config.json). 

There are different strategies for selecting the final articles:

- Percentage: Select a percentage of articles with the highest scores.

- Maximum Number: Specify the maximum number of articles to select based on their scores.

- Threshold: Set a threshold for the cosine similarity value between the embeddings of the keyword list and each article.

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

5. Generate output 

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

To run the pipeline:

```commandline
python3 dataQuest/filter_articles.py 

    --input-dir "path/to/converted/json/compressed/" 
    
    --output-dir "output/" 
    
    --input-type "delpher_kranten" 
    
    --glob "*.gz"
    
    --period-type "decade"
```
In our case:
- The input data consists of compressed JSON files with the .gz extension. 
- The input type is "delpher_kranten". 
- Selected articles are categorized by decade.

OR

```
sh scripts/filter_articles.sh
```
## About the Project
**Date**: February 2024

**Researcher(s)**:

Pim Huijnen (p.huijnen@uu.nl)


**Research Software Engineer(s)**:

- Parisa Zahedi (p.zahedi@uu.nl)
- Shiva Nadi (s.nadi@uu.nl)


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

