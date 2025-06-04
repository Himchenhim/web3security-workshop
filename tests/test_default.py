from wake.testing import *

from pytypes.contracts.Vault import SingleTokenVault
from pytypes.tests.helpers.MockERC20 import MockERC20

# Print failing tx call trace
def revert_handler(e: RevertError):
    if e.tx is not None:
        print(e.tx.call_trace)


@chain.connect()
@on_revert(revert_handler)
def test_default():
    admin = chain.accounts[0]
    user = chain.accounts[1]

    token = MockERC20.deploy("MockERC20", "MOCK", from_=admin)
    vault = SingleTokenVault.deploy(token, 1 * 10 ** 18, 1_000 * 10 ** 18, from_=admin)

    # token.mint(user, 1_000 * 10 ** 18, from_=admin)
    mint_erc20(token, user, 100 * 10 ** 18)
    token.approve(vault, 100 * 10 ** 18, from_=user)

    vault.deposit(100 * 10 ** 18, from_=user)
    vault.withdraw(100 * 10 ** 18, from_=user)

