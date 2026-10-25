"""Independent, deliberately narrower host adoption of Distribution SV-01–03."""
import hashlib
import json
from pathlib import Path
import re
from .runtime import Command, HostRuntime
from prototypes.runtime_model.model import Service, Model, Rejected

FIELDS = set('schema id package executable_sha256 target argv environment kind requires after readiness restart authority_requests'.split())
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z')
ENV = re.compile(r'[A-Za-z_][A-Za-z0-9_]*\Z')

def require(ok, reason):
    if not ok: raise Rejected(reason)

def pairs(items):
    result={}
    for k,v in items:
        require(k not in result,'duplicate descriptor key')
        result[k]=v
    return result

def text(value):
    try: return isinstance(value,str) and '\0' not in value and len(value.encode('utf-8'))<=4096
    except UnicodeError: return False

def parse(raw):
    require(isinstance(raw,bytes) and 0<len(raw)<=65536,'descriptor size')
    try:
        d=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=lambda _: require(False,'nonfinite JSON'))
    except (ValueError,UnicodeError,RecursionError) as e:
        raise Rejected('invalid descriptor JSON') from e
    require(isinstance(d,dict) and set(d)==FIELDS,'descriptor fields')
    require(d['schema']=='aether-service-experiment-v1','descriptor version')
    require(all(isinstance(d[k],str) and ID.fullmatch(d[k]) for k in ('id','package','target')),'identity')
    require(d['target']=='host-posix-experiment-v1','unsupported target')
    require(isinstance(d['executable_sha256'],str) and re.fullmatch('[0-9a-f]{64}',d['executable_sha256']),'digest')
    require(isinstance(d['argv'],list) and 1<=len(d['argv'])<=16 and all(text(a) for a in d['argv']) and bool(d['argv'][0]),'argv')
    env=d['environment']
    require(isinstance(env,dict) and len(env)<=16 and all(ENV.fullmatch(k) and text(v) for k,v in env.items()),'environment')
    require(d['kind'] in ('long-running','oneshot'),'kind')
    require(d['readiness'] in (('completed',) if d['kind']=='oneshot' else ('started','notified-ready')),'readiness')
    req=d['requires']; after=d['after']
    require(isinstance(req,dict) and len(req)<=64 and all(ID.fullmatch(k) and v in ('started','notified-ready','completed') for k,v in req.items()),'requires')
    require(isinstance(after,list) and len(after)<=64 and all(isinstance(k,str) and ID.fullmatch(k) for k in after) and len(set(after))==len(after),'after')
    # This adapter has no authority broker. Reject every request instead of pretending to grant it.
    require(d['authority_requests']==[],'host authority requests unsupported')
    retry=d['restart']
    require(isinstance(retry,dict) and set(retry)=={'mode','retries','delay_ms'},'restart fields')
    require(retry['mode'] in ('never','on-failure'),'restart mode')
    require(type(retry['retries']) is int and 0<=retry['retries']<=2 and type(retry['delay_ms']) is int and 1<=retry['delay_ms']<=60000,'host retry bounds')
    require(retry['mode']!='never' or retry['retries']==0,'never retries')
    require(d['kind']!='oneshot' or retry['mode']=='never','oneshot retries')
    service=Service(d['id'],kind='oneshot' if d['kind']=='oneshot' else 'daemon',milestone=d['readiness'],requires=tuple(req.items()),after=tuple(after),retries=retry['retries'],delay=retry['delay_ms'],startup=1000,stop=1000,cleanup=1000)
    command=Command(tuple(d['argv']),d['executable_sha256'],tuple(env.items()))
    # Model validates the narrower service identifiers and combined graph during preparation.
    return service,command

class Prepared:
    """Caller-held content pins; no package authenticity or hostile-filesystem guarantee."""
    def __init__(self, paths):
        require(isinstance(paths,(tuple,list)) and 1<=len(paths)<=8,'host graph size')
        self.inputs=[]; services=[]; commands={}
        for path in paths:
            path=Path(path).resolve(strict=True)
            with path.open('rb') as f: raw=f.read(65537)
            service,command=parse(raw)
            require(service.name not in commands,'duplicate service')
            self.inputs.append((path,hashlib.sha256(raw).hexdigest()))
            services.append(service); commands[service.name]=command
            HostRuntime._validate(command)
        Model(services)  # Entire graph validated before any process can launch.
        self.services=tuple(services); self.commands=commands

    def activate(self, *, cwd):
        for path,pin in self.inputs:
            with path.open('rb') as f: raw=f.read(65537)
            require(hashlib.sha256(raw).hexdigest()==pin,'stale prepared descriptor')
        return HostRuntime(self.services,self.commands,cwd=cwd)
