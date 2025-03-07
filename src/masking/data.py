import csv
from math import ceil
from random import choice, choices, randrange, shuffle

from numpy.random import exponential, randint

import config as cfg
import data_config as dcfg
from fake_ticket_data import FakeProfile
from utility import load_json, list_to_str

class GenerateData:
    '''Generate Data'''
    
    def __init__(self) -> None:
        pass

    def generate_text_ticket_csv(self, sensitive_portion=cfg.SENSITIVE_PORTION, ticket_count=cfg.TICKET_COUNT) -> None:
        '''Generate ticket csv having ticket text'''
 
        fields = ['ticket_id', 'user_id', 'customer', 'category', 'priority', 'description', 'attribute_list', 
                  'sensitive_flag']
        file_name = f'./src/masking/input/agent_{cfg.AGENT_COUNT}/ticket_count{cfg.TICKET_COUNT}_sensitive{cfg.SENSITIVE_PORTION}.csv'

        with open(file_name, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(fields)
            profile_count = ceil(ticket_count/dcfg.TICKET_PER_PROFILE) + 1
            customer_list = choices(range(cfg.CUSTOMER_COUNT), k=profile_count)
            category_list = choices(range(cfg.CAT_COUNT), 
                                    k=ticket_count)
            ticket_text_list = self.get_ticket_text_list(category_list,
                                                         sensitive_portion=sensitive_portion, 
                                                         ticket_count=ticket_count)
            list_index = 0
            priority_list = choices(range(cfg.PRIORITY_COUNT), cfg.PRIORITY_DIST, k=ticket_count)
            i_arr_time = exponential(1/cfg.ARR_RATE, ticket_count)
            i_arr_time = [round(x,3) for x in i_arr_time]
            for i in range(ticket_count):
                user_id, category, ticket_text, attribute_list, sensitive_flag = ticket_text_list[list_index]
                row = [i, user_id, customer_list[user_id], category, priority_list[i], ticket_text, 
                    list_to_str(attribute_list), sensitive_flag]
                csv_writer.writerow(row)
                list_index += 1
            csv_file.close()
    
    def get_ticket_text_list(self, category_list: list, sensitive_portion = cfg.SENSITIVE_PORTION, ticket_count=cfg.TICKET_COUNT) -> list:
        '''
        Returns the list containing templates in tuples of
        (user_id_list, category_id, ticket text, attribute list, sensitive_flag)
        '''

        ticket_template = load_json(dcfg.TICKET_TEMPLATE_FILE) # Read template file and store in dict
        # Generate sensitive flag according to required distribution
        sensitive_flag_list = choices([0,1], weights=[100-sensitive_portion, sensitive_portion], k=ticket_count)
        template_list = []

        for cat, sensitive_flag in zip(category_list, sensitive_flag_list):
            if sensitive_flag:
                template = choice(ticket_template['Sensitive'][cfg.CATEGORY_NAME[cat]])
            else:
                template = choice(ticket_template['Non sensitive'][cfg.CATEGORY_NAME[cat]])
            template_list.append(template)
        # ticket_per_profile = ceil(cfg.ticket_count/dcfg.profile_count)
        # profile_count = ceil(cfg.ticket_count/dcfg.ticket_per_profile) + 1
        profile_list = [FakeProfile() for _ in range(dcfg.PROFILE_COUNT)]
        ticket_per_profile_count_list = self.get_ticket_count_list(1,25, ticket_count)
        ticket_list = []
        attr_list = []
        user_id_list = []

        profile_index = 0
        temp_index = 0

        # Get fake ticket text from template, corresponding to profiles
        for template in template_list:
            text, attr_type = profile_list[profile_index].get_fake_ticket_text(template)
            ticket_list.append(text)
            attr_list.append(attr_type)
            user_id_list.append(profile_index)

            # Take care of profile index, increase it after having defined ticket count.
            temp_index += 1
            if temp_index == ticket_per_profile_count_list[profile_index]:
                temp_index = 0
                profile_index += 1

        ticket_tuple = list(zip(user_id_list, category_list, ticket_list, attr_list, sensitive_flag_list))
        shuffle(ticket_tuple)

        return ticket_tuple
    
    def get_ticket_count_list(self, c_min:int, c_max:int, ticket_count=cfg.TICKET_COUNT) -> list[int]:
        '''
        Get list of ticket count of users.
        param:
            c_min: Min ticket count for a profile.
            c_max: Max ticket count for a profile.
        [WARNING!] Does not give correct list for every parameters.
        '''
        count_array = randint(low=c_min, high=c_max, size=dcfg.PROFILE_COUNT)
        count_array[::-1].sort()

        top50_sum = count_array[:dcfg.PROFILE_COUNT//2].sum()
        total_sum = count_array.sum()
        diff = (total_sum - ticket_count) / top50_sum

        for i in range(dcfg.PROFILE_COUNT):
            if count_array.sum() < ticket_count:
                break
            count_array[i] = count_array[i] * ( 1 - diff)
        
        count_array[0] += (ticket_count - count_array.sum())
        shuffle(count_array) # type: ignore

        return list(count_array)

    def generate_ticket_arrival_pattern(self, ticket_count=cfg.TICKET_COUNT, arrival_rate=cfg.ARR_RATE) -> str:
        '''Save Ticket arrival pattern'''
        
        i_arr_time = exponential(1/arrival_rate, ticket_count)
        i_arr_time = [round(x,3) for x in i_arr_time]
        fields = ['ticket_id', 'inter_arr_time', 'arr_time']
        file_name = './src/masking/input/arrival_pattern/ticket_arrival_rate{}.csv'.format(arrival_rate)

        with open(file_name, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(fields)
            for i in range(ticket_count):
                row = [i, i_arr_time[i], round(sum(i_arr_time[:i+1]),3)]
                csv_writer.writerow(row)
            csv_file.close()
        return file_name

    def generate_attribute_csv(self):
        '''
        Generate attribute vector and save it in CSV by name 'file_name'
        Attribute Vector row:
            <attribute_id, vulnerability_score, disclosure_proportion>
        '''
        file_name = './src/masking/input/attribute_vmax{}_vmin{}_dmax{}_dmin{}.csv'.format(dcfg.ATTR_VUL_SCORE_MAX,
                                                                             dcfg.ATTR_VUL_SCORE_MIN,
                                                                             dcfg.DISCLOSURE_PROPORTION_MAX,
                                                                             dcfg.DISCLOSURE_PROPORTION_MIN)
        fields = ['attribute_id', 'vulnerability_score', 'disclosure_proportion']
        with open(file_name, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(fields)

            for attribute_id in range(dcfg.ATTR_COUNT):
                vulnerability_score = randrange(dcfg.ATTR_VUL_SCORE_MIN, dcfg.ATTR_VUL_SCORE_MAX)
                disclosure_proportion = 100 if not vulnerability_score else randrange(dcfg.DISCLOSURE_PROPORTION_MIN, dcfg.DISCLOSURE_PROPORTION_MAX, step=10)
                csv_writer.writerow([attribute_id, vulnerability_score, disclosure_proportion])
            csv_file.close()

if __name__ == '__main__':
    for ac in [22, 24, 26, 28]:
        cfg.AGENT_COUNT = ac
        gd = GenerateData()
        for tc in [1000,1500,2000]:
            cfg.TICKET_COUNT = tc
            for ss in [60]:
                gd.generate_text_ticket_csv(ticket_count=tc, sensitive_portion=ss)
