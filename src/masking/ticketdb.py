import csv
from typing import List
from tabulate import tabulate
from attributedb import Attribute, AttributeDB, get_sensitive_score

import config as cfg
import data_config as dcfg
from error import TicketError
from ticketstate import TicketState
class Ticket:
    '''
    Ticket class
    <ticket_id,customer,category,priority,inter_arr_time,arr_time,description,attribute_list,sensitive_flag>
    '''

    def __init__(self, id = -1, user_id = -1, customer: int = -1, category: int = -1,
                priority: int = -1, inter_arr_time: float = 0.0, arr_time: float = 0.0, 
                ticket_text = '', attribute_list: List[Attribute] = [], sensitive_flag = 0) -> None:
        self.id = id
        self.user_id = user_id
        self.customer = customer
        self.category = category
        self.priority = priority
        self.inter_arr_time = inter_arr_time
        self.arr_time = arr_time
        self.sensitive_flag = sensitive_flag
        self.text = ticket_text
        self.attribute_list = attribute_list
        self.state = TicketState.DORMANT

    def update_arrival_time(self, inter_arrival_time: float, arrival_time:float) -> None:
        '''Update ticket's arrival times'''
        self.inter_arr_time = inter_arrival_time
        self.arr_time = arrival_time

    def get_sensitivity_score(self) -> float:
        '''Get Sensitive score of ticket'''
        return get_sensitive_score(self.attribute_list)

    def get_customer(self) -> int:
        '''get customer'''
        return self.customer

    def get_category(self) -> int:
        '''get ticket category'''
        return self.category

    def get_inter_arr_time(self) -> float:
        '''Get ticket inter arrival time'''
        return self.inter_arr_time

    def get_arr_time(self) -> float:
        '''Get ticket arrival time'''
        return self.arr_time

    def get_priority(self) -> int:
        '''Get priority of a ticket'''
        return self.priority

class TicketDB:
    '''Ticket database class'''

    def __init__(self, ticket_file: str, ticket_arrival_file:str, attributedb: AttributeDB, verbose=False) -> None:
        self.ticket_file = ticket_file
        self.ticket_arrival_file = ticket_arrival_file
        self.ticket_list: List[Ticket] = []
        self.attributedb = attributedb
        self.list_index = 0
        self.curr_time = 0
        self.verbose = verbose
        self.__initialize()
        self.__initialize_arrival_time()

    def __initialize(self):
        '''Initialize Ticket objects'''

        with open(self.ticket_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for row in csvreader:
                attribute_str_list = row[6].split()
                attribute_id_list = [dcfg.ENTITIES.index(attr) for attr in attribute_str_list]
                attribute_obj_list = self.attributedb.get_attribute_obj_list(attribute_id_list)
                self.ticket_list.append(
                    Ticket(id=int(row[0]), user_id=int(row[1]), customer=int(row[2]), category=int(row[3]), priority=int(row[4]), ticket_text=row[5], attribute_list=attribute_obj_list, 
                           sensitive_flag=int(row[7]))
                           )
    
    def __initialize_arrival_time(self) -> None:
        '''initialize arrival time of tickets'''
        with open(self.ticket_arrival_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for row in csvreader:
                if int(row[0]) > cfg.TICKET_COUNT - 1:
                    break
                ticket = self.ticket_list[int(row[0])]
                ticket.update_arrival_time(inter_arrival_time=float(row[1]), 
                                                                  arrival_time=float(row[2]))

    def get_ticket_obj(self, ticket_id: int) -> Ticket:
        '''Get ticket Object'''
        return self.ticket_list[ticket_id]

    def get_category(self, id: int) -> int:
        '''Get current ticket category'''
        return self.ticket_list[id].get_category()

    def get_inter_arr_time(self, id: int) -> float:
        '''Get arrival time of current ticket'''
        return self.ticket_list[id].get_inter_arr_time()

    def next_ticket(self) -> Ticket:
        '''Get next ticket'''
        if self.list_index > cfg.TICKET_COUNT-1:
            raise TicketError('Ticket list index error at next_ticket with index :{}'.format(self.list_index))
        try:
            self.ticket_list[self.list_index].state = TicketState.NEW
            self.curr_time += self.ticket_list[self.list_index].get_inter_arr_time()

            new_ticket = self.ticket_list[self.list_index]
        except IndexError:
            print('List index: ', self.list_index)
            raise
        self.list_index += 1

        return new_ticket
        
    def next_ticket_set(self, epoch_end_time: float) -> list:
        '''
        Get next set of arrived ticket within epoch time
        returns:
            Ticket object list
        '''
        new_tickets = []
        new_tickets_id = []
        arr_time = []

        while(self.ticket_list[self.list_index].arr_time < epoch_end_time):
            ticket = self.ticket_list[self.list_index]
            new_tickets.append(ticket)
            new_tickets_id.append(ticket.id)
            arr_time.append(ticket.arr_time)
            ticket.state = TicketState.NEW
            self.curr_time += ticket.get_inter_arr_time()
            self.list_index += 1
        if self.verbose:
            print('\nEpoch end time: ', epoch_end_time)
            print(tabulate(zip(new_tickets_id,arr_time), headers=['Ticket ID', 'Arrival time'], floatfmt='.4f'))

        return new_tickets


if __name__ == "__main__":
    ticketdb = TicketDB('./src/masking/input/ticket.csv', True) # type: ignore
    curr_time = 0
    for i in range(5):
        curr_time += cfg.EPOCH_TIME
        ticketdb.next_ticket_set(curr_time)