from wake.testing import *

from pytypes.contracts.Vault import SingleTokenVault
from pytypes.tests.helpers.MockERC20 import MockERC20

# Print failing tx call trace
def revert_handler(e):
    if e.tx is not None:
        print(e.tx.call_trace)


@chain.connect()
@on_revert(revert_handler)
def test_default():
    pass

