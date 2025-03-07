from math import ceil
from random import choice, shuffle
from typing import List, Tuple
from faker import Faker
from tqdm import tqdm
import re
import masking.data_config as dcfg
from masking.utility import load_json

class FakeProfile():
    def __init__(self, id = -1) -> None:
        '''
        Fake profile dict attributes:
        {
            'address',
            'birthdate',
            'blood_group',
            'company',
            'current_location' (lattitude, longitude),
            'job',
            'mail',
            'name',
            'residence',
            'sex',
            'ssn',
            'username',
            'website (list)'
        }
        '''
        self.profile = Faker(['en_US']).profile()
        self.id = id

    def get_fake_ticket_spacy(self, fake_ticket_str: str, template_id = 0):
        '''Get Spacy v3 friendly fake ticket based on ticket template given'''
        pii_type = self.get_pii_type(fake_ticket_str)
        pii_list = self.get_pii_list(pii_type)

        ticket_str = re.sub("{{\w+}}", "{}", fake_ticket_str) # type: ignore
        start_index = self.get_start_index(ticket_str)
        fake_ticket = ticket_str.format(*pii_list)

        len_list = [len(x) for x in pii_list]
        spacy_tuple_list = []

        for i in range(len(start_index)):
            start = sum(start_index[:i+1]) + sum(len_list[:i])
            end = start + len_list[i]
            spacy_tuple_list.append((start, end, pii_type[i]))

        return (fake_ticket, spacy_tuple_list)

    def get_fake_ticket_text(self, fake_ticket_str: str) -> Tuple[str, list]:
        '''return fake ticket description of ticket based on template 'fake_ticket_str' '''
        pii_type = self.get_pii_type(fake_ticket_str)
        pii_list = self.get_pii_list(pii_type)

        ticket_str = re.sub("{{\w+}}", "{}", fake_ticket_str) # type: ignore
        fake_ticket_text = ticket_str.format(*pii_list)

        return (fake_ticket_text, pii_type)

    def get_pii_type(self, fake_ticket_str: str) -> list[str]:
        '''Get PII type'''
        temp_pii_list = re.findall(
            "{{\w+}}", fake_ticket_str)  # type: ignore # Gives pii in format {{pii}}
        pii_list = [x.translate({ord(i): None for i in '{}'})
                    for x in temp_pii_list]  # remove '{{' and '}}' from pii

        return pii_list

    def get_pii_list(self, pii_type: list[str]) -> list[str]:
        '''Get PII based on profile for given pii types'''
        pii_list = []
        fake = Faker()

        for pii_t in pii_type:
            if pii_t in self.profile.keys():
                pii_list.append(self.profile[pii_t])
            elif pii_t == 'money':
                pii_list.append(fake.pricetag())
            elif pii_t == 'credit_card_number':
                pii_list.append(fake.credit_card_number())
            elif pii_t == 'cc_provider':
                pii_list.append(fake.credit_card_provider())
            elif pii_t == 'bank_account_number':
                pii_list.append(fake.bban())
            elif pii_t == 'zip_code':
                pii_list.append(self.profile['residence'][-5:]) # type: ignore
            elif pii_t == 'date':
                pii_list.append(fake.date())
            elif pii_t == 'phone_number':
                pii_list.append(fake.msisdn())
            elif pii_t == 'product_name':
                pii_list.append(choice(dcfg.PRODUCT_NAME))
            elif pii_t == 'url':
                pii_list.append(fake.url())
            elif pii_t == 'software':
                pii_list.append(choice(dcfg.SOFTWARE_LIST))
            elif pii_t == 'city':
                pii_list.append(fake.city())
            elif pii_t == 'python_package':
                pii_list.append(choice(dcfg.PYTHON_PACKAGE_LIST))

        return pii_list

    def get_start_index(self, ticket_string: str) -> list[int]:
        count = 0
        start_index_list = []

        for i in range(len(ticket_string)):
            if ticket_string[i] == '{':
                start_index_list.append(count)
            elif ticket_string[i] == '}':
                count = 0
            else:
                count += 1

        return start_index_list

class FakeTicketDB():
    def __init__(self, profile_count:int) -> None:
        self.profiles = [FakeProfile() for _ in range(profile_count)]
    
    def get_fake_ticket_spacy(self) -> List[dict]:
        '''Get fake tickets based on templates present in 'ticket_template.json'''
        
        ticket_list = []
        ticket_template = get_template()
        template_id = 0

        for fake_profile in self.profiles:
            for template in ticket_template:
                ticket_list.append(fake_profile.get_fake_ticket_spacy(template, template_id))
                template_id += 1
        
        return ticket_list
    

    def get_fake_ticket_spacy2(self) -> List[dict]:
        """Get fake tickets based on templates present in 'ticket_template.json'"""
        
        ticket_list = []
        ticket_template = get_template()
        template_id = 0
        
        # Create a progress bar for the outer loop (profiles)
        for fake_profile in tqdm(self.profiles, desc="Profiles Progress"):
            # Create a progress bar for the inner loop (templates)
            for template in tqdm(ticket_template, desc="Template Progress", leave=False):
                ticket_list.append(fake_profile.get_fake_ticket_spacy(template, template_id))
                template_id += 1
        
        return ticket_list

    
def get_fake_ticket_text(ticket_count:int) -> List[str]:
    '''
    Get ticket description text based on templates present in 'ticket_template.txt'
    It creates fake profile on the go.
    '''
    
    ticket_list = []
    ticket_template = get_template()
    
    profile_count = ceil(ticket_count/len(ticket_template))

    for _ in range(profile_count):
        fake_profile = FakeProfile()
        for template in ticket_template:
            text, _ = fake_profile.get_fake_ticket_text(template)
            ticket_list.append(text)
    
    shuffle(ticket_list)
    
    return ticket_list

def get_template() -> List[str]:
    '''Get list of templates read from template file'''
    
    template_dict = load_json(dcfg.TICKET_TEMPLATE_FILE)
    keys_1 = list(template_dict.keys())
    keys_2 = list(template_dict[keys_1[0]].keys())
    template_list = []
    for key1 in keys_1:
        for key2 in keys_2:
            template_list.extend(template_dict[key1][key2])

    return template_list

if __name__ == '__main__':
    print('Nothing to do!!!')