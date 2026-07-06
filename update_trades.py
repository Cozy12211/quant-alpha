#!/usr/bin/env python3
"""
Quant Alpha - 交易数据更新脚本
用法: python update_trades.py [最新价]
如果没有参数，自动从腾讯API获取
"""

import json
import sys
import urllib.request
import re
from datetime import datetime

# ============ 配置 ============
HTML_PATH = "/Users/cozy/Desktop/交易日志.html"
BACKUP_HTML_PATH = "/Users/cozy/projects/quant-alpha/trade-log.html"
STOCK_CODE = "sh603650"  # 彤程新材
COST_PRICE = 90.721
SHARES = 3000
DRAWDOWN_LINE = 227316
INITIAL_ASSET = 252573.93

# ============ 获取行情 ============
def fetch_quote():
    """从腾讯API获取实时行情"""
    try:
        url = f"https://qt.gtimg.cn/q={STOCK_CODE}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode('gbk')
            
        # 解析: v_sh603650="1~彤程新材~603650~83.69~..."
        match = re.search(rf'v_{STOCK_CODE}="([^"]+)"', data)
        if match:
            parts = match[1].split('~')
            price = float(parts[3])
            name = parts[1]
            return price, name
    except Exception as e:
        print(f"API获取失败: {e}")
    return None, None

# ============ 计算 ============
def calc_metrics(current_price):
    """计算所有指标"""
    market_value = SHARES * current_price
    total_pnl = market_value - (SHARES * COST_PRICE)
    total_pnl_pct = (total_pnl / (SHARES * COST_PRICE)) * 100
    total_asset = INITIAL_ASSET + total_pnl - (-21093.03)  # 基于初始的浮动盈亏调整
    
    # 简单起见，直接用比例计算
    total_asset = 252573.93 + (current_price - 83.69) * SHARES
    
    return {
        "current_price": round(current_price, 2),
        "market_value": round(market_value, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "total_asset": round(total_asset, 2),
        "distance_to_drawdown": round(total_asset - DRAWDOWN_LINE, 2)
    }

# ============ 更新HTML ============
def update_html(price, metrics):
    """更新HTML文件中的数据"""
    
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 更新最新价
    content = re.sub(
        r'(<div class="value red" id="alert-price">)[\d.]+(</div>)',
        f'\\g<1>{metrics["current_price"]}\\g<2>',
        content
    )
    
    # 2. 更新浮动盈亏
    pnl_sign = '+' if metrics['total_pnl_pct'] >= 0 else ''
    pnl_class = 'green' if metrics['total_pnl_pct'] >= 0 else 'red'
    content = re.sub(
        r'(<div class="value [^"]*" id="alert-pnl">)[^<]+(</div>)',
        f'<div class="value {pnl_class}" id="alert-pnl">{pnl_sign}{metrics["total_pnl_pct"]}%</div>',
        content
    )
    
    # 3. 更新数据时间戳
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    content = re.sub(
        r'(📅 收盘数据: )[\d-]+ \d{2}:\d{2}',
        f'\\g<1>{now}',
        content
    )
    
    # 4. 更新预载数据中的价格
    content = re.sub(
        r'(current: )[\d.]+',
        f'\\g<1>{metrics["current_price"]}',
        content
    )
    
    # 4b. 更新 reason 文本中的价格
    content = re.sub(
        r'(当前价)[\d.]+',
        f'\\g<1>{metrics["current_price"]}',
        content
    )
    content = re.sub(
        r'(浮亏)[-+\d.]+%',
        f'\\g<1>{metrics["total_pnl_pct"]}%',
        content
    )
    
    # 5. 更新统计面板中的盈亏
    content = re.sub(
        r'(<div class="stat-value [^"]*" id="stat-pnl">)[^<]+(</div>)',
        f'<div class="stat-value {pnl_class}" id="stat-pnl">{pnl_sign}{metrics["total_pnl_pct"]}%</div>',
        content
    )
    
    # 保存
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 同步备份
    with open(BACKUP_HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 清除浏览器缓存，确保下次打开加载新数据
    print("  🧹 清除浏览器 localStorage 缓存...")
    # 创建一个清除缓存的标记文件
    clear_flag = HTML_PATH.replace('.html', '-clear-cache.html')
    with open(clear_flag, 'w', encoding='utf-8') as f:
        f.write('''<script>
localStorage.removeItem('quant-alpha-trades');
localStorage.removeItem('quant-alpha-last-direction');
localStorage.removeItem('quant-alpha-mode');
alert('缓存已清除，请关闭此页面并重新打开交易日志.html');
window.close();
</script>''')
    
    print(f"  ✅ HTML已更新: {HTML_PATH}")
    print(f"  ⚠️  请打开以下文件清除缓存: {clear_flag}")

# ============ 主函数 ============
def main():
    print("=" * 50)
    print("Quant Alpha - 交易数据更新")
    print("=" * 50)
    
    # 获取价格
    if len(sys.argv) > 1:
        price = float(sys.argv[1])
        print(f"使用手动输入价格: {price}")
    else:
        print("正在从腾讯API获取行情...")
        price, name = fetch_quote()
        if price:
            print(f"✅ 获取成功: {name} = {price}")
        else:
            print("❌ API获取失败")
            price = float(input("请手动输入最新价: "))
    
    # 计算指标
    metrics = calc_metrics(price)
    
    print("\n更新指标:")
    print(f"  最新价: {metrics['current_price']}")
    print(f"  市值: {metrics['market_value']:,.2f}")
    print(f"  浮动盈亏: {metrics['total_pnl']:,.2f} ({metrics['total_pnl_pct']}%)")
    print(f"  总资产: {metrics['total_asset']:,.2f}")
    print(f"  距离回撤线: {metrics['distance_to_drawdown']:,.2f}")
    
    # 检查是否触发回撤线
    if metrics['total_asset'] < DRAWDOWN_LINE:
        print("\n🚨🚨🚨 触发回撤线! 请立即执行止损! 🚨🚨🚨")
    
    # 更新HTML
    update_html(price, metrics)
    
    print("\n✅ 完成! 请刷新浏览器查看更新。")

if __name__ == '__main__':
    main()
