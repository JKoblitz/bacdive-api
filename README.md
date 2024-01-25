# BacDive API

Using the BacDive API requires registration. Registration is free but the usage of BacDive data is only permitted when in compliance with the BacDive terms of use. See [About BacDive](https://bacdive.dsmz.de/about) for details.

Please register [here](https://api.bacdive.dsmz.de/login).

The Python package can be initialized using your login credentials:


```python
import bacdive

client = bacdive.BacdiveClient('name@mail.example', 'password')

# [optional] You may define the search type as one of the following: 
# 'exact' (default), 'contains', 'startswith', 'endswith'
client.setSearchType('exact')

# The search method fetches all BacDive-IDs matching your query
# and returns the number of IDs found
count = client.search(taxonomy='Bacillus subtilis subtilis')
print(count, 'strains found.')

# the retrieve method lets you iterate over all strains
# and returns the full entry as dict
# Entries can be further filtered using a list of keys (e.g. ['keywords'])
for strain in client.retrieve():
    print(strain)
```

## Example queries:

```python
# Search by BacDive-IDs (either semicolon separated or as list):
query = {"id": 24493}
query = {"id": "24493;12;132485"}
query = {"id": [24493, 12, 132485]}

# Search by culture collection number
query = {"culturecolno": "DSM 26640"}
# New in v1.0: Search by culture collection number with multiple numbers:
query = {"culturecolno": ["DSM 26640", "DSM 26646"]}
query = {"culturecolno": "DSM 26640;DSM 26646"} # semicolon may be used as separator

# Search by culture collection number with search type 'startswith':
client.setSearchType('startswith')
query = {"culturecolno": "DSM"}

# Search by taxonomy (either as full name or as list):
# With genus name, species epithet (optional), and subspecies (optional).
query = {"taxonomy": "Bacillus subtilis subsp. subtilis"}
query = {"taxonomy": ("Escherichia", "coli")}

# Search by 16S sequence accession numbers:
query = {"16s": "AF000162"}
# New in v1.0: Search by 16S sequence with multiple sequence accession numbers:
query = {"16s": ["AB681963", "JN566021", "AY027686"]}
# New in v1.0: Search by 16S sequence with search type 'startswith':
client.setSearchType('startswith')
query = {"16s": "AB"}

# Search by genome sequence accession numbers:
query = {"genome": "GCA_006094295"}
# New in v1.0: Search by genome sequence with multiple sequence accession numbers:
query = {"genome": ["GCA_003332855", "GCA_024623325", "GCA_017377855"]}
# New in v1.0: Search by genome sequence with search type 'startswith':
client.setSearchType('startswith')
query = {"genome": "DSM"}


# run query
client.search(**query)
```

## Filtering

Results from the `retrieve` Method of both clients can be further filtered. The result contains a list of matched keyword dicts:

```python
filter=['keywords', 'culture collection no.']
result = client.retrieve(filter)
print({k:v for x in result for k,v in x.items()})
```

The printed result will look like this:

```python
{'1161': [{'keywords': ['human pathogen', 'Bacteria']},
          {'culture collection no.': 'DSM 4393, pC194, SB202'}],
 '1162': [{'keywords': ['human pathogen', 'Bacteria']},
          {'culture collection no.': 'DSM 4514, ATCC 37015, BD170, NCIB 11624, '
                                     'pUB110'}],
 '1163': [{'keywords': ['human pathogen', 'Bacteria']},
          {'culture collection no.': 'DSM 4554, ATCC 37128, BGSC 1E18, pE194'}],
 '1164': [{'keywords': 'Bacteria'},
          {'culture collection no.': 'DSM 4750, 1E7, BGSC 1E7, pE194-cop6'}],
...
```

## Hints for more advanced queries
If you have more advanced queries that are currently not covered by the API, we recommend you to use the [Bac*Dive* Advanced Search](https://bacdive.dsmz.de/advsearch), which is very flexible and powerful. You can then download the resulting table as CSV (button at the top right), import the CSV into your Python script, and use the BacDive-IDs to download all relevant information via the API.


## New in v0.3

We added AI-based predictions to the Bac*Dive* database. Predicted traits are excluded by default. To include them, you have to call the method `includePredictions()`:

```python
client.includePredictions()
```

You can exclude predictions again by calling: 

```python
client.excludePredictions()
```

## New in v1.0

Thanks to [phenolophthaleinum](https://github.com/phenolophthaleinum) for improving the error handling and Joaquim Sardá for improving the BacDive-API and adding new search possibilities.

Examples for search type definitions and array requests are included in the examples above.