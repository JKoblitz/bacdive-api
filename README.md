# BacDive API

Using the BacDive API requires registration. Registration is free but the usage of BacDive data is only permitted when in compliance with the BacDive terms of use. See [About BacDive](https://bacdive.dsmz.de/about) for details.

Please register [here](https://api.bacdive.dsmz.de/login).

The Python package can be initialized using your login credentials:


```python
import bacdive

client = bacdive.BacdiveClient('name@mail.example', 'password')

# the search method fetches all BacDive-IDs matching your query
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

# Search by taxonomy (either as full name or as list):
# With genus name, species epithet (optional), and subspecies (optional).
query = {"taxonomy": "Bacillus subtilis subsp. subtilis"}
query = {"taxonomy": ("Escherichia", "coli")}

# Search by sequence accession numbers:
query = {"16s": "AF000162"} # 16S sequence
query = {"genome": "GCA_006094295"} # genome sequence

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

## New in v0.3

We added AI-based predictions to the Bac*Dive* database. Predicted traits are excluded by default. To include them, you have to call the method `includePredictions()`:

```python
client.includePredictions()
```

You can exclude predictions again by calling: 

```python
client.excludePredictions()
```

