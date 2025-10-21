

def read_config(filename):
    config = {}
    with open(f'ignore_file\\{filename}', 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config