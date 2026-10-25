# SPDX-License-Identifier: BSD-2-Clause
"""Selected AF05 owner and independent digest-shaped namespace oracle."""
from openzfs_fs_activation_service import owner as activation_owner
from openzfs_fs_runtime_service import probe as runtime_probe

FIRST = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
SECOND = FIRST[:-1] + '6'


def validate_profile(selected, activation, runtime, reader, service):
    if not isinstance(selected, bool):
        raise ValueError('names selection must be boolean')
    if selected and not (runtime and ((activation and service is not None) or
                                      (reader and service is None))):
        raise ValueError('names require activation writer or independent runtime reader')
    if isinstance(service, dict) and service.get('names', False) is not selected:
        raise ValueError('names delivery/profile mismatch')


def owner(text, waiting=True):
    selected = activation_owner(text, waiting)
    for old, new in [('"activation-service.h"', '"names-service.h"'),
                     ('aether_fs_activation_run(', 'aether_fs_names_run(')]:
        if selected.count(old) != 1:
            raise ValueError('names owner exact context: ' + old)
        selected = selected.replace(old, new, 1)
    return selected


def probe(text, reader=False, empty=False, case='normal'):
    selected = runtime_probe(text, reader, empty, case)
    for old, new in [('"p"', '"' + FIRST + '"'), ('"q"', '"' + SECOND + '"')]:
        if selected.count(old) != 1:
            raise ValueError('names independent oracle exact context: ' + old)
        selected = selected.replace(old, new, 1)
    return selected
