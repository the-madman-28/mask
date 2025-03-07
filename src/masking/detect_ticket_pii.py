from presidio_analyzer import RecognizerResult, LocalRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts
from typing import List
import spacy
import config as cfg
import data_config as dcfg

class DetectTicketPII(LocalRecognizer):
    expected_confidence_level = 0.7 # expected confidence level for this recognizer

    ENTITIES = dcfg.ENTITIES
    
    MODEL_LANGUAGES = {
        "en": cfg.MODEL_PATH,
    }

    PRESIDIO_EQUIVALENCES = {
        'PERSON': 'name',
        'EMAIL_ADDRESS': 'mail',
        'US_BANK_NUMBER': 'bank_account_number',
        'US_DRIVER_LICENSE': 'ssn',
        'ORG': 'company',
        'MONEY': 'money'
    }

    model = spacy.load(cfg.MODEL_PATH)
    def load(self) -> None:
        pass

    def analyze(self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts) -> List[RecognizerResult]:
        doc = self.model(text)
        results = []

        for ent in doc.ents:
            result = RecognizerResult(
                entity_type=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
                score=self.expected_confidence_level
            ) 
            results.append(result)
            # print(doc.text[ent.start_char:ent.end_char],(ent.start_char, ent.end_char, ent.label_))
        
        return results

