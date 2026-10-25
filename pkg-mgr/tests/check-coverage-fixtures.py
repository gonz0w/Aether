#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Reject invented or stale coverage using a disposable miniature inventory."""
import copy
import importlib.util
from pathlib import Path
import tempfile


def main():
    source = Path(__file__).with_name('check-development.py')
    spec = importlib.util.spec_from_file_location('development', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='pkg-coverage-') as directory:
        root = Path(directory)
        (root / 'test.txt').write_text('reject corrupt record\n')
        case = dict(id='fixture-rejection', surface='parser', owner='fixture',
                    family='contract', stage='before-merge', layer='host',
                    test='test.txt', anchor='reject corrupt record',
                    oracle='corrupt record rejected', forbidden='publication',
                    limits='synthetic fixture', clauses=['Coding:CE-05'])
        valid = dict(surfaces=[dict(id='parser', tests=['test.txt'])],
                     coverage_cases=[case])
        if module.check_cases(root, valid) != 1:
            raise AssertionError('positive discovery count')
        invalid = []
        for field, value in [('oracle', ''), ('clauses', []),
                             ('surface', 'invented'), ('layer', 'verified'),
                             ('stage', 'green'), ('anchor', 'absent'),
                             ('test', '../outside.txt')]:
            item = copy.deepcopy(valid)
            item['coverage_cases'][0][field] = value
            invalid.append(item)
        invalid += [dict(surfaces=valid['surfaces'], coverage_cases=[]),
                    dict(surfaces=valid['surfaces'], coverage_cases=[case, case])]
        for item in invalid:
            try:
                module.check_cases(root, item)
            except ValueError:
                continue
            raise AssertionError('invalid coverage accepted')
        (root / 'test.txt').write_text('reject corrupt record\n' * 2)
        try:
            module.check_cases(root, valid)
        except ValueError:
            pass
        else:
            raise AssertionError('ambiguous anchor accepted')
    print('PASS: coverage positive control and 10 semantic rejection cases')


if __name__ == '__main__':
    main()
