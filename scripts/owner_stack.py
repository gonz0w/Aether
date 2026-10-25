# SPDX-License-Identifier: BSD-2-Clause
"""Conservative direct-call x86_64 owner stack inspection, not a formal proof."""
import re
import struct


class StackLimit(ValueError):
    def __init__(self, observation):
        self.observation = observation
        super().__init__('owner conservative stack exceeds' + str(observation['usable_stack_bytes']) + ': ' + str(observation['entry_stack_bytes']))


def inspect(disassembly, elf=None, *, stack_bytes=4096):
    if type(stack_bytes) is not int or stack_bytes not in (4096, 8192):
        raise ValueError('unknown owner stack profile')
    usable = stack_bytes - 8
    spans = None
    loads = []
    constant_edges = 0
    if elf is not None:
        raw = elf.read_bytes()
        if raw[:6] != b'\x7fELF\x02\x01':
            raise ValueError('stack inspection requires ELF64 little endian')
        program = struct.unpack_from('<Q', raw, 32)[0]
        step, entries = struct.unpack_from('<HH', raw, 54)
        if step != 56 or program + step * entries > len(raw):
            raise ValueError('stack inspection program bounds')
        for i in range(entries):
            kind, flags, at, address, _, size, memory, _ = struct.unpack_from('<IIQQQQQQ', raw, program + i * step)
            if kind == 1:
                if at + size > len(raw) or memory < size:
                    raise ValueError('stack inspection load bounds')
                loads.append((address, size, at, flags, memory))
        offset = struct.unpack_from('<Q', raw, 40)[0]
        stride, count = struct.unpack_from('<HH', raw, 58)
        if stride != 64 or offset + count * stride > len(raw):
            raise ValueError('stack inspection section bounds')
        spans = {}
        for i in range(count):
            section = struct.unpack_from('<IIQQQQIIQQ', raw, offset + i * stride)
            if section[1] != 2:
                continue
            start, size, entry = section[4], section[5], section[9]
            if entry != 24 or size % entry or start + size > len(raw):
                raise ValueError('stack inspection symbol bounds')
            for at in range(start, start + size, entry):
                _, kind, _, _, address, length = struct.unpack_from('<IBBHQQ', raw, at)
                if kind & 15 == 2 and address != 0 and length != 0:
                    spans[address] = length
    def readonly(address, size):
        matches = [(base, at) for base, length, at, flags, _ in loads
                   if flags == 5 and base <= address and address + size <= base + length]
        if len(matches) != 1:
            raise ValueError('unverified readonly owner constant')
        base, at = matches[0]
        # Reject any writable alias covering even part of the observed bytes.
        if any(flags & 2 and address < base + memory and base < address + size
               for base, _, _, flags, memory in loads):
            raise ValueError('writable owner constant alias')
        return raw[at + address - base:at + address - base + size]
    functions = {}
    current = None
    for line in disassembly.splitlines():
        header = re.fullmatch(r'([0-9a-f]+) <(.+)>:', line.strip())
        if header:
            current = int(header[1], 16)
            if spans is not None and current not in spans:
                current = None
                continue
            functions[current] = {'name': header[2], 'local': 128, 'edges': []}
            continue
        instruction = re.match(r'\s*([0-9a-f]+):\s+([a-z][a-z0-9]*)\s*(.*)', line)
        if current is None or instruction is None:
            continue
        at, op, args = instruction.groups()
        if spans is not None and int(at, 16) >= current + spans[current]:
            continue
        function = functions[current]
        if op in ('push', 'pushf', 'pushfd', 'pushfq'):
            function['local'] += 8
        elif op in ('enter', 'leave'):
            raise ValueError('unsupported implicit stack adjustment')
        elif op == 'xchg' and re.search(r'(?:^|,\s*)(?:rsp|esp|sp|spl)(?:\s*,|\s*$)', args):
            raise ValueError('dynamic stack exchange')
        elif re.match(r'(?:esp|sp|spl)\s*,', args):
            raise ValueError('partial stack pointer adjustment')
        elif op == 'sub' and args.startswith('rsp, '):
            amount = args[5:].strip()
            if re.fullmatch(r'(0x[0-9a-f]+|[0-9]+)', amount) is None:
                raise ValueError('dynamic stack adjustment')
            function['local'] += int(amount, 0)
        elif op == 'pop' and args == 'rsp':
            raise ValueError('dynamic stack pointer restore')
        elif op == 'call' or op.startswith('j') or op.startswith('loop'):
            target = re.match(r'(?:0x)?([0-9a-f]+)\s+<', args)
            if target:
                function['edges'].append((int(target[1], 16), 8 if op == 'call' else 0))
            elif elf is not None and op in ('call', 'jmp') and args.startswith('qword ptr [rip '):
                # Resolve only an actual FF15/FF25 six-byte RIP-relative indirect
                # edge through an immutable file-backed pointer. Ignore tool
                # comments, reject registers/tables/writable or unknown targets.
                address = int(at, 16)
                instruction_bytes = readonly(address, 6)
                if instruction_bytes[:2] != (b'\xff\x15' if op == 'call' else b'\xff\x25'):
                    raise ValueError('owner constant edge instruction mismatch')
                pointer = address + 6 + struct.unpack('<i', instruction_bytes[2:])[0]
                resolved = struct.unpack('<Q', readonly(pointer, 8))[0]
                if resolved not in spans:
                    raise ValueError('owner constant edge target')
                function['edges'].append((resolved, 8 if op == 'call' else 0))
                constant_edges += 1
            elif op == 'call' or not re.match(r'(?:0x)?[0-9a-f]+\s*$', args):
                raise ValueError('unknown/indirect call or tail edge: '+args)
        elif re.match(r'rsp\s*,', args):
            if not (op == 'add' and re.fullmatch(r'rsp, (0x[0-9a-f]+|[0-9]+)', args)
                    and int(args.split(',')[1].strip(), 0) <= usable):
                raise ValueError('unknown stack adjustment: '+op+' '+args)
    if not functions or 0x400000 not in functions:
        raise ValueError('missing owner entry')
    memo = {}
    def depth(address, seen):
        if address in seen:
            raise ValueError('recursive owner call graph')
        if address not in functions:
            raise ValueError('unknown owner call target')
        if address in memo:
            return memo[address]
        function = functions[address]
        following = 0
        for target, extra in function['edges']:
            if target not in functions:
                # In-function local jumps have no extra stack edge.
                if extra == 0 and address < target:
                    next_entry = min((a for a in functions if a > address), default=1 << 64)
                    if spans is not None:
                        next_entry = address + spans[address]
                    if target < next_entry:
                        continue
                raise ValueError('unresolved owner edge')
            following = max(following, extra + depth(target, seen | {address}))
        memo[address] = function['local'] + following
        return memo[address]
    maximum = depth(0x400000, set())
    path = []
    current = 0x400000
    while True:
        function = functions[current]
        path.append(dict(name=function['name'], local_bytes=function['local']))
        candidates = [(memo[target] + extra, target) for target, extra in function['edges'] if target in memo]
        if not candidates:
            break
        current = max(candidates)[1]
    observation = {'method': 'sum static pushes/subtractions plus128 redzone per function and direct call/tail graph',
            'entry_stack_bytes': maximum, 'usable_stack_bytes': usable,
            'reachable_functions': len(memo), 'readonly_constant_edges': constant_edges,
            'maximum_path': path,
            'scope': 'compiled matched ELF/raw; overestimates alternative prologues; not formal peak/interrupt proof'}
    if maximum > usable:
        raise StackLimit(observation)
    return observation
