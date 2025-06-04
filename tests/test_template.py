
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

        # 2. Initialize python internal state


    @flow()
    def flow_deposit(self):

        # 1. Prepare random input

        # 2. Run transaction

        # 3. Check error

        # 4. Check events

        # 5. Update python state

        pass

    @flow()
    def flow_withdraw(self):
        # 1. Prepare random input

        # 2. Run transaction

        # 3. Check error

        # 4. Check events

        # 5. Update python state

        pass


    @invariant()
    def invariant_balances(self):
        pass


@chain.connect()
def test_vault_fuzz():
    VaultFuzzTest.run(10, 1_000_000)