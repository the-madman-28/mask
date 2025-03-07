import math
import data_config as dcfg
import csv
from typing import Callable, List
from functools import partial

def mask_from_start(disclosure_percent:float, x:str) -> str:
    mask_len = int(len(x) * (1 - disclosure_percent))
    mask = 'x'*mask_len
    masked_x = mask + x[mask_len + 1:]
    # print(masked_x, disclosure_percent)
    return masked_x

def mask_from_end(disclosure_percent:float, x:str) -> str:
    mask_len = int(len(x) * (1 - disclosure_percent))
    mask = 'x'*mask_len
    masked_x = x[:mask_len] + mask
    # print(masked_x, disclosure_percent)
    return masked_x

def mask_from_center(disclosure_percent:float, x:str) -> str:
    text_len = len(x)
    visible_text_len = int(text_len * disclosure_percent / 2)
    mask_len = text_len - 2 * visible_text_len
    mask = 'x'*mask_len
    masked_x = x[:visible_text_len] + mask + x[visible_text_len + mask_len:]
    # print(masked_x, disclosure_percent)
    return masked_x

class Attribute:
    '''
    Attribute class, contains information about attribute
    '''

    def __init__(self, id : int = -1) -> None:
        self.id = id
        self.vulnerability_score = 0
        self.disclosure_proportion = 0.0
        self.type = ''
    
    def update(self, type: str, vulnerability_score : int, disclosure_proportion : float, masking_plan: Callable[[float, str], str]) -> None:
        '''Update Attribute object with 'vulnerability_score' and 'disclosure_proportion' '''
        self.type = type
        self.vulnerability_score = vulnerability_score
        self.disclosure_proportion = disclosure_proportion
        self.masking_plan = partial(masking_plan, self.disclosure_proportion)

class AttributeDB:
    '''
    Attribute database, contains Attribute class objects
    '''

    def __init__(self, attribute_file : str, uniform_disclosure = False, uniform_disclosure_percent = 0.0) -> None:
        self.attribute_list = [Attribute(i) for i in range(dcfg.ATTR_COUNT)]
        self.attribute_file = attribute_file
        self.uniform_disclosure = uniform_disclosure
        self.uniform_disclosure_percent = uniform_disclosure_percent
        self.__initialize()

    def __initialize(self) -> None:
        '''
        initialize the attribute object from 'attribute_file' csv
        '''
        with open(self.attribute_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            if self.uniform_disclosure:
                for row in csvreader:
                    self.attribute_list[int(row[0])].update(row[1],int(row[2]), self.uniform_disclosure_percent, self.get_masking_plan(row[4]))
            else:
                for row in csvreader:
                    self.attribute_list[int(row[0])].update(row[1], int(row[2]), float(row[3]), self.get_masking_plan(row[4]))
    
    def get_attribute_obj(self, attribut_id : int) -> Attribute:
        '''Get attribute object of id 'attribute_id' '''
        return self.attribute_list[attribut_id]
    
    def get_attr_obj_from_type(self, attr_type:str) -> Attribute:
        '''Return attribute object of attribute type (attr_type)'''
        for attr in self.attribute_list:
            if attr.type == attr_type:
                return attr
                
        return Attribute()
    
    def get_attribute_obj_list(self, attribute_id_list : List[int]) -> List[Attribute]:
        '''Get list of attribute object given list of attribute id'''
        attribute_obj_list = []
        for attribute_id in attribute_id_list:
            attribute_obj_list.append(self.attribute_list[attribute_id])
        
        return attribute_obj_list

    def get_attribute_disclosure(self, attribute_type: str) -> float:
        attr_index = -1
        for attr in self.attribute_list:
            if attr.type == attribute_type:
                attr_index = attr.id
                break
        
        return self.attribute_list[attr_index].disclosure_proportion
    
    def get_masking_plan(self, masking_plan:str) -> Callable[[float, str], str]:
        plan_dict = {'mask_from_start': mask_from_start,
                     'mask_from_center': mask_from_center,
                     'mask_from_end': mask_from_end}
        
        return plan_dict[masking_plan]

    def print_attributes(self) -> None:
        '''Print the attributes and its properties'''
        for attr in self.attribute_list:
            print(attr.type,' : ', attr.disclosure_proportion)
    
def get_sensitive_score( attribute_list: List[Attribute]) -> float:
    '''Get sensitive score of attribute list passed'''
    q_score = 0 # Quasi attribute sensitive score
    q_count = 0 # Quasi attribute count
    r_score = 0 # Remaining attribute sensitive score
    
    for attr in attribute_list:
        if attr.vulnerability_score in [2,3]:
            q_score += attr.vulnerability_score * attr.disclosure_proportion
            q_count += 1
        else:
            r_score += attr.vulnerability_score * attr.disclosure_proportion
    
    sensitive_score = r_score
    
    if q_count > 0:
        sensitive_score += ((math.e / 2) ** math.log(q_count)) * q_score

    return sensitive_score