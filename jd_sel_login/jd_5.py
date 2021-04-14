# 快识别打码的平台
KUAI_USERNAME = 'tang1323'
KUAI_PASSWORD = '130796abc'
KUAI_SOFT_ID = 907581
KUAI_KIND = 9004
# 对接打码平台，识别验证码,这是快识别平台
from jd_sel_login.parse_code import base64_api

img_path = 'D:\\Py-Project\\spider\\jd_sel_login\\jd_6_cap.png'
# 与接口对应
# 这里超级鹰只能识别图片的二进制，而快识别只识别原图片
code_result = base64_api(KUAI_USERNAME, KUAI_PASSWORD, img_path)
print("验证码识别结果：", code_result)
pass


# captcha2.png
# 33类型：147,46
# 34类型：

# captcha1.png
# 33类型：128,35
# 34类型：145，48
