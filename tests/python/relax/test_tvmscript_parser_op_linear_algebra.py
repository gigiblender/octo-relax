# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from typing import Optional, Union

import tvm
import tvm.testing
from tvm import IRModule, relax
from tvm.script.parser import relax as R


def _check(
    parsed: Union[relax.Function, IRModule],
    expect: Optional[Union[relax.Function, IRModule]],
):
    test = parsed.script(show_meta=True)
    roundtrip_mod = tvm.script.parse(test)
    tvm.ir.assert_structural_equal(parsed, roundtrip_mod)
    if expect:
        tvm.ir.assert_structural_equal(parsed, expect)


def test_matmul():
    @R.function
    def foo(
        x: R.Tensor((2, 3, 4, 5), "float32"), y: R.Tensor((6, 2, 3, 5, 7), "float32")
    ) -> R.Tensor((6, 2, 3, 4, 7), "float32"):
        gv: R.Tensor((6, 2, 3, 4, 7), "float32") = R.matmul(x, y)
        return gv

    x = relax.Var("x", R.Tensor((2, 3, 4, 5), "float32"))
    y = relax.Var("y", R.Tensor((6, 2, 3, 5, 7), "float32"))
    bb = relax.BlockBuilder()
    with bb.function("foo", [x, y]):
        gv = bb.emit(relax.op.matmul(x, y))
        bb.emit_func_output(gv)

    _check(foo, bb.get()["foo"])


if __name__ == "__main__":
    tvm.testing.main()
