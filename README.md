
# Anonymization Module

This repository is a fork of PESO to seperate out the Anonymization module.

The aim is to build an API for anonymization of PIIs and sensitive data present in unstructured text document. Current focus is to separate the anonymization module from PESO whcih anonymizes the ticket.

## GOALS & TODO

- [x] Remove unnecessary files and modules from PESO.
- [ ] Remove other fields from ticket, keep only text.
- [x] Restructure streamlit home.
- [x] Convert Jupyter Notebook to python script for model training.

### Code Changes

- [x] Category distribution in data.py

### Ideas:
- [ ] Identify and keep necesarry data intact or mask upto certain level. Kind of rule-based. It kind of sets the threshold of masking that can be done on an attribute to keep its utility. [NITIN]
- [ ] Pseudo-anaonymize or hash the sensitive data while in transit. The agent can use the hash for system queries. The idea is, system knows the data but agent doesn't. [NITIN]
