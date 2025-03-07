from pathlib import Path

# Ticket
TICKET_COUNT = 1000

# Agent
AGENT_COUNT = 20

# Arrival time
ARR_RATE = 0.35        # lambda Not defined

PRIVACY_FACTOR = 0.4

# Data
SENSITIVE_PORTION = 60

# Category
CATEGORY_NAME = ['Software', 'Finance', 'Travel', 'Leave', 'HR', 'Medical', 'Access', 'Purchase']
CAT_COUNT = len(CATEGORY_NAME)

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = str(BASE_DIR) + '/ner/models/spacy_model6/model-best'

# Customer
CUSTOMER_COUNT = 5

# Priority
PRIORITY_COUNT = 4  # 0 is high, 3 is low
PRIORITY_DIST = [0.05,0.1,0.35,0.5]

EPOCH_TIME = 3.0