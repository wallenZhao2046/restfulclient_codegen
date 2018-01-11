# coding: utf8

import argparse
import os
import json
from code_reviser import UnittestCodeRevisor
from request_parser import HarRequestParser, PostmanCollectionParser, SwaggerParser

SEP = os.linesep

class CodeGenerator(object):
    def __init__(self):
        pass

    def main(self):
        parser = argparse.ArgumentParser(
            description=('Open a HAR file (that can be exported by '
                         'Firefox or Chrome "Inspect") and write a '
                         'python script that performs the same '
                         'HTTP requests using the Python "requests" '
                         'module.')
        )
        parser.add_argument(
            '-i',
            dest='infile',
            default='-'
        )
        parser.add_argument(
            '-o',
            dest='outfile',
            default='-'
        )
        parser.add_argument(
            '-F',
            dest='reqformat',
            default='har'
        )
        args = parser.parse_args()
        print(f'input har file : {args.infile}')
        print(f'output testcode file: {args.outfile}')
        print(f'reqformat : {args.reqformat}')
        fobj = open(args.infile, mode='r', encoding='utf-8', closefd=True)

        if args.reqformat == 'har':
            req_parser = HarRequestParser(fobj)
        elif args.reqformat == 'swagger':
            req_parser = SwaggerParser(fobj)
        elif args.reqformat == 'postman':
            req_parser = PostmanCollectionParser(fobj)
        else:
            raise Exception(f'unsupport request format {args.reqformat}')

        req_elem_list = req_parser.parse_request()

        code_revisor = UnittestCodeRevisor()

        code_lines = code_revisor.get_code_lines(req_elem_list)

        result = SEP.join(code_lines)

        print(f'result is {json.dumps(result, indent=4)}')

        outobj = open(args.outfile, mode='w', encoding='utf-8')
        outobj.write(result)


if __name__ == '__main__':

    # CodeGenerator().main()

    fobj = open("test_data/swagger-ui-sample.json", mode='r', encoding='utf-8', closefd=True)


    req_parser = SwaggerParser(fobj, exclude_tags=["internal-api-controller", 'user-center-controller', 'user-center-bitexpro-controller', 'wallet-api-controller'])

    req_elem_list = req_parser.parse_request()

    # for elem in req_elem_list:
    #     print(f'req_elem: {json.dumps(elem, indent=4)}')


    code_revisor = UnittestCodeRevisor(tags=['mgt-api-controller'])

    code_lines = code_revisor.get_code_lines(req_elem_list)

    result = SEP.join(code_lines)


    # import autopep8
    # result = autopep8.fix_code(
    #         result, options={'aggressive': 1})



    # try:
    #     import autopep8
    #     result = autopep8.fix_code(
    #         result, options={'aggressive': 1})
    # except ImportError as e:
    #     pass

    print(f'{result}')

    # req_parser = PostmanCollectionParser(fobj)
