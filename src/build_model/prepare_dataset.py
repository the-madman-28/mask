import warnings
from pathlib import Path

import spacy
from spacy.tokens import DocBin

from fake_ticket_data import FakeTicketDB

def convert(lang: str, train_data, output_path: Path) -> None:
    '''
    Convert annotated data to .spacy format

    :param lang: Language
    :param train_data: Train Data
    :param output_path: Path to save output
    '''
    nlp = spacy.blank(lang)         # Create blank spacy model
    db = DocBin()                   # docbin object to serialize the texts
    for text, annot in train_data:  # TRAIN_DATA is in spacy v3 format i.e (text, [(start, end, label)])
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annot:
            span = doc.char_span(start, end, label=label)
            if span is None:
                msg = f"Skipping entity [{start}, {end}, {label}] in the following text because the character span '{doc.text[start:end]}' does not align with token boundaries:\n\n{repr(text)}\n"
                warnings.warn(msg)
            else:
                ents.append(span)
        doc.ents = ents
        db.add(doc)
    db.to_disk(output_path)  # Save the dataset

def save_spacy_friendly_ticket(output_path: Path, profile_count=200) -> None:
    '''
    Create ticket and save in spacy friendly manner

    :param output_path: Path to save generated dataset
    :param profile_count: Profiles of user to consider
    '''
    fake_ticket = FakeTicketDB(profile_count) # Generate fake tickets having 300 individual profiles
    tickets = fake_ticket.get_fake_ticket_spacy2() # Get fake tickets based on templates present in 'ticket_template.txt

    convert('en', tickets, output_path)

if __name__ == "__main__":
    save_spacy_friendly_ticket(Path('./train3.spacy'),5)
    # save_spacy_friendly_ticket(Path('./eval2.spacy'))