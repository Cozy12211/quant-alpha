#!/usr/bin/env python3
"""实时行情抓取模块 - 新浪/腾讯公开API"""
import urllib.request
import re

def get_sina_quote(symbol):
    """从新浪获取A股实时行情"""
    # symbol: 603650 → sh603650
    prefix = "sh" if symbol.startswith("6") else "sz"
    code = prefix + symbol
    
    try:
        url = f"https://hq.sinajs.cn/list={code}"
        req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode('gbk')
            
        # 解析: var hq_str_sh603650="彤程新材,94.820,97.710,89.080,..."
        match = re.search(r'"([^"]*)"', data)
        if not match:
            return None
            
        parts = match.group(1).split(',')
        if len(parts) < 33:
            return None
            
        return {
            "name": parts[0],
            "symbol": symbol,
            "open": float(parts[1]),
            "pre_close": float(parts[2]),
            "price": float(parts[3]),
            "high": float(parts[4]),
            "low": float(parts[5]),
            "volume": int(parts[8]),
            "amount": float(parts[9]),
            "date": parts[30],
            "time": parts[31],
            "source": "sina"
        }
    except Exception as e:
        print(f"[Quote] 新浪API错误: {e}")
        return None

def get_tencent_quote(symbol):
    """从腾讯获取A股实时行情（备用）"""
    prefix = "sh" if symbol.startswith("6") else "sz"
    code = prefix + symbol
    
    try:
        url = f"https://qt.gtimg.cn/q={code}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode('gbk')
            
        # v_sh603650="1~彤程新材~603650~89.08~97.71~..."
        match = re.search(r'"([^"]*)"', data)
        if not match:
            return None
            
        parts = match.group(1).split('~')
        if len(parts) < 35:
            return None
            
        return {
            "name": parts[1],
            "symbol": symbol,
            "price": float(parts[3]),
            "pre_close": float(parts[4]),
            "open": float(parts[5]),
            "high": float(parts[33]),
            "low": float(parts[34]),
            "volume": int(parts[6]),
            "source": "tencent"
        }
    except Exception as e:
        print(f"[Quote] 腾讯API错误: {e}")
        return None

def get_quote(symbol):
    """获取实时行情，优先新浪，失败用腾讯"""
    result = get_sina_quote(symbol)
    if result:
        return result
    return get_tencent_quote(symbol)

if __name__ == "__main__":
    import json
    q = get_quote("603650")
    print(json.dumps(q, ensure_ascii=False, indent=2))
