KEY = 'key_id'
SECRET = b'000000'
NMI = 'nmi_code'
VALID_RESPONSE = {
    'success': True,
    'code': '0',
    'msg': 'success',
    'data': {'item': 1}}

VALID_RESPONSE_LIST = {
    'success': True,
    'code': '0',
    'msg': 'success',
    'data': [{'item': 1}, {'item': 2}]}

VALID_RESPONSE_RECORDS = {
    'success': True,
    'code': '0',
    'msg': 'success',
    'data': {'records': [{'item': 1}, {'item': 2}]}}

VALID_RESPONSE_PAGED_RECORDS = {
    'success': True,
    'code': '0',
    'msg': 'success',
    'data': {'page': {'records': [{'item': 1}, {'item': 2}]}}}
