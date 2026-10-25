#!/usr/bin/env python3
import hashlib,importlib.util,json,struct,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('transport',ROOT/'mk/aether-supervised.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def reject(fn):
 try:fn()
 except (ValueError,OSError,subprocess.CalledProcessError):return
 raise AssertionError('unexpected acceptance')
with tempfile.TemporaryDirectory() as t:
 d=Path(t);root=d/'root';root.mkdir(mode=0o700)
 subprocess.run(['make','-s','-f','mk/pkg.mk','ROOT='+str(root),'init-root'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 kernel=bytearray(64);kernel[:7]=b'\x7fELF\x02\x01\x01';struct.pack_into('<HH',kernel,16,2,62)
 data=[kernel,b'P',b'D',struct.pack('<8sIIQII',b'AELIFE01',1,1,0x400000,1,0)+b'L',b'S']
 paths=[]
 for i,raw in enumerate(data):p=d/str(i);p.write_bytes(raw);paths.append(p)
 subprocess.run(['sh',str(ROOT/'mk/aether-boot-v2.sh'),'stage',str(root),*[str(p) for p in paths],*[m.digest(p) for p in paths],m.digest(paths[0])],check=True,stdout=subprocess.DEVNULL)
 base=m.digest(root/'aether-boot-v2/receipt.kv');native=d/'native'
 native.write_bytes(struct.pack('<8sII',b'AENSUP01',64,1)+bytes(32)+kernel+b'S');pin=m.digest(native)
 reject(lambda:m.stage(root,base,native,'0'*64));assert not (root/'aether-supervised-v1').exists()
 saved=native.read_bytes();native.write_bytes(saved+b'x');reject(lambda:m.stage(root,base,native,m.digest(native)));native.write_bytes(saved)
 receipt=m.stage(root,base,native,pin);bundle=root/'aether-supervised-v1';m.verify(bundle,receipt)
 reject(lambda:m.stage(root,base,native,pin));reject(lambda:m.verify(bundle,'0'*64))
 payload=bundle/'native-c.bin';payload.write_bytes(saved+b'x');reject(lambda:m.verify(bundle,receipt));payload.write_bytes(saved)
 (bundle/'extra').write_text('x');reject(lambda:m.verify(bundle,receipt));(bundle/'extra').unlink()
 payload.unlink();payload.symlink_to(native);reject(lambda:m.verify(bundle,receipt));payload.unlink();payload.write_bytes(saved)
 m.verify(bundle,receipt)
 print('PASS: supervised transport and seven rejection cases')

 # Memory uses an explicit profile; legacy envelopes/receipts do not opt in.
 reject(lambda:m.stage(root,base,native,pin,memory=True))
 memory_raw=b'AENFD001'+saved[8:];native.write_bytes(memory_raw)
 memory_pin=m.digest(native)
 reject(lambda:m.envelope(native))
 memory_receipt=m.stage(root,base,native,memory_pin,memory=True)
 memory_bundle=root/'aether-memory-v1';m.verify(memory_bundle,memory_receipt)
 reject(lambda:m.stage(root,base,native,memory_pin,memory=True))
 metadata=memory_bundle/'receipt.json';original=metadata.read_bytes()
 for options in ({'native-memory':False,'smp':False},{'native-memory':True,'smp':True}):
  obj=json.loads(original);obj['required_kernel_options']=options
  metadata.write_text(json.dumps(obj));reject(lambda:m.verify(memory_bundle,m.digest(metadata)))
 obj=json.loads(original);del obj['required_kernel_options']
 metadata.write_text(json.dumps(obj));reject(lambda:m.verify(memory_bundle,m.digest(metadata)))
 metadata.write_bytes(original)
 payload=memory_bundle/'native-c.bin';payload.write_bytes(saved)
 reject(lambda:m.verify(memory_bundle,memory_receipt))
 payload.write_bytes(memory_raw);m.verify(memory_bundle,memory_receipt)
 print('PASS: explicit native-memory transport and seven profile rejection cases')
 # New dual-image profiles must not be accepted by older single-image readers.
 for profile,magic in (('launch',b'AENEX001'),('channel',b'AENCH001'),('files',b'AENFS001'),('process',b'AENFS001'),('coexist',b'AENCO001'),('coexist-small-pool',b'AENCO001'),('files-writable',b'AENFS001'),('files-writable-memory',b'AENFS001')):
  raw=struct.pack('<8sIIII',magic,64,64,1,0)+bytes(32)+kernel+kernel+b'S'
  native.write_bytes(raw)
  reject(lambda:m.envelope(native))
  reject(lambda:m.envelope(native,b'AENFD001'))
  malformed=[raw[:55],raw+b'x',raw[:-1]]
  for offset,value in ((8,0),(12,63),(16,4097),(20,1)):
   bad=bytearray(raw);struct.pack_into('<I',bad,offset,value);malformed.append(bytes(bad))
  for offset in (56,120):
   bad=bytearray(raw);bad[offset+18]=3;malformed.append(bytes(bad))
  for bad in malformed:
   native.write_bytes(bad);reject(lambda:m.envelope(native,magic))
  native.write_bytes(raw);dual_pin=m.digest(native)
  (root/'.replacement').mkdir()
  reject(lambda:m.stage(root,base,native,dual_pin,profile=profile))
  assert not (root/('aether-'+profile+'-v1')).exists()
  (root/'.replacement').rmdir()
  dual_receipt=m.stage(root,base,native,dual_pin,profile=profile)
  dual=root/('aether-'+profile+'-v1');m.verify(dual,dual_receipt)
  reject(lambda:m.stage(root,base,native,dual_pin,profile=profile))
  metadata=dual/'receipt.json';original=metadata.read_bytes()
  required_memory=profile=='files-writable-memory'
  for options in ({'smp':True,'native-memory':required_memory},{'smp':False,'native-memory':not required_memory},{'smp':0,'native-memory':required_memory},{}):
   obj=json.loads(original);obj['required_kernel_options']=options
   metadata.write_text(json.dumps(obj));reject(lambda:m.verify(dual,m.digest(metadata)))
  obj=json.loads(original);obj['format']='aether-'+('channel' if profile=='launch' else 'launch')+'-transport-v1'
  metadata.write_text(json.dumps(obj));reject(lambda:m.verify(dual,m.digest(metadata)))
  metadata.write_bytes(original);m.verify(dual,dual_receipt)
 print('PASS: launch/channel/files dual-image profiles, lengths, both ELF identities, options, pending guard and cross-profile rejection')

 # The shared envelope magic cannot establish the compiled service mode.
 metadata=root/'aether-files-writable-v1/receipt.json';original=metadata.read_bytes()
 for mode in (None,True,'read-only','persistent'):
  obj=json.loads(original)
  if mode is None:del obj['service_mode']
  else:obj['service_mode']=mode
  metadata.write_text(json.dumps(obj));reject(lambda:m.verify(metadata.parent,m.digest(metadata)))
 obj=json.loads(original);obj['format']='aether-files-transport-v1'
 metadata.write_text(json.dumps(obj));reject(lambda:m.verify(metadata.parent,m.digest(metadata)))
 metadata.write_bytes(original);m.verify(metadata.parent,m.digest(metadata))
 print('PASS: explicit volatile-scratch mode and relabel rejection')

 metadata=root/'aether-files-writable-memory-v1/receipt.json';original=metadata.read_bytes()
 obj=json.loads(original);obj['required_kernel_options']['native-memory']=1
 metadata.write_text(json.dumps(obj));reject(lambda:m.verify(metadata.parent,m.digest(metadata)))
 obj=json.loads(original);obj['format']='aether-files-writable-transport-v1'
 metadata.write_text(json.dumps(obj));reject(lambda:m.verify(metadata.parent,m.digest(metadata)))
 metadata.write_bytes(original);m.verify(metadata.parent,m.digest(metadata))
 print('PASS: memory-enabled writable profile rejects integer options and legacy relabeling')

 metadata=root/'aether-coexist-small-pool-v1/receipt.json';original=metadata.read_bytes()
 for flag in (False,1,None):
  obj=json.loads(original)
  if flag is None:del obj['required_kernel_options']['native-coexist-small-pool']
  else:obj['required_kernel_options']['native-coexist-small-pool']=flag
  metadata.write_text(json.dumps(obj));reject(lambda:m.verify(metadata.parent,m.digest(metadata)))
 obj=json.loads(original);obj['format']='aether-coexist-transport-v1'
 metadata.write_text(json.dumps(obj));reject(lambda:m.verify(metadata.parent,m.digest(metadata)))
 metadata.write_bytes(original);m.verify(metadata.parent,m.digest(metadata))
 print('PASS: coexist pool mode, exact boolean and relabel rejection')

 # ABI 9 is an explicit 80-byte/three-image envelope; inspect every ELF.
 raw=struct.pack('<8s6I',b'AENMX001',64,64,64,1,0,0)+bytes(48)+kernel*3+b'S'
 for profile in ('connections','connections-small-pool'):
  native.write_bytes(raw);receipt=m.stage(root,base,native,m.digest(native),profile=profile)
  bundle=root/('aether-'+profile+'-v1');m.verify(bundle,receipt)
  reject(lambda:m.envelope(native,b'AENCO001'))
  reject(lambda:m.stage(root,base,native,m.digest(native),profile=profile))
  for offset,value in ((8,63),(12,1048577),(16,0),(20,8193),(24,1),(28,1)):
   bad=bytearray(raw);struct.pack_into('<I',bad,offset,value);native.write_bytes(bad);reject(lambda:m.envelope(native,b'AENMX001'))
  for offset in (80,144,208):
   bad=bytearray(raw);struct.pack_into('<H',bad,offset+18,183);native.write_bytes(bad);reject(lambda:m.envelope(native,b'AENMX001'))
  for bad in (raw[:79],raw[:-1],raw+b'x'):
   native.write_bytes(bad);reject(lambda:m.envelope(native,b'AENMX001'))
  native.write_bytes(raw)
  meta=bundle/'receipt.json';saved_meta=meta.read_bytes()
  for flag in (None,1,profile!='connections-small-pool'):
   obj=json.loads(saved_meta)
   if flag is None:del obj['required_kernel_options']['native-coexist-small-pool']
   else:obj['required_kernel_options']['native-coexist-small-pool']=flag
   meta.write_text(json.dumps(obj));reject(lambda:m.verify(bundle,m.digest(meta)))
  meta.write_bytes(saved_meta);m.verify(bundle,receipt)
 print('PASS: ABI-9 three-image bounds, both reserved words, all ELF identities and pool options')

 for size in (4097,8192):
  native.write_bytes(struct.pack('<8s6I',b'AENMX001',64,64,64,size,0,0)+bytes(48)+kernel*3+b'S'*size)
  m.envelope(native,b'AENMX001')
 native.write_bytes(struct.pack('<8s6I',b'AENMX001',64,64,64,8193,0,0)+bytes(48)+kernel*3+b'S'*8193)
 reject(lambda:m.envelope(native,b'AENMX001'))
 print('PASS: owner ABI-9 two-page bound accepts 4097/8192 and rejects 8193 bytes')
