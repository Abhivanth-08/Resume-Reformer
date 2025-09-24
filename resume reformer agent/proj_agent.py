import json

def space(st,l):
    try:
        ind=st.find(" ",l)
        return st[:ind],ind
    except:
        return st,l

def find_largest_common_substring(source: str, target: str):
    source = source.lower()
    target = target.lower()
    m = len(source)
    n = len(target)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    length = 0
    end_pos = 0

    for i in range(m):
        for j in range(n):
            if source[i] == target[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
                if dp[i + 1][j + 1] > length:
                    length = dp[i + 1][j + 1]
                    end_pos = j + 1

    if length == 0:
        return -1, -1, ""

    start = end_pos - length
    return start, end_pos, target[start:end_pos]


def proj_create(old, proj, projupd, old2):
    with open(old) as a, open(proj) as b, open(projupd) as c:
        a = json.dumps(json.load(a))  # convert back to JSON-formatted string
        b = json.load(b)
        c = json.load(c)

    md1 = {}
    md2 = {}
    for i in range(len(b)):
        try:
            if c[i]['title'] not in a:
                md1[b[i]['title']] = c[i]['title']
                md2[b[i]['description'].split('Technologies')[0]] = c[i]['description'].split('Technologies')[0]
                md2[b[i]['description'].split('Technologies')[1]] = c[i]['description'].split('Technologies')[1]
        except Exception as e:
            print(f"Skipping index {i} due to error: {e}")

    for i in md1:
        start, end, match = find_largest_common_substring(i, a)
        if start != -1:
            print(f"Replacing {a[start:end]} with {md1[i]}")
            a = a.replace(a[start:end], md1[i])

    while len(md2) != 0:
        keys = list(md2.keys())
        for i in keys:
            start, end, match = find_largest_common_substring(i, a)
            if start != -1 and a[start:end] not in [".", " "]:
                print(f"Replacing {a[start:end]} with {space(md2[i],len(a[start:end]))[0]}")
                a = a.replace(a[start:end], md2[i][:len(a[start:end])])
                new_key = i[len(a[start:end]):]
                new_value = md2[i][space(md2[i],len(a[start:end]))[1]:]
                if new_key and new_value:
                    md2[new_key] = new_value
            md2.pop(i)

    k = json.loads(a)
    with open(old2, "w") as d:
        json.dump(k, d, indent=2)


proj_create("old_det.json","projects.json","projects_upd.json","n1.json")

