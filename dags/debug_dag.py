from __future__ import annotations

import copy

from airflow.operators.python import PythonOperator


class ThirdPartyClassWithMisbehavedGetAttr:

    def __getattr__(self, item):
        if attr := getattr(self, f'_{item}'):
            return attr
        raise AttributeError


class CustomOperator(PythonOperator):

    shallow_copy_attrs = ('_misbehavedparam', 'misbehavedparam')

    def __init__(self,
                 *,
                 misbehavedparam: None | ThirdPartyClassWithMisbehavedGetAttr = None,
                 **kwargs):
        super().__init__(**kwargs)
        self._misbehavedparam = misbehavedparam or ThirdPartyClassWithMisbehavedGetAttr()

    def __deepcopy__(self, *args):  # Only here to intercept the call and allow debuging
        # breakpoint()
        super().__deepcopy__(*args)


def f(**kwargs):
    print('here')


operator1 = CustomOperator(python_callable=f, task_id='doit')
print(operator1._BaseOperator__init_kwargs)
result = copy.deepcopy(operator1)  # Infinite recursion loop.
