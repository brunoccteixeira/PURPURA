import os, sys, time

def _sanitize_sys_path():
    cwd = os.getcwd()
    sys.path = [p for p in sys.path if p not in ('', cwd)]
    bad_prefix = os.path.join(cwd, 'trino')
    sys.path = [p for p in sys.path if not p.startswith(bad_prefix)]

def connect():
    _sanitize_sys_path()
    import trino
    host  = os.getenv('TRINO_HOST', 'localhost')
    port  = int(os.getenv('TRINO_PORT', '8080'))
    user  = os.getenv('TRINO_USER', 'bruno')
    cat   = os.getenv('TRINO_CATALOG', 'lake')
    sch   = os.getenv('TRINO_SCHEMA', 'ifrs')
    return trino.dbapi.connect(host=host, port=port, user=user, catalog=cat, schema=sch)

def wait_ready(max_wait=180, sleep=1.0):
    last_err = None
    t0 = time.time()
    while time.time() - t0 < max_wait:
        try:
            cur = connect().cursor()
            cur.execute('SELECT 1')
            row = cur.fetchone()
            if row and row[0] == 1:
                return True
        except Exception as e:
            last_err = e
        time.sleep(sleep)
    raise RuntimeError(f'Trino not ready after {max_wait}s: {last_err}')
