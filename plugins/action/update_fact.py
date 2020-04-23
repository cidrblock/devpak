from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import copy
import json
import re
from ansible.plugins.action import ActionBase
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible.errors import AnsibleModuleError
from collections.abc import MutableMapping


ARGSPEC = {
    'argument_spec': {
        'updates': {
            'required': True,
            'type': 'list'
        },
    }
}

VALID_MODULE_KWARGS = ('argument_spec', 'mutually_exclusive', 'required_if',
                       'required_one_of', 'required_together')


class ActionModule(ActionBase):
    """ action module
    """

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._updates = None
        self._result = None

    def _check_argspec(self):
        # pylint: disable=W0212
        basic._ANSIBLE_ARGS = to_bytes(
            json.dumps({'ANSIBLE_MODULE_ARGS': self._task.args}))
        # pylint: enable=W0212
        spec = {k: v for k, v in ARGSPEC.items() if k in VALID_MODULE_KWARGS}
        basic.AnsibleModule.fail_json = self._fail_json
        basic.AnsibleModule(**spec)

    def _fail_json(self, msg):
        msg = msg.replace('(basic.py)', self._task.action)
        raise AnsibleModuleError(msg)

    def _set_vars(self):
        self._updates = self._task.args.get('updates')
      

    @staticmethod
    def set_value_at_path(fact, path, value):
        obj = copy.deepcopy(fact)

        *parts, last = path.split('.')

        for part in parts:
            if isinstance(obj, MutableMapping):
                obj = obj[part]
            else:
                obj = obj[int(part)]

        if isinstance(obj, MutableMapping):
            obj[last] = value
        else:
            obj[int(last)] = value
        return obj
    
    def set_value(self, obj, path, val):
        first, sep, rest = path.partition(".")
        if first.isnumeric():
            first = int(first)
        if rest:
            new_obj = obj[first]
            self.set_value(new_obj, rest, val)
        else:
            obj[first] = val


    def run(self, tmp=None, task_vars=None):
        self._task.diff = True
        self._result = super(ActionModule, self).run(tmp, task_vars)
        # self._check_argspec()
        # self._set_vars()

        facts = {}

        results = set()
        for key, value in self._task.args.items():
            obj, path = key.split('.', 1)
            results.add(obj)
            path = re.sub(r"\[(\d+)\]", r".\1", path)
            retrieved = task_vars['vars'].get(obj)
            self.set_value(retrieved, path, value)
        
        for key in results:
            self._result.update({key: task_vars['vars'].get(obj)})
        
        self._result.update({"targs": self._task.args})

        return self._result
