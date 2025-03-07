import csv
import os
from pathlib import Path
from typing import List
import streamlit as st
import re
from simulation import Simulate
import config as cfg
import data_config as dcfg
from ticketdb import Ticket
from utility import get_duplicate
from mask_text import mask_text, mask_text1

from privacy_factor import disclosure_proportion
class PESODemo:
    def __init__(self) -> None:
        st.set_page_config(page_title="PESO",
                           page_icon="🔐",
                           layout='wide',
                           menu_items={
                               'About': 'This is Masking App, part of PESO, built by Rohit Gupta'
                           })
        st.image(str(cfg.BASE_DIR)+ '\\ui\\masking_header.png', width=800)

        self.home_tab, self.config_tab, self.readme_tab = st.tabs(['🏠Home',
                                                                   '⚙Privacy Config Manager',
                                                                   '📖Readme'])
        if 'ticket_count' not in st.session_state:
            st.session_state.ticket_count = 0
        if 'ticket_column' not in st.session_state:
            st.session_state.ticket_column = [
                'Ticket ID', 'Category', 'Subcategory', 'Arrival Time', 'Alloted Agent ID', 'Sensitive Score', 'Ticket text']
        if 'ticket_arrival_csv' not in st.session_state:
            st.session_state.ticket_arrival_csv = str(cfg.BASE_DIR) + f'\\input\\arrival_pattern\\ticket_arrival_rate{cfg.ARR_RATE}.csv'
        if 'arrival_rate' not in st.session_state:
            st.session_state.arrival_rate = cfg.ARR_RATE
        if 'ticket_csv' not in st.session_state:
            st.session_state.ticket_csv = str(cfg.BASE_DIR) + f'\\input\\agent_{cfg.AGENT_COUNT}\\ticket_count{cfg.TICKET_COUNT}_sensitive{cfg.SENSITIVE_PORTION}.csv'
        if 'attribute_csv' not in st.session_state:
            st.session_state.attribute_csv = str(cfg.BASE_DIR) + '\\input\\attribute2.csv'
        if 'file_dict' not in st.session_state:
            st.session_state.file_dict = {
                                        'ticket_file': st.session_state.ticket_csv,
                                        'ticket_arrival_file': st.session_state.ticket_arrival_csv,
                                        'attribute_file': st.session_state.attribute_csv
                                    }
        if 'simulate' not in st.session_state:
            st.session_state.simulate = Simulate(st.session_state.file_dict)
        if 'new_ticket' not in st.session_state:
            st.session_state.new_ticket = Ticket()
        if 'cat_stat' not in st.session_state:
            st.session_state.cat_stat = None
    
    def window(self):
        '''Create a window, layout and tabs'''

        tabs_font_css = """
        <style>
        button[data-baseweb="tab"] {
        font-size: 20px;
        }
        </style>
        """

        st.write(tabs_font_css, unsafe_allow_html=True)

        with self.home_tab:
            self.simulation_dashboard()

        # Configuration Manager
        with self.config_tab:
            self.config_manager()
        
        with self.readme_tab:
            readme_md = read_markdown_file(str(cfg.BASE_DIR) + '/info/streamlit_app_readme.md')
            self.readme_tab.markdown(readme_md)

    def config_manager(self) -> None:
        # self.config_tab.markdown('## Privacy Config Manager')
        vul_5_attr = ['ssn','bank_account_number','address','residence','credit_card_number']
        vul_4_attr = ['phone_number','mail', 'username', 'url']
        vul_3_attr = ['zip_code', 'city', 'company', 'job', 'name', 'cc_provider']
        vul_2_attr = ['product_name', 'python_package', 'software']
        vul_1_attr = ['money', 'date']

        attr_input_label = 'Enter attributes seperated by comma(,) without spaces.'
        attr_input = self.config_tab.text_area(attr_input_label,placeholder=str(dcfg.ENTITIES))
        uploaded_attribut_file = self.config_tab.file_uploader('Upload attribute file', type='txt')
        
        if uploaded_attribut_file:
            attr_list = self.get_attribute_from_uploaded_file(uploaded_attribut_file)
        elif attr_input:
            attr_list = re.sub('[^A-Za-z0-9_,]+', '', attr_input).split(',')
        else:
            attr_list = dcfg.ENTITIES

        self.config_form = self.config_tab.form(key='vulnerability_ratings_form')
        vul_5 = self.config_form.multiselect('Vulnerability: Very High(5)', attr_list, default=vul_5_attr)
        vul_4 = self.config_form.multiselect('Vulnerability: High(4)', attr_list, default=vul_4_attr)
        vul_3 = self.config_form.multiselect('Vulnerability: Medium(3)', attr_list, default=vul_3_attr)
        vul_2 = self.config_form.multiselect('Vulnerability: Low(2)', attr_list, default=vul_2_attr)
        vul_1 = self.config_form.multiselect('Vulnerability: Very Low(1)', attr_list, default=vul_1_attr)
        p_factor = self.config_form.number_input('Privacy Factor', min_value=0.1, max_value=1.0, value=0.40, step=0.01)

        config_submit_button = self.config_form.form_submit_button(label='save')

        if config_submit_button:
            selected_attr = vul_1+vul_2+vul_3+vul_4+vul_5
            if len(attr_list) != len(selected_attr):
                missing_attr = set(attr_list)^set(selected_attr)
                duplicate_attr = get_duplicate(selected_attr)
                self.config_tab.info('There is error in attribute list input. Attributes: Missing {}, Duplicate {}'.format(missing_attr,duplicate_attr), icon='❌')
                return

            dp_dict = disclosure_proportion(vul_1, vul_2, vul_3, vul_4, vul_5, p_factor)

            if dp_dict == 0:
                self.config_tab.write("Error in parameters setting")
            else:
                self.config_tab.write(dp_dict)
                self.save_attribute_csv(p_factor, dp_dict, vul_1, vul_2, vul_3, vul_4, vul_5)

    def simulation_dashboard(self) -> None:
        next_btn_col, spacer,  reset_btn_col = self.home_tab.columns([1, 3, 0.5])
        next_btn_col.button('Next Ticket', on_click=self.next_ticket)
        spacer.write('')
        reset_btn_col.button('Reset', on_click=self.reset)

        fields = ['Ticket ID', "Content", 'Category']
        column_ratio = [1,7,1]
        cols = self.home_tab.columns(column_ratio)

        # header
        for col, field in zip(cols, fields):
            col.write("**"+field+"**")
            
        inner_cols = self.home_tab.columns(column_ratio)
        cat = cfg.CATEGORY_NAME[st.session_state.new_ticket.category]

        inner_cols[0].write('TKT00{}'.format(st.session_state.new_ticket.id))

        # Change made here: Use a switch for extra privacy
        extra_privacy = inner_cols[1].checkbox("Enable Extra Privacy", value=False)  # Change made here

        if extra_privacy:
            # Call the anonymize_pii function if extra privacy is enabled
            masked_text, detected_pii = mask_text1(st.session_state.new_ticket.text,
                                        st.session_state.simulate.attributedb,
                                        cat)  # Change made here
        else:
            # Call the mask_text function if extra privacy is not enabled
            masked_text, detected_pii = mask_text(st.session_state.new_ticket.text,
                                                st.session_state.simulate.attributedb,
                                                cat)
        # masked_text, detected_pii = mask_text(st.session_state.new_ticket.text,
        #                                      st.session_state.simulate.attributedb,
        #                                      cat)
        # results = self.detect_ticket_pii(st.session_state.new_ticket.text)
        # masked_ticket_text = self.mask_ticket_pii(ticket_text=st.session_state.new_ticket.text,
        #                                             result=results)
        # result_dict = self.recognizerresult_to_dict(st.session_state.new_ticket.text, results)
        inner_cols[1].write(st.session_state.new_ticket.text)
        inner_cols[1].write(detected_pii)
        inner_cols[2].write(cfg.CATEGORY_NAME[st.session_state.new_ticket.category])
        inner_cols[2].markdown('**Sensitive score**: {}'.format(round(st.session_state.new_ticket.get_sensitivity_score(),2)))
        inner_cols[1].markdown('##### Masked Ticket')
        inner_cols[1].write(masked_text)
    
    def next_ticket(self) -> None:
        st.session_state.new_ticket = st.session_state.simulate.ticketdb.next_ticket()

    def reset(self):
        '''Reset the Simulation'''
        st.session_state.file_dict = {
                                        'ticket_file': st.session_state.ticket_csv,
                                        'ticket_arrival_file': st.session_state.ticket_arrival_csv,
                                        'attribute_file': st.session_state.attribute_csv
                                    }
        st.session_state.simulate = Simulate(st.session_state.file_dict)
        st.session_state.ticket_count = 0
        st.session_state.new_ticket = Ticket()

    def save_uploadedfile(self, uploadedfile):
        with open(os.path.join("tempDir", uploadedfile.name), "wb") as f:
            f.write(uploadedfile.getbuffer())
        return st.success("Uploaded {}".format(uploadedfile.name), icon='✅')
    
    def get_attribute_from_uploaded_file(self, uploadedfile) -> List[str]:
        '''get attribute read from uploded file'''
        with open(uploadedfile.name) as f:
            lines = f.readlines()
        attr = []
        for line in lines:
            line_split = re.sub('[^A-Za-z0-9_,]+', '', line).split(',')
            line_split = [item for item in line_split if item != '']
            attr.extend(line_split)
        
        return attr

    def save_attribute_csv(self, p_factor:float, dp_dict:dict, vul_1:list, vul_2:list,
                           vul_3:list, vul_4:list, vul_5:list) -> None:
        '''Save generated privacy factor dictionary in attribute csv '''
        attr_list = [vul_1, vul_2, vul_3, vul_4, vul_5]
        r_list = ['very low','low','medium','high','very high']
        
        fields = ['attribute_id','type','vulnerability_score','disclosure_percentage', 'masking_plan']
        file_name = str(cfg.BASE_DIR) + '/input/attribute/attribute_privacyfactor_{}.csv'.format(round(p_factor,2))
        with open(file_name, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(fields)
            id = 0
            for i in range(5):
                for attr in attr_list[i]:
                    row = [id, attr,i+1,dp_dict[r_list[i]], dcfg.MASKING_PLAN[attr]]
                    csv_writer.writerow(row)
                    id += 1
            csv_file.close()

def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()


if __name__ == '__main__':
    demo = PESODemo()
    demo.window()
