#!/bin/bash

# 切换到脚本所在目录
cd $(cd "$(dirname "$0")";pwd)

# 定义规则源的URL列表并下载规则文件，合并保存到 dns.txt 中
urls=(
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/ultimate.mini.txt"
    "https://raw.githubusercontent.com/YujiaCheng1996/adblockfilters/main/rules/adblockdnslite.txt"
    "https://raw.githubusercontent.com/ghvjjjj/adblockfilters/refs/heads/main/rules/adblockdnslite.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.xiaomi.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.oppo-realme.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.vivo.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.roku.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.lgwebos.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.tiktok.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.samsung.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.winoffice.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.amazon.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.apple.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/dyndns.txt"
    "https://raw.githubusercontent.com/hagezi/dns-blocklists/refs/heads/main/adblock/native.huawei.txt"
)

for url in "${urls[@]}"; do
    curl -sSL "$url" >> dns.txt
done

# 添加自定义规则
cat ../rules/myrules.txt >> dns.txt

# 修复换行符，统一格式
sed -i 's/\r//' dns.txt

# 去重并排序规则
#python sort.py dns.txt 

# 下载 oisd 白名单
#curl -s https://oisd.nl/excludes.php | grep -o '<a href=[^>]*>[^<]*' | sed 's/.*>//' | sort -u > oisd.txt

# 使用 hostlist-compiler 优化生成的规则
#hostlist-compiler -c dns.json -o dns-output.txt

# 提取仅包含黑名单规则的行到 dns.txt
#cat dns-output.txt | grep -P "^\|\|.*\^$" > dns.txt

# 再次排序规则
python sort.py dns.txt 

# 处理并生成纯域名列表文件
cat dns.txt | grep -vE '(@|\*)' | grep -Po "(?<=\|\|).+(?=\^)" | grep -v "\*" > ./domain.txt
cat domain.txt | sed "s/^/\+\./g" >> ./domainset.txt

# 下载 Mihomo 工具的最新版本并解压
wget -O version.txt https://github.com/MetaCubeX/mihomo/releases/download/Prerelease-Alpha/version.txt
version=$(cat version.txt)
wget "https://github.com/MetaCubeX/mihomo/releases/download/Prerelease-Alpha/mihomo-linux-amd64-$version.gz"
gzip -d "mihomo-linux-amd64-$version.gz"
chmod +x "mihomo-linux-amd64-$version"

# 使用 Mihomo 工具将规则集转换为指定格式
./"mihomo-linux-amd64-$version" convert-ruleset domain text domainset.txt anti-ad.mrs

# 移动生成的规则文件
mv dns.txt anti-ad.mrs ../rules/

# 清理缓存文件
rm -rf ./*.txt
rm "mihomo-linux-amd64-$version"
