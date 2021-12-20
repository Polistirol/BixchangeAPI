
ORDER_TYPE_CHOICHES = (
    (1, ("Buy_Market")),
    (2, ("Sell_Market")),
    (3, ("Buy_Limit_Fast")),
    (4, ("Sell_Limit_Fast")),
    (5, ("Buy_Limit_Full")),
    (6, ("Sell_Limit_Full")),
    (99, ("Referral")),
)

ORDER_STATUS_CHOICHES = (
    (1, ("Open")),
    (2, ("Closed")),
    (3, ("Failed")),
    (4, ("Canceld"))
)

TRANSACTION_TYPE_CHOICHES = (
    (1, ("exchange")),
    (99, ("referral")),
)


def is_order_type_valid(_type):
    for t in ORDER_TYPE_CHOICHES:
        if _type == t[0]:
            return True
    return False
