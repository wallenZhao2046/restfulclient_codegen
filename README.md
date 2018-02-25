# restfulclient_codegen

restfulclient_codegen is a tool to generate restful client test code automatically by convert Har, postman exported file, or swagger-ui


There are three components, code generator request_parser and code reviser


usage: code_generator.py [-h] [-i INFILE] [-f REQFORMAT] [-o OUTFILE]
                         [-t TESTTYPE] [-TAG TAGS]

            description:
                Open a HAR file / Swagger-ui json file / postman export file
                Output a unittest or behave test code file.
                --------------------------------------------------------------------
                - Swagger-ui json file that can be get by http://<HOST>/v2/api-docs, and save to a file.
                - HAR file that can be exported by Firefox or Chrome "Inspect".
                - postman export file that can be exported from postman colleciton as a JSON file ("Collection v2.1") .



optional arguments:
  -h, --help    show this help message and exit
  -i INFILE     specify the input file
  -f REQFORMAT  input file's format, supports(swagger/har/postman), default is
                har
  -o OUTFILE    specify the output file
  -t TESTTYPE   output file's test code type, supports(unittest/behave),
                default is unittest
  -TAG TAGS     OPTIONAL: specify tag name of swagger-ui json file, comma
                seperated multiple tag name.

