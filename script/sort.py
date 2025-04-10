import sys
import re
import datetime
from typing import List


# 扩展后的国家代码后缀集合，排除国际域名和中国域名
COUNTRY_SUFFIXES = {
    "jp", "kr", "pl", "uk", "de", "fr", "it", "ru", "es", "ca", "au", "ch", "se", "br", "za", "in", "id", "vn", "th", "my",
    "ar", "mx", "ph", "cl", "nz", "pt", "be", "no", "fi", "gr", "tr", "sa", "ae", "hk", "sg", "tw", "dk", "ie", "cz", "hu",
    "ro", "bg", "sk", "lt", "lv", "ee", "is", "mt", "cy", "rs", "si", "hr", "ba", "mk", "me", "al", "ge", "am", "az", "by",
    "kg", "kz", "md", "tj", "tm", "uz", "ua", "pk", "np", "lk", "bd", "kh", "la", "mm", "bt", "bn", "mn", "af", "ir", "iq",
    "jo", "lb", "om", "qa", "kw", "bh", "ye", "sy", "ps", "dz", "ma", "tn", "ly", "eg", "sd", "et", "ng", "gh", "ci", "sn",
    "ke", "tz", "ug", "zm", "zw", "mw", "bw", "na", "sz", "ls", "mg", "mu", "sc", "cv", "gw", "gq", "st", "ga", "cg", "cd",
    "ao", "cm", "ne", "bf", "ml", "td", "mr", "sl", "lr", "gm", "gn", "bj", "tg", "bi", "rw", "so", "dj", "er", "ss"
}


def read_file(file_name: str) -> List[str]:
    """
    读取文件内容。
    :param file_name: 文件路径
    :return: 文件的每一行组成的列表
    """
    with open(file_name, 'r', encoding='utf8') as f:
        return [line.strip() for line in f if line.strip()]


def write_file(file_name: str, lines: List[str]) -> None:
    """
    将处理后的内容写回文件。
    :param file_name: 文件路径
    :param lines: 要写入的内容列表
    """
    with open(file_name, 'w', encoding='utf8') as f:
        f.write("\n".join(lines) + "\n")


def filter_rules(lines: List[str]) -> List[str]:
    """
    过滤掉无效规则和指定的国家代码后缀。
    :param lines: 原始规则列表
    :return: 过滤后的规则列表
    """
    filtered_lines = []
    suffix_pattern = re.compile(rf"\.({'|'.join(COUNTRY_SUFFIXES)})\^$")  # 匹配以特定后缀结尾的规则

    for line in lines:
        # 移除注释和不符合规则的行
        if line.startswith('!') or line.startswith('['):
            continue
        # 移除带有特定国家代码后缀的域名规则
        if suffix_pattern.search(line):
            continue
        # 符合 Adblock 规则格式的行
        if re.match(r"^\|\|[^\^]+?\^$", line):
            filtered_lines.append(line)
    return filtered_lines


def remove_duplicates(lines: List[str]) -> List[str]:
    """
    去重规则。
    :param lines: 已过滤的规则列表
    :return: 去重后的规则列表
    """
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)
    return unique_lines


def extract_domain(rule: str) -> str:
    """
    提取规则中的域名部分。
    :param rule: Adblock 规则
    :return: 提取的域名
    """
    return rule.split("||")[-1].split("^")[0]


def sort_rules(lines: List[str]) -> List[str]:
    """
    按次级域名排序（忽略顶级域名）。
    - 忽略顶级域名（TLD），按次级域名进行排序。
    - 如果次级域名相同，则按完整域名排序。
    :param lines: 已过滤和去重的规则列表
    :return: 排序后的规则列表
    """
    def sorting_key(rule: str):
        domain = extract_domain(rule)
        parts = domain.split(".")
        # 次级域名部分（倒数第二部分）
        second_level_domain = parts[-2] if len(parts) > 1 else parts[0]
        return (second_level_domain, domain)

    return sorted(lines, key=sorting_key)


def add_header(file_name: str, rule_count: int) -> List[str]:
    """
    添加文件头部信息。
    :param file_name: 文件路径
    :param rule_count: 规则数量
    :return: 包含头部信息的列表
    """
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return [
        "! Title: Optimized Adblock Rules",
        "! Description: This is an optimized adblock filter list.",
        f"! Source file: {file_name}",
        f"! Version: {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        f"! Last Modified: {now}",
        f"! Total Rules: {rule_count}",
        "!",
    ]


def main():
    """
    主函数：处理规则文件。
    """
    if len(sys.argv) != 2:
        print("用法: python sort.py <文件路径>")
        sys.exit(1)

    file_name = sys.argv[1]
    # 读取文件
    lines = read_file(file_name)
    # 过滤规则
    filtered_lines = filter_rules(lines)
    # 去重规则
    unique_lines = remove_duplicates(filtered_lines)
    # 排序规则
    sorted_rules = sort_rules(unique_lines)
    # 添加头部信息
    header = add_header(file_name, len(sorted_rules))
    # 写入文件
    write_file(file_name, header + sorted_rules)
    print(f"文件 {file_name} 已成功优化，共处理 {len(sorted_rules)} 条规则。")


if __name__ == "__main__":
    main()
