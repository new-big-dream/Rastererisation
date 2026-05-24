def lire(file_name):
    res = [[], []]
    
    for line in open(file_name):
        parts = line.split()
        if len(parts) >= 4:
            if parts[0] == 'v':
                res[0].append([float(_) for _ in parts[1:4]])
            if parts[0] == 'f':
                res[1].append([int(v.split('/')[0]) for v in parts[1:4]])
    return res

#il s'agit du Model

def lire_plus(file_name):
    res = [[], [], [], []]
    
    for line in open(file_name):
        parts = line.split()
        if len(parts) >= 4:
            if parts[0] == 'v':
                res[0].append([float(_) for _ in parts[1:4]])
            if parts[0] == 'f':
                res[1].append([[int(v.split('/')[0]), int(v.split('/')[-1])] for v in parts[1:4]]) #coords of (ax,ay,az), (n1,n2,n3)
            if parts[0] == 'vn':
                res[2].append([float(_) for _ in parts[1:4]])
            if parts[0] == 'vt':
                res[3].append([float(_) for _ in parts[1:4]])
    return res

def lire_final(file_name):
    res = [[], [], [], []]
    
    for line in open(file_name):
        parts = line.split()
        if not parts: 
            continue
        if len(parts) >= 4:
            if parts[0] == 'f':
                res[0].append([[int(v.split('/')[0]), int(v.split('/')[1]), int(v.split('/')[2])] for v in parts[1:4]]) #coords of (ax,ay,az), (uvx,uvy), (n1,n2,n3) 
            if parts[0] == 'v':
                res[1].append([float(_) for _ in parts[1:4]])
            if parts[0] == 'vn':
                res[3].append([float(_) for _ in parts[1:4]])
        if len(parts) >= 3:
            if parts[0] == 'vt':
                res[2].append([float(_) for _ in parts[1:4]])
    return res