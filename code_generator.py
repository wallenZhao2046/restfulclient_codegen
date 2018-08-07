# coding: utf8

import argparse
import os
import json
import textwrap
from code_reviser import UnittestCodeRevisor, BehaveCodeRevisor, CustomCodeRevisor
from request_parser import HarRequestParser, PostmanCollectionParser, SwaggerParser

SEP = os.linesep


class CodeGenerator(object):
    '''
    命令行工具入口
    '''

    def __init__(self):
        pass

    def main(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='''
            description: 
                Open a HAR file / Swagger-ui json file / postman export file 
                Output a unittest or behave test code file.
                --------------------------------------------------------------------
                - Swagger-ui json file that can be get by http://<HOST>/v2/api-docs, and save to a file.        
                - HAR file that can be exported by Firefox or Chrome "Inspect". 
                - postman export file that can be exported from postman colleciton as a JSON file ("Collection v2.1") .
            
            '''

        )
        parser.add_argument(
            '-i',
            help='specify the input file',
            dest='infile',
            default='-'
        )
        parser.add_argument(
            '-f',
            help="input file's format, supports(swagger/har/postman), default is har",
            dest='reqformat',
            default='har'
        )
        parser.add_argument(
            '-o',
            help='specify the output file',
            dest='outfile',
            default='-'
        )
        parser.add_argument(
            '-t',
            help="output file's test code type, supports(unittest/behave), default is unittest",
            dest='testtype',
            default='unittest'
        )
        parser.add_argument(
            '-TAG',
            help='OPTIONAL: specify tag name of swagger-ui json file, comma seperated multiple tag name. ',
            dest='tags',
            default='-'
        )
        args = parser.parse_args()

        print(f'- input file: {args.infile}')
        print(f'- output file: {args.outfile}')
        print(f'- request format : {args.reqformat}')
        print(f'- test type: {args.testtype}')
        print(f'- tags: {args.tags}')
        fobj = open(args.infile, mode='r', encoding='utf-8', closefd=True)

        if args.reqformat == 'swagger':
            req_parser = SwaggerParser(fobj)
        elif args.reqformat == 'postman':
            req_parser = PostmanCollectionParser(fobj)
        else:
            req_parser = HarRequestParser(fobj)

        if args.tags != '-':
            tags = args.tags.split(',')
        else:
            tags = []

        if args.testtype == 'behave':
            code_revisor = BehaveCodeRevisor(tags=tags)
        if args.testtype == 'custom':
            code_revisor = CustomCodeRevisor(tags=tags)
        else:
            code_revisor = UnittestCodeRevisor(tags=tags)

        req_elem_list = req_parser.parse_request()

        code_lines = code_revisor.get_code_lines(req_elem_list)

        result = SEP.join(code_lines)

        outobj = open(args.outfile, mode='w', encoding='utf-8')
        outobj.write(result)

        print('generate done ...')
        print(f'check result in {args.outfile}')


if __name__ == '__main__':
    CodeGenerator().main()

    # fobj = open("test_data/swagger-ui-sample.json", mode='r', encoding='utf-8', closefd=True)
    #
    #
    # req_parser = SwaggerParser(fobj, exclude_tags=["internal-api-controller", 'user-center-controller', 'user-center-bitexpro-controller', 'wallet-api-controller'])
    #
    # req_elem_list = req_parser.parse_request()
    #
    # # for elem in req_elem_list:
    # #     print(f'req_elem: {json.dumps(elem, indent=4)}')
    #
    # #### work fine for unittest case
    # # code_revisor = UnittestCodeRevisor(tags=['mgt-api-controller'])
    # # code_lines = code_revisor.get_code_lines(req_elem_list)
    # # result = SEP.join(code_lines)
    # # print(f'{result}')
    #
    #
    # # import autopep8
    # # result = autopep8.fix_code(
    # #         result, options={'aggressive': 1})
    #
    #
    #
    # # try:
    # #     import autopep8
    # #     result = autopep8.fix_code(
    # #         result, options={'aggressive': 1})
    # # except ImportError as e:
    # #     pass
    #
    #### work fine for behave test case
    # code_revisor = BehaveCodeRevisor(tags=['mgt-api-controller'])
    #
    # code_lines, feature_lines = code_revisor.get_code_lines(req_elem_list)
    # result = SEP.join(code_lines)
    #
    # feature = SEP.join(feature_lines)
    #
    # print(f'{result}')
    # print(f'=================')
    # print(f'{feature}')

    # req_parser = PostmanCollectionParser(fobj)
