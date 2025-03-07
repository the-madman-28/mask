from pathlib import Path

CATEGORY_ENTITIES = {
    'Software': ['software', 'python_package', 'url'],
    'Finance': ['bank_account_number', 'credit_card_number', 'money', 'ssn'],
    'Travel': ['city', 'address', 'zip_code'],
    'Leave': ['date', 'name', 'phone_number'],
    'HR': ['job', 'name', 'mail'],
    'Medical': ['medical', 'name', 'phone_number'],
    'Access': ['username', 'password', 'url'],
    'Purchase': ['product_name', 'money', 'credit_card_number']
}

# Ticket attribute parameters
ENTITIES = ['address', 'bank_account_number', 'cc_provider', 'city', 'company', 'credit_card_number',
            'date', 'job', 'mail', 'money', 'name', 'phone_number', 'product_name', 'python_package',
            'residence', 'software', 'ssn', 'url', 'username', 'zip_code']
            
ATTR_COUNT = len(ENTITIES)
ATTR_VUL_SCORE_MIN = 0
ATTR_VUL_SCORE_MAX = 10
DISCLOSURE_PROPORTION_MIN = 40
DISCLOSURE_PROPORTION_MAX = 100

# Synthetic data
PROFILE_COUNT = 200
TICKET_PER_PROFILE = 5

BASE_DIR = Path(__file__).resolve().parent

TICKET_TEMPLATE_FILE = BASE_DIR /'input/ticket_template.json'

PRODUCT_NAME = ['Dishwasher', 'Washing Machine', 'Dryer', 'Microwave', 'Oven', 'Toaster', 'Waffle Iron',
                'Refrigerator', 'Freezer', 'Vacuum Cleaner', 'Air Conditioner', 'Air Purifier', 'Blender',
                'Ceiling Fan', 'Domestic Robot', 'Heater', 'Garbage Disposal Unit', 'Hair Dryer', 'Humidifier',
                'Dehumidifier', 'Sewing Machine', 'Water Purifier']

COLOR_LIST = ["#FF0000", "#c2c2c2", '#c719fa', '#fdee00', '#dab165', '#f4c2c2', '#9f8170', '#4fe1d4',
                '#66cd00', '#D5F9DE', '#7fffd4', '#b5a642', '#ff7f24', '#f4c2f4', '#9fc270', '#7f00d4']

SOFTWARE_LIST = ['Microsoft Office suite', 'Acrobat Reader', 'Acrobat Reader', 'Photoshop', 'ServiceNow',
                 'Dropbox', 'DocSend', 'Guidewire', 'Cornerstone', 'Secureworks', 'Procore', 'Asana', 'iCIMS',
                 'Autodesk', 'Intuit', 'Wolfrom', 'Salesforce', 'Qualtrics', 'BlackLine', 'Webex', 'Jabber',
                 'Gainsight', 'Jira', 'VMware', 'Python', 'Ananconda', 'VSCode', 'Outlook']

PYTHON_PACKAGE_LIST = ['jupyter', 'scikit', 'pandas', 'numpy', 'tkinter', 'qt5', 'Flask', 'conda', 'Django', 
                       'spacy']

MASKING_PLAN = {'name': 'mask_from_start',
                'company': 'mask_from_start',
                'job': 'mask_from_start',
                'ssn': 'mask_from_start',
                'money': 'mask_from_start',
                'mail': 'mask_from_start',
                'zip_code': 'mask_from_start',
                'address': 'mask_from_start',
                'credit_card_number': 'mask_from_start',
                'bank_account_number': 'mask_from_start',
                'cc_provider': 'mask_from_start',
                'username': 'mask_from_start',
                'date': 'mask_from_center',
                'phone_number': 'mask_from_start',
                'product_name': 'mask_from_center',
                'url': 'mask_from_center',
                'software': 'mask_from_center',
                'city': 'mask_from_start',
                'python_package': 'mask_from_start',
                'residence': 'mask_from_center'
                }