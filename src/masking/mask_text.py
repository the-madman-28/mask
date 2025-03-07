## Autor: Rohit Gupta

from typing import List, Tuple
import spacy
import config as cfg
import data_config as dcfg
from presidio_analyzer import AnalyzerEngine, LocalRecognizer, RecognizerRegistry, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities.engine import OperatorConfig
from attributedb import AttributeDB
from presidio_analyzer.nlp_engine import NlpArtifacts

class DetectPII(LocalRecognizer):
    def __init__(self, model_path: str, entities: List[str], name: str = '', confidence_level: float = 0.7):
        """
        Initialize the PII recognizer with the given model path and confidence level.
        """
        if name == '':
            self.name = self.__class__.__name__  # assign class name as name
        else:
            self.name = name
        self._id = f"{self.name}_{id(self)}"
        self.expected_confidence_level = confidence_level  # Set confidence level
        self.supported_entities = entities  # List of entities to detect
        self.is_loaded = False
        self.model = self._load_model(model_path)  # Load spaCy model
        self.is_loaded = True
        self.presidio_equivalences = self._load_presidio_equivalences()
        self.supported_language = 'en'
        self.context = []

    def _load_model(self, model_path: str):
        """
        Load and return the spaCy model for PII detection.
        """
        return spacy.load(model_path)

    def _load_presidio_equivalences(self):
        """
        Load entity equivalences to map spaCy entities to Presidio PII entities.
        """
        return {
            'PERSON': 'name',
            'EMAIL_ADDRESS': 'mail',
            'US_BANK_NUMBER': 'bank_account_number',
            'US_DRIVER_LICENSE': 'ssn',
            'ORG': 'company',
            'MONEY': 'money'
        }

    def load(self) -> None:
        """
        Load any additional resources, if needed (placeholder).
        """
        pass

    def analyze(self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts) -> List[RecognizerResult]:
        """
        Analyze the text and return a list of recognized PII entities.
        """
        doc = self.model(text)
        return self._extract_entities(doc)

    def _extract_entities(self, doc) -> List[RecognizerResult]:
        """
        Extract entities from the spaCy document and return as RecognizerResults.
        """
        results = []
        for ent in doc.ents:
            if ent.label_ in self.supported_entities:  # Only consider specified entities
                result = self._create_recognizer_result(ent)
                results.append(result)
        return results

    def _create_recognizer_result(self, ent) -> RecognizerResult:
        """
        Create a RecognizerResult object from the extracted entity.
        """
        return RecognizerResult(
            entity_type=ent.label_,  # The entity type from spaCy
            start=ent.start_char,  # Start character of entity
            end=ent.end_char,  # End character of entity
            score=self.expected_confidence_level  # Confidence level
        )

def detect_pii(text_input: str, cat: str) -> Tuple[List[RecognizerResult], dict]:
    '''Detect PII and return recognized PIIs'''
    # Create configuration containing engine name and models
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": cfg.MODEL_PATH}],
    }

    # Create NLP engine based on configuration
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()
    detect_pii = DetectPII(cfg.MODEL_PATH, entities=dcfg.ENTITIES)

    registry = RecognizerRegistry()
    registry.add_recognizer(detect_pii)

    # Pass the created NLP engine and supported_languages to the AnalyzerEngine
    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine, 
        supported_languages=["en"],
        registry=registry
    )

    analyzer.registry.add_recognizer(detect_pii)
    results = analyzer.analyze(text=text_input, language='en')

    results_dict = {}
    for result in results:
        key = text_input[result.start:result.end]
        results_dict[key] = result.entity_type

    print(f"detect PII results - {results} and results dict - {results_dict}")
    return results, results_dict

def anonymize_pii(text_input: str, result: List[RecognizerResult], attributedb: AttributeDB) -> str:
    '''
    Mask the text PIIs according to disclosure proportion
    '''    
    operator_options = {} 
    # this is storing the elements to be changed and DP will be put here.
    for entity in dcfg.ENTITIES:
        operator_options[entity] = OperatorConfig("custom", {"lambda": attributedb.get_attr_obj_from_type(entity).masking_plan})

    anonymizer = AnonymizerEngine()
    anonymized_text = anonymizer.anonymize(text=text_input,
                                        analyzer_results=result, # type: ignore
                                        operators=operator_options).text
    return anonymized_text

def anonymize_pii1(text_input: str, result: List[RecognizerResult], attributedb: AttributeDB, cat: str) -> str:
    """
    Mask the text PIIs according to disclosure proportion:
    - If the entity is present in the category (CATEGORY_ENTITIES), apply its defined masking method.
    - If the entity is not in the category, completely mask it.
    """
    # Get the list of allowed entities for the given category
    category_entities = dcfg.CATEGORY_ENTITIES.get(cat, [])
    operator_options = {}

    for entity in dcfg.ENTITIES:
        if entity in category_entities:
            # Apply category-specific masking plan
            operator_options[entity] = OperatorConfig(
                "custom", {"lambda": attributedb.get_attr_obj_from_type(entity).masking_plan}
            )
        else:
            # Completely mask entities not in the category
            operator_options[entity] = OperatorConfig(
                "replace", {"new_value": "[MASKED]"}
            )

    anonymizer = AnonymizerEngine()
    anonymized_text = anonymizer.anonymize(
        text=text_input,
        analyzer_results=result,  # type: ignore
        operators=operator_options
    ).text

    return anonymized_text

def mask_text(text_input: str, attributedb: AttributeDB, cat: str) -> Tuple[str, dict]:

    print(f"This is category of the ticket {cat}")
    recognizer_result, detected_pii_dict = detect_pii(text_input, cat)
    print(f"Deteceted PII - {detected_pii_dict}")
    masked_text = anonymize_pii(text_input, recognizer_result, attributedb)

    return masked_text, detected_pii_dict

def mask_text1(text_input: str, attributedb: AttributeDB, cat: str) -> Tuple[str, dict]:
    print(f"This is category of the ticket {cat}")
    recognizer_result, detected_pii_dict = detect_pii(text_input, cat)
    print(f"Deteceted PII - {detected_pii_dict}")
    masked_text1 = anonymize_pii1(text_input, recognizer_result, attributedb, cat)

    return masked_text1, detected_pii_dict