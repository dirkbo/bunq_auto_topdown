#!/usr/bin/env .venv/bin/python -W ignore
import argparse

from libs.bunq_lib import BunqLib
from libs.share_lib import ShareLib
from bunq.sdk.context import ApiEnvironmentType
from decimal import Decimal
from bunq.sdk.model.generated.endpoint import *
from bunq.sdk.model.generated.object_ import Pointer, Amount, NotificationFilter



def main():

    all_option = ShareLib.parse_all_option()
    environment_type = ShareLib.determine_environment_type_from_all_option(all_option)

    bunq = BunqLib(environment_type)

    account_a = None
    account_b = None

    account_a_id = "17952"
    account_b_id = "17958"

    if all_option.topdown_from_account:
        try:
            # Try usingbunq account id
            account_a = MonetaryAccountBank.get(all_option.topdown_from_account)
            account_a = account_a.value
            account_a_id = account_a.id_
            print(" Watching (bunq_id): %s" % all_option.topdown_from_account)
        except Exception as e:
            # Check for iban / phone /whatever alias
            for account in bunq.get_all_monetary_account_active():
                for alias in account.alias:
                    if alias.value == all_option.topdown_from_account:
                        account_a = account
                        account_a_id = account_a.id_
                        print(" Watching: %s" % all_option.topdown_from_account)
    else:
        return

    if all_option.topdown_to_account:
        try:
            # Try using bunq account id
            account_b = MonetaryAccountBank.get(all_option.topdown_to_account)
            account_b = account_b.value
            account_b_id = account_b.id_
            print(" Sending extra Money to (bunq_id): %s" % all_option.topdown_to_account)
        except Exception as e:
            # Check for iban / phone / whatever alias
            for account in bunq.get_all_monetary_account_active():
                for alias in account.alias:
                    if alias.value == all_option.topdown_to_account:
                        account_b = account
                        account_b_id = account_b.id_
                        print(" Sending extra Money To: %s" % all_option.topdown_to_account)
    else:
        return

    max_value = Decimal(125)
    if all_option.amount:
        max_value = Decimal(all_option.amount)
        print("Maximum Money to keep: %s" % max_value)
    else:
        return

    if environment_type is ApiEnvironmentType.SANDBOX:
        # In Sandbox use Fallback

        if account_b is None:
            print("Using Sandbox fallback")
            account_b_id = "17958"

        if account_a is None:
            account_a_id = "17952"
            print("Using Sandbox fallback")
            try:
                account_a = MonetaryAccountBank.get(account_a_id)
                account_a = account_a.value
            except:
                pass
            finally:
                if account_a is None:
                    return

    if account_a is not None and account_b_id is not None:
        a_balance = Decimal(account_a.balance.value)
        print("Balance (%s): %s of Max %s" % (account_a.id_, a_balance, max_value))
        if account_a.balance.currency != account_b.balance.currency:
            print("Auto Top-Down not Possible, currencies don't match!")
            return
        if a_balance > max_value:
            delta = a_balance - max_value
            # send delta amount to b
            print(" Moving %s to %s" % (delta, account_b_id))
            description = "Auto Down"
            amount_string = str(delta)
            Payment.create(
                amount=Amount(amount_string, account_a.balance.currency),
                monetary_account_id=account_a_id,
                counterparty_alias=ShareLib.get_first_pointer_iban(account_b),
                description=description
            )
        else:
            print(" Balance OK")

    bunq.update_context()

if __name__ == '__main__':
    main()
