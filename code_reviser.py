# coding: utf8

import os

SEP = os.linesep

class UnittestCodeRevisor(object):
    def __init__(self, host='localhost', tags=[]):
        self.host = host
        self.tags = tags

    def get_code_lines(self, req_elem_list):
        code_lines = []

        import_apart = [
            'import requests',
            'import json',
            'import unittest',
            'HOST= ""',
            "HEAD={}",
            'class AllTest(unittest.TestCase):',

        ]

        code_lines = code_lines + import_apart

        for elem in req_elem_list:

            if self.tags and not set(elem['tag']).issubset(self.tags):
                continue
            code_lines.append(self.__get_code(elem['url'], elem['method'], elem['headers'], elem['params'], elem['data']))

        return code_lines


    def __get_code(self, url, method, headers, params, data):
        case_name = url.replace('/', '_').replace('.', '_').replace(':', '').replace('-', '_').replace('{', '').replace('}', '')

        variabled_url = self.__variable_url(url)


        variabled_param = self.__variable_param(params)
        variabled_data = self.__variable_param(data)

        # test code template
        call_code_format = (
            '''
            def test_{case_name}(self):
        
                url = '%s{url}' %HOST
                method = '{method}'
        
                params = {params}
                data = {data}
        
                print("!!! url is %s{url}" %HOST)
                print("!!! method is %s" %method)
                print("!!! headers is %r" %HEAD)
                print("!!! params is {params}")
                print("!!! data is %r" %data)
        
                res = requests.request(method, url, headers=HEAD, params=params, data=data)
                res = json.loads(res.text)
                print('--- result: %r' %res) 
                assert res['status'] == 'ok'

            '''
        )

        call_code = call_code_format.format(
            sep=SEP,
            case_name=case_name,
            url=variabled_url,
            method=method.lower(),
            params=repr(variabled_param),
            data=data
        )
        return call_code

    def __variable_url(self, url):
        vari_url = url.replace(self.host, '%s')
        vari_url = vari_url.replace('{', '').replace('}', '')

        return vari_url

    def __variable_param(self, params: dict):
        return params


#
# class BehaveTestCodeRevisor(object):
#     def __init__(self, req_list):
#         self.req_list = req_list
#
#     def get_code_lines(self):
#         for req in self.req_list:
#             url = req['url']
#             params = req['params']
#             data = req['data']
#
#             params




