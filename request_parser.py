# coding: utf8

import json
import json.decoder
import os

SEP = os.linesep

def filter_url(url: str) -> object:
    if url.find('?') > 0:
        url = url[:url.find('?')]
    return url

class HarRequestParser(object):
    def __init__(self, fobj):
        self.fobj = fobj

    def set_har_file(self, fobj):
        self.fobj = fobj

    def parse_request(self) -> list:
        print('------------ begin to parse request ------------')
        fobj = self.fobj
        request_list = []
        for entry in json.load(fobj)['log']['entries']:
            # for each in entries ....
            request_el = entry['request']
            url, method, headers, params, data = self.__get_request_element(request_el)
            d = {
                'url' : url,
                'method' : method,
                'headers' : headers,
                'params' : params,
                'data' : data
            }

            print(f'data is {d}')
            request_list.append(d)
        return request_list

    def __get_request_element(self, request_el):
        # for request ...
        # for url
        url = request_el['url']

        url = filter_url(url)
        # for method
        method = request_el['method']
        # for postData
        data = dict()
        if 'postData' in request_el:
            if 'text' in request_el['postData']:
                data = request_el['postData']['text']
            elif 'params' in request_el['postData']:
                raise NotImplementedError(
                    "Haven't seen 'params' in the wild yet.")

        params = None
        if 'queryString' in request_el:
            params = dict(
                (d['name'], d['value']) for d in request_el['queryString']
            )

        # for headers dict
        headers = dict(
            (d['name'], d['value']) for d in request_el['headers'])
        ## filter headers
        headers = {k: v for k, v in headers.items() if
                   k.lower().startswith('referer') or k.lower().startswith('token') or k.lower().startswith('hb-pro-token')}
        headers['Content-Type'] = 'application/json'
        return url, method, headers, params, data


class PostmanCollectionParser(object):
    def __init__(self, fobj):
        self.fobj = fobj

    def set_collection_file(self, fobj):
        self.fobj = fobj

    def parse_request(self) -> list:
        request_list = []
        content = json.load(self.fobj)
        item_list = content['item']
        self.parse_item(item_list, request_list)
        return request_list

    def parse_item(self, itemobj, request_list):
        for item in itemobj:
            print(f'item is {item}')
            if 'item' in item.keys():
                self.parse_item(item['item'], request_list)
            else:
                url, method, headers, params, data = self.parse_single(item)
                d = {
                    'url': url,
                    'method': method,
                    'headers': headers,
                    'params': params,
                    'data': data
                }
                request_list.append(d)

    def parse_single(self, item):

        method = item['request']['method']
        headers = self.list2dict(item['request']['header'])
        data = {}

        body_part = item['request']['body']

        if 'raw' in body_part.keys() and body_part['raw'] != '':
            print(f'body_part is {body_part}')
            body_raw = body_part['raw']
            body_raw = body_raw.replace('"{{', '"').replace('}}"', '"').replace('{{', '"').replace('}}', '"')
            print(f'body_raw is {body_raw}')
            try:
                data = json.loads(body_raw)
            except:
                pass

        url_part = item['request']['url']

        url = filter_url(url_part['raw'])

        # TODO: parse URL in item: handle :id  variable,  replace :id by variable
        params = {}

        if 'query' in url_part.keys():
            params = self.list2dict(item['request']['url']['query'])

        return url, method, headers, params, data

    def filter_varible(self, filtered_url, vars):
        variabled_url = filtered_url
        # TODO: need to variable
        return variabled_url

    def list2dict(self, obj_list):
        target_dict = dict()
        for obj in obj_list:
            if obj['key'] in target_dict:
                target_dict[obj['key']] = target_dict[obj['key']] + ',' + obj['value']
            else:
                target_dict[obj['key']] = obj['value']
        return target_dict


class SwaggerParser(object):
    def __init__(self, fobj: object, include_tags=list()):
        self.fobj = fobj
        self.__include_tags = include_tags

    def parse_request(self) -> list:
        content = json.load(self.fobj)
        tags = content['tags']
        host = content['host']

        definitions = content['definitions']
        body_def_dict = self.__parse_definitions(definitions)

        req_list = []
        paths = content['paths']

        for url, req_content in paths.items():
            method = list(req_content.keys())[0]
            content_detail = req_content[method]
            tag = content_detail['tags']

            params, data = {}, {}

            if 'parameters' in content_detail:
                params, data = self.__parse_parameters(content_detail['parameters'], body_def_dict)

            headers = self.__parse_headers(content_detail)
            d = {
                'url': url,
                'method': method,
                'headers': headers,
                'params': params,
                'data': data,
                'tag': tag
            }

            if self.__include_tags and tag[0] in self.__include_tags:
                req_list.append(d)
            else:
                req_list.append(d)

        return req_list

    def __parse_definitions(self, def_obj) -> dict:
        definition = dict()

        for data_name, value in def_obj.items():
            if 'ApiResponse' in data_name:
                continue
            if 'properties' not in value :
                continue
            data_dict = self.__parse_properties(value['properties'])
            definition[data_name] = data_dict
        return definition

    def __parse_properties(self, prop_obj) -> dict:
        data_dict = dict()
        for param_name, value in prop_obj.items():
            data_dict[param_name] = value['type']

        return data_dict

    def __parse_parameters(self, para_list, definitions) -> (dict, dict):
        # TODO enhance
        params = dict()
        data = dict()

        for param in para_list:

            location = param['in']
            if location == 'query':
                param_name = param['name']
                params[param_name] = ""
            elif location == 'body':
                if 'schema' in param:
                    schema = param['schema']
                    ref_name = schema['$ref'].replace('#/definitions/', '')
                    if ref_name in definitions:
                        data = definitions[ref_name]

            elif location == 'path':
                pass
            elif location == 'header':
            #     TODO: need to fix header
                pass
            else:
                raise Exception(f'unsupport param in {location}')

        return params, data

    def __parse_headers(self, content_obj):
        return {}


