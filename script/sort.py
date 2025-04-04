import os
import sys
import re
import datetime
from typing import List, Dict

# 获取当前时间
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 读取文件名
file_name = sys.argv[1]

# 国家代码列表
countries = (
    "af|ax|al|dz|as|ad|ao|ai|aq|ag|ar|am|aw|au|at|az|bs|bh|bd|bb|by|be|bz|bj|bm|bt|bo|bq|ba|bw|br|io|bn|bg|bf|bi|cv|kh|cm|ca|ky|cf|td|cl|co|km|cd|cg|ck|cr|ci|hr|cu|cw|cy|cz|dk|dj|dm|do|ec|eg|sv|gq|er|ee|et|fk|fo|fj|fi|fr|gf|pf|tf|ga|gm|ge|de|gh|gi|gr|gl|gd|gp|gu|gt|gg|gn|gw|gy|ht|hm|va|hn|hu|is|in|id|ir|iq|ie|im|il|it|jm|jp|je|jo|kz|ke|ki|kp|kr|kw|kg|la|lv|lb|ls|lr|ly|li|lt|lu|mo|mg|mw|my|mv|ml|mt|mh|mq|mr|mu|yt|mx|fm|md|mc|mn|me|ms|ma|mz|mm|na|nr|np|nl|nc|nz|ni|ne|ng|nu|nf|mk|mp|no|om|pk|pw|ps|pa|pg|py|pe|ph|pn|pl|pt|pr|qa|re|ro|ru|rw|bl|sh|kn|lc|mf|pm|vc|ws|sm|st|sa|sn|rs|sc|sl|sg|sx|sk|si|sb|so|za|gs|ss|es|lk|sd|sr|sj|sz|se|ch|sy|tw|tj|tz|th|tl|tg|tk|to|tt|tn|tr|tm|tc|tv|ug|ua|ae|gb|us|um|uy|uz|vu|ve|vn|vg|vi|wf|eh|ye|zm|zw"
)

# 打开文件并读取所有行
with open(file_name, 'r', encoding='utf8') as f:
    lines = f.readlines()

# 使用正则表达式移除含有无用信息的行
lines = [
    line.replace('\r', '').replace('\n', '').strip() for line in lines
    if len(line.strip()) > 0 and not line.strip().startswith('#') and not re.match(r'^[\s]*!', line) and not re.match(r'^[\s]*\[', line) and not re.search(r'\.(' + countries + r')\^', line)
]

# 去重函数，短域名已被拦截，则干掉所有长域名
def repetition(l: List[str]) -> List[str]:
    l = sorted(l, key=lambda item: len(item), reverse=False)  # 按从短到长排序
    if len(l) < 2:
        return l
    if l[0] == '':
        return l[:1]
    tmp = set()
    for i in range(len(l) - 1):
        for j in range(i + 1, len(l)):
            if re.match(r'.*\.' + re.escape(l[i]), l[j]):
                tmp.add(l[j])
    l = list(set(l) - tmp)
    l.sort()
    return l

# 创建一个字典来存储唯一的规则
unique_rules: Dict[str, List[str]] = {}
for line in lines:
    rule = line.strip()
    if rule:
        domain = rule.split('||')[-1].split('^')[0]  # 提取域名部分
        if domain not in unique_rules:
            unique_rules[domain] = []
        unique_rules[domain].append(rule)

# 按 adblock 规则进行去重
deduped_rules: List[str] = []
for domain, rules in unique_rules.items():
    deduped_rules.extend(repetition(rules))

# 提取主域名的函数
def get_parent_domain(domain: str) -> str:
    parts = domain.split('.')
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    return domain

# 对规则进行排序，按照主域名部分进行排序
sorted_rules = sorted(deduped_rules, key=lambda item: get_parent_domain(item.split('||')[-1].split('^')[0]))

# 在开头添加信息
header = [
    f'! Title: My filter\n',
    f'! Description: This is an adblock filter list to block ads efficiently.\n',
    f'! Homepage: https://github.com/ykvhjnn/ad-filter\n',
    f'! Source: {file_name}\n',
    f'! Version: {datetime.datetime.now().strftime("%Y%m%d%H%M%S")}\n',
    f'! Last modified: {now}\n',
    f'! Blocked domains: {len(sorted_rules)}\n',
    f'!\n'
]

# 写入文件
with open(file_name, 'w', encoding='utf8') as f:
    f.writelines(header)
    for rule in sorted_rules:
        f.write(rule + '\n')
