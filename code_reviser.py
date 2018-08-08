# coding: utf8

import os
import re

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
            'HEAD={',
            "   'Referer' : f'{HOST}/swagger-ui.html',",
            "   'Content-Type': 'application/json' ",
            "}",
            'class AllTest(unittest.TestCase):',
        ]

        code_lines = code_lines + import_apart

        for elem in req_elem_list:

            if self.tags and not set(elem['tag']).issubset(self.tags):
                continue
            code_lines.append(
                self.__get_code(elem['url'], elem['method'], elem['headers'], elem['params'], elem['data']))

        return code_lines

    def __get_code(self, url, method, headers, params, data):

        print(f'get_code {url} {method}')

        var_inurls = UnittestCodeRevisor.gen_var_in_url(url)
        case_name = url.replace('/', '_').replace('.', '_').replace(':', '').replace('-', '_').replace('{', '').replace(
            '}', '')

        variabled_url = variable_url(url, self.host)
        variabled_param = UnittestCodeRevisor.gen_variables(params, type='params')
        variabled_data = UnittestCodeRevisor.gen_variables(data, type='data')

        case_code = f"    def test_{method}_{case_name}(self):"

        for item in var_inurls:
            case_code = case_code + SEP + '        ' + item

        for item in variabled_param:
            case_code = case_code + SEP + '        ' + item

        for item in variabled_data:
            case_code = case_code + SEP + '        ' + item

        # test code template
        call_code_format = (
            '''
        url = f'%s{url}' %HOST 
        method = '{method}'
        
        print(f"!!! url is %s{url}" %HOST)
        print("!!! method is %s" %method)
        print("!!! headers is %r" %HEAD)
        print("!!! params is {params}")
        print("!!! data is %r" %data)
        
        res = requests.request(method, url, headers=HEAD, params=params, data=data)
        res = res.json()
        print('--- result: %r' %res) 
        self.assertEqual('ok', res['status'])
    
            '''
        )

        call_code = call_code_format.format(
            sep=SEP,
            case_name=case_name,
            url=variabled_url,
            method=method.lower(),
            params=repr(params),
            data=data
        )

        call_code = case_code + SEP + call_code

        return call_code

    def gen_variables(params: dict, type='params') -> list:
        result = []
        for key in params.keys():
            result.append(f'_{key.replace("-", "_")} = ""')

        result.append(f'{type} = {{')
        for key, value in params.items():
            result.append(f"    '{key}': _{key.replace('-', '_')} , ")

        result.append('}')
        return result

    def gen_var_in_url(url) -> list:
        result = []

        vars = re.findall('\{(.*?)\}', url)

        for var in vars:
            var = var.replace('-', '_')
            result.append(str(var) + " = '100'")

        return result


class CustomCodeRevisor(object):
    def __init__(self, host='localhost', tags=[]):
        self.host = host
        self.tags = tags

    def get_code_lines(self, req_elem_list):
        code_lines = []

        import_apart = [
            'import requests',
            'import json',
            'import unittest',
            'from ddt import *',
            'import os',
            'import csv',
            'import copy',
            '@ddt',
            'class AllTest(unittest.TestCase):',
            '               HOST= ""',
            '               HEAD={',
            "                   'Referer' : f'{HOST}/swagger-ui.html',",
            "                   'Content-Type': 'application/json' ",
            "               }",

        ]

        code_lines = code_lines + import_apart

        for elem in req_elem_list:

            if self.tags and not set(elem['tag']).issubset(self.tags):
                continue
            code_lines.append(
                self.__get_code(elem['url'], elem['method'], elem['headers'], elem['params'], elem['data']))

        return code_lines

    def __get_code(self, url, method, headers, params, data):

        var_inurls = self.gen_var_in_url(url)
        case_name = url.replace('/', '_').replace('.', '_').replace(':', '').replace('-', '_').replace('{', '').replace(
            '}', '')

        variabled_url = variable_url(url, self.host)
        variabled_param = self.gen_variables(params, type='params')
        variabled_data = self.gen_variables(data, type='data')

        case_code = \
            f'''    
                    @data(*annotated('test_{case_name}'))
                    @unpack
                    def test_{method}_{case_name}(self, token, exchange_code, status):
            '''

        for item in var_inurls:
            case_code = case_code + SEP + '                     ' + item

        for item in variabled_param:
            case_code = case_code + SEP + '                     ' + item

        for item in variabled_data:
            case_code = case_code + SEP + '                     ' + item

        # test code template
        call_code_format = (
            '''
                    url = f'%s{url}' %self.HOST 
                    method = '{method}'
                    
                    header = copy.deepcopy(self.HEAD)
                    if token == 'valid':
                        header['HB-PRO-TOKEN'] = self.TOKEN
                    
                    if exchange_code != 'empty':
                        header['CLOUD-EXCHANGE'] = exchange_code
                    
                    print(f"!!! url is %s{url}" %self.HOST)
                    print("!!! method is %s" %method)
                    print("!!! headers is %r" %header)
                    print("!!! params is %r" %params)
                    print("!!! data is %r" %data)
                    
                    res = requests.request(method, url, headers=header, params=params, data=data)
                    print('--- result: %r' %res) 
                    assert res.status_code == int(status), 'expect %s, but %s' %(status, res.status_code)
            '''
        )

        call_code = call_code_format.format(
            sep=SEP,
            case_name=case_name,
            url=variabled_url,
            method=method.lower(),
            params=repr(params),
            data=data
        )

        call_code = case_code + SEP + call_code

        return call_code

    def gen_variables(self, params: dict, type='params') -> list:
        result = []
        for key in params.keys():
            result.append(f'_{key.replace("-", "_")} = ""')

        result.append(f'{type} = {{')
        for key, value in params.items():
            result.append(f"    '{key}': _{key.replace('-', '_')} , ")

        result.append('}')
        return result

    def gen_var_in_url(self, url) -> list:
        result = []

        vars = re.findall('\{(.*?)\}', url)

        for var in vars:
            var = var.replace('-', '_')
            result.append(str(var) + " = '100'")

        return result


class BehaveCodeRevisor(object):
    def __init__(self, host='localhost', tags=[]):
        self.host = host
        self.tags = tags

    def get_code_lines(self, req_elem_list):
        code_lines = []
        feature_lines = []

        import_apart = [
            '# coding: utf8',
            '',
            'from behave import *',
            'import json',
            ''
        ]

        for elem in req_elem_list:

            if self.tags and not set(elem['tag']).issubset(self.tags):
                continue

            variabled_url = variable_url(elem['url'], self.host)
            variabled_param = self.__gen_variables(elem['params'], type='params')
            variabled_data = self.__gen_variables(elem['data'], type='data')

            vars = self.__get_vars(variabled_data, variabled_param, variabled_url)

            code_lines.append(self.__get_feature_lines(vars))

            code_lines.append('---------------------------------------')
            code_lines = code_lines + import_apart
            code_lines.append(
                self.__get_code(elem['url'], elem['method'], elem['headers'], elem['params'], elem['data']))

            code_lines.append('=======================================')

        return code_lines

    def __get_feature_lines(self, vars):
        code = (
            '''
            #language: zh-CN
            
            @
            功能: 
                场景大纲: 
            '''
        )

        code = code + "假如 "
        for var in vars:
            code = code + "<" + var + ">" + ", "

        code = code + SEP + "            当 "
        code = code + SEP + "            那么 <status>, <expect>"
        code = code + SEP + "            例子:"
        code = code + SEP + "            | "
        for var in vars:
            code = code + var + " | "
        code = code + " status | expect |"

        return code

    def __get_code(self, url, method, headers, params, data):

        var_inurls = self.__gen_var_in_url(url)

        variabled_url = variable_url(url, self.host)
        variabled_param = self.__gen_variables(params, type='params')
        variabled_data = self.__gen_variables(data, type='data')

        # print(f'variabled_url: {variabled_url}')
        # print(f'variabled_param: {variabled_param}')
        # print(f'variabled_data: {variabled_data}')

        given_part = self.__gen_given_code(variabled_url, variabled_param, variabled_data)

        when_part = self.__gen_when_code(variabled_url, method, headers, params, data)

        then_part = self.__gen_then_code()

        call_code = given_part + SEP \
                    + when_part + SEP \
                    + then_part

        return call_code

    def __gen_variables(self, params: dict, type='params') -> list:
        result = []
        for key in params.keys():
            result.append(key.replace("-", "_"))
        return result

    def __gen_var_in_url(self, url) -> list:
        result = []
        vars = re.findall('\{(.*?)\}', url)
        for var in vars:
            var = var.replace('-', '_')
            result.append(var)
        return result

    def __enbrace_variable(var_list, front, end):
        result = ''
        for var in var_list:
            result.append(front + var + end)
        return result

    def __gen_given_code(self, url, params, data):

        vars = self.__get_vars(data, params, url)

        given_code = (
            '@Given("'
        )

        for var in vars:
            given_code = given_code + '{' + var + '}' + ', '

        given_code = given_code + '")'

        given_code = given_code + SEP + 'def step_impl(context'

        for var in vars:
            given_code = given_code + ', ' + var

        given_code = given_code + '):'

        for var in vars:
            given_code = given_code + SEP + f'   context.{var} = {var}'

        # print(f"======= given_code is {given_code}")

        return given_code

    def __get_vars(self, data, params, url):
        vars = list()
        vars = vars + self.__gen_var_in_url(url)
        if len(params) > 0:
            vars = vars + params
        if len(data) > 0:
            vars = vars + data
        return vars

    def __gen_when_code(self, url, method, headers, params, data):

        when_code = (
            f'''
@When('')
def step_impl(context):
    url = "{url}"
    method = "{method}" 
    headers = {headers}   
    params = {params}
    body = {data}           
            '''
        )

        # print(f" when_code is {when_code}")
        return when_code

    def __gen_then_code(self):

        then_code = (
            '''
@then('{status}{expect}')
def step_impl(context, status, expect):
    pass
            '''
        )

        # print(f"then_code is {then_code}")

        return then_code


def variable_url(url, host='localhost'):
    vari_url = url.replace(host, '%s')

    vars = re.findall('\{(.*?)\}', url)
    for var in vars:
        new_var = var.replace('-', '_')
        vari_url = vari_url.replace(var, new_var)
    return vari_url
