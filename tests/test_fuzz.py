import logging
from wake.testing import *
from wake.testing.fuzzing import *

from collections import defaultdict
from typing import Dict

from pytypes.contracts.Vault import SingleTokenVault
from pytypes.tests.helpers.MockERC20 import MockERC20

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class VaultFuzzTest(FuzzTest):

    vault: SingleTokenVault
    token: MockERC20

    vault_balances: dict[Address, int] = {}
    token_balances: dict[Address, int] = {}

    def pre_sequence(self):
        self.admin = random_account()

        # 1. Deploy contracts
        self.token = MockERC20.deploy("MockERC20", "MOCK", from_=self.admin)
        self.vault = SingleTokenVault.deploy(self.token, 1 * 10 ** 18, 1_000 * 10 ** 18, from_=self.admin)

        # 2. Initialize python internal state
        self.vault_balances = defaultdict(int)
        self.token_balances = defaultdict(int)

    @flow()
    def flow_deposit(self):

        # 1. Prepare random input
        amount = random.randint(1, 100000) * 10 ** 16
        user = random_account()

        mint_erc20(self.token, user, amount)
        self.token.approve(self.vault, amount, from_=user)
        self.token_balances[user.address] += amount

        # 2. Run transaction
        deposit_tx: TransactionAbc
        with may_revert( (self.vault.BelowMinDeposit, self.vault.AboveMaxDeposit) ) as e:
            deposit_tx = self.vault.deposit(amount, from_=user)

        # 3. Check error
        if self.vault.minDepositAmount() > amount or self.vault.maxDepositAmount() < amount:
            assert e.value == self.vault.BelowMinDeposit() or e.value == self.vault.AboveMaxDeposit()
            return
        else:
            assert e.value == None

        # 4. Check events
        events = [e for e in deposit_tx.events if isinstance(e, self.vault.Deposited)]
        assert len(events) == 1
        assert isinstance(events[0], self.vault.Deposited)
        assert events[0].user == user.address
        assert events[0].amount == amount

        logger.info(f"User {user} deposited {amount} tokens")

        # 5. Update python state
        self.vault_balances[user.address] += amount
        self.token_balances[user.address] -= amount

    @flow()
    def flow_withdraw(self):
        # 1. Prepare random input
        eligible_users = [user for user in self.vault_balances.keys() if self.vault_balances[user] > 0]
        if not eligible_users:
            return
        user = random.choice(eligible_users)
        amount = random.randint(1, self.vault_balances[user] * 2)

        # 2. Run transaction
        withdraw_tx: TransactionAbc
        with may_revert(self.vault.InsufficientBalance) as e:
            withdraw_tx = self.vault.withdraw(amount, from_=user)

        # 3. Check error
        if self.vault_balances[user] < amount:
            assert e.value == self.vault.InsufficientBalance()
            return
        else:
            assert e.value == None

        # 4. Check events
        events = [e for e in withdraw_tx.events if isinstance(e, self.vault.Withdrawn)]
        assert len(events) == 1
        assert isinstance(events[0], self.vault.Withdrawn)
        assert events[0].user == user
        assert events[0].amount == amount

        logger.info(f"User {user} withdrew {amount} tokens")

        # 5. Update python state
        self.vault_balances[user] -= amount
        self.token_balances[user] += amount


    @invariant()
    def invariant_balances(self):
        for account in self.vault_balances.keys():
            assert self.vault_balances[account] == self.vault.balanceOf(account)
            assert self.token_balances[account] == self.token.balanceOf(account)


@chain.connect()
def test_vault_fuzz():
    VaultFuzzTest.run(10, 1_000_000)