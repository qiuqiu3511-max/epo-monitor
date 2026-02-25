import requests
from bs4 import BeautifulSoup
import json
import os

# 配置：关注的 IPC 分类号
TARGET_IPCS = ['A61K', 'C12N', 'C07K', 'C12Q', 'A61P']
URL = "https://www.epo.org/en/case-law-appeals/decisions/recent?year=2026&items_per_page=100&page=0"
DB_FILE = 'seen_decisions.json'

def get_latest_decisions():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有决策条目（根据 EPO 2026 页面结构调整）
    decisions = []
    # 假设每个决策都在一个特定的 class 容器中，这里以表格行为例
    rows = soup.find_all('tr')[1:] # 跳过表头
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5: continue
        
        case_id = cols[0].get_text(strip=True) # 案件号
        ipc_text = cols[4].get_text(strip=True) # IPC 分类列
        pdf_link = row.find('a', href=True)['href']
        
        # 检查是否包含关注的 IPC
        if any(ipc in ipc_text for ipc in TARGET_IPCS):
            decisions.append({
                'id': case_id,
                'ipc': ipc_text,
                'link': f"https://www.epo.org{pdf_link}" if not pdf_link.startswith('http') else pdf_link
            })
    return decisions

def main():
    # 1. 加载已记录的案件
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            seen = json.load(f)
    else:
        seen = []

    # 2. 获取最新案件
    current_decisions = get_latest_decisions()
    
    # 3. 对比，找出新案件
    new_findings = [d for d in current_decisions if d['id'] not in seen]
    
    if new_findings:
        print(f"发现 {len(new_findings)} 个新决定！")
        for item in new_findings:
            print(f"[{item['id']}] 分类: {item['ipc']} | 链接: {item['link']}")
        
        # 更新数据库
        seen.extend([d['id'] for d in new_findings])
        with open(DB_FILE, 'w') as f:
            json.dump(seen, f)
        
        # 如果需要发通知（如 Telegram/微信），可以在这里调用 webhook
    else:
        print("没有发现新变动。")

if __name__ == "__main__":
    main()
