#!/usr/bin/env python
# coding: utf-8

import traceback
import requests
import os
import datetime
import sys


class TeleLog:
    
    def __init__(self, api, chat_id):
        self.api = api
        self.chat_id = chat_id
        
    def make_request(self, method, params):
        url_to_request = 'https://api.telegram.org/bot{api}/{method}'.format(api=self.api, method=method)
        return requests.post(url_to_request, params=params)
        
    def send_message(self, text):
        params = {'chat_id': str(self.chat_id), 'text': text}
        return self.make_request('sendMessage', params)
    
    def send_error(self, text=''):
        
        tb = traceback.format_exc()

        if hasattr(sys, 'ps1') is not True:
            current_file_name = os.path.basename(__file__)
        else:
            current_file_name = "interactive mode"

        current_datetime = datetime.datetime.now()

        type_log = "ERROR"

        message = "{current_datetime}\n{type_log} in {current_file_name}\n{text}\n{tb}".format(
            type_log=type_log, 
            current_file_name=current_file_name, 
            current_datetime=current_datetime.replace(microsecond=0), 
            text=text,
            tb=tb
        )

        return self.send_message(message)
