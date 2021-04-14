import re

text = '<a href="http://mall.jd.com/index-881388.html" target="_blank" clstag="shangpin|keycount|product|bbtn" class="hl_red">京日达服饰专营店</a>'


re_match = re.search('<a href="(.*?)"', text)
if re_match:
    print(re_match.group(1))









