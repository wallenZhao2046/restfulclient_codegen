## input swagger format and output behave code with tag
python code_generator.py -i test_data/swagger-ui-sample.json -f swagger -o tmp/001.txt  -t behave -TAG mgt-api-controller
## input swagger format and output unittest code
python code_generator.py -i test_data/swagger-ui-sample.json -o tmp/001.txt 
## input har format and output unittest code
python code_generator.py -i test_data/har_single.json -o tmp/002.txt
## input har format and output behave code
python code_generator.py -i test_data/har_double.json -o tmp/002.txt -t behave
## input postman collection export file and output behave code
python code_generator.py -i test_data/postman_collection.json -f postman -o tmp/003.txt -t behave
