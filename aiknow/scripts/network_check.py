import httpx, sys, time, socket

TARGETS = [
    ("GitHub API", "https://api.github.com"),
    ("GitHub Pages", "https://yxj325.github.io/aiknow"),
    ("PyPI 清华", "https://pypi.tuna.tsinghua.edu.cn/simple"),
    ("清华镜像", "https://mirrors.tuna.tsinghua.edu.cn"),
    ("华为云镜像", "https://mirrors.huaweicloud.com"),
]

def check(target):
    name, url = target
    try:
        start = time.time()
        r = httpx.get(url, follow_redirects=True, timeout=10)
        elapsed = round((time.time() - start) * 1000)
        size = len(r.content) // 1024
        status = "OK" if r.status_code < 400 else "WARN"
        print(f"  [{status}] {name:12s} {elapsed:4d}ms  ({r.status_code}, {size}KB)")
        return True
    except Exception as e:
        print(f"  [FAIL] {name:12s} - {str(e)[:50]}")
        return False

print("AI知库 网络诊断")
print("=" * 50)
ok = sum(1 for t in TARGETS if check(t))
print(f"\n{ok}/{len(TARGETS)} targets reachable")
if ok < len(TARGETS):
    print("部分地区需要配置镜像或代理")
