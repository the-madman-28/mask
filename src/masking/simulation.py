import config as cfg
from ticketdb import TicketDB
from attributedb import AttributeDB

class Simulate:
    '''Simulate '''

    def __init__(self, file_dict: dict, privacy_factor=cfg.PRIVACY_FACTOR, uniform_disclosure = False, 
                 uniform_disclosure_percent = 0.0, verbose=False) -> None:
        self.attributedb = AttributeDB(file_dict['attribute_file'], uniform_disclosure, uniform_disclosure_percent)
        self.ticketdb = TicketDB(file_dict['ticket_file'], file_dict['ticket_arrival_file'], self.attributedb, verbose)
        self.privacy_factor = privacy_factor
        self.current_time = 0
        self.verbose = verbose

if __name__ == "__main__":
    file_dict = {
        'ticket_file': f'./src/masking/input/agent_{cfg.AGENT_COUNT}/ticket_count{cfg.TICKET_COUNT}_sensitive{cfg.SENSITIVE_PORTION}.csv',
        'ticket_arrival_file': f'./src/masking/input/arrival_pattern/ticket_arrival_rate{cfg.ARR_RATE}.csv',
        'attribute_file': f'./src/masking/input/attribute/attribute_privacyfactor_{cfg.PRIVACY_FACTOR}.csv'
    }
    s = Simulate(file_dict, verbose=True)
    