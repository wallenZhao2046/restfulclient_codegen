# ---------------input har format --------------------------
## output behave code
python code_generator.py -i test_data/har_double.json -o tmp/002.txt -t behave

## output unittest code
python code_generator.py -i test_data/har_single.json -o tmp/002.txt

# -------------- input swagger ui format ---------------------
## output behave code with tag
python code_generator.py -i test_data/swagger-ui-sample.json -f swagger -o tmp/001.txt  -t behave -TAG mgt-api-controller

## output unittest code
python code_generator.py -i test_data/swagger-ui-sample.json -o tmp/001.txt 

# ----------------input postman collection export format -------------------------
## output behave code
python code_generator.py -i test_data/postman_collection.json -f postman -o tmp/003.txt -t behave

## ouput api service code
python code_generator.py -i test_data/swagger-ui_0920.json -t service -f swagger -TAG dw-mgt-controller   -o tmp/dw-mgt-controller.py
