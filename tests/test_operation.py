import brownie
from brownie import Wei


def test_mint(ygift, token, giftee, chain):
    amount = Wei("1000 ether")
    start = chain[-1].timestamp + 1000
    duration = 1000
    token.approve(ygift, 2 ** 256 - 1)
    ygift.mint(giftee, token, amount, "name", "msg", "url", start, duration)
    gift = ygift.gifts(0).dict()
    assert gift == {
        "token": token,
        "name": "name",
        "message": "msg",
        "url": "url",
        "amount": amount,
        "start": start,
        "duration": duration,
    }


def test_tip(ygift, token, giftee, chain):
    amount = Wei("1000 ether")
    start = chain[-1].timestamp
    token.approve(ygift, 2 ** 256 - 1)
    ygift.mint(giftee, token, amount, "name", "msg", "url", start, 0)
    ygift.tip(0, amount, "tip")
    gift = ygift.gifts(0).dict()
    assert gift["amount"] == amount * 2


def test_tip_nonexistent(ygift, token):
    with brownie.reverts("yGift: Token ID does not exist."):
        ygift.tip(1, 1000, "nope")


def test_collect(ygift, token, giftee, chain):
    amount = Wei("1000 ether")
    start = chain[-1].timestamp + 1000
    duration = 1000
    token.approve(ygift, 2 ** 256 - 1)
    ygift.mint(giftee, token, amount, "name", "msg", "url", start, duration)

    with brownie.reverts("yGift: Rewards still vesting"):
        ygift.collect(0, amount, {"from": giftee})

    # excess requested amount is rounded down to available
    chain.sleep(1200)
    chain.mine()
    ygift.collect(0, amount, {"from": giftee})
    assert 0 < token.balanceOf(giftee) < amount

    chain.sleep(duration)
    chain.mine()

    with brownie.reverts("yGift: You are not the NFT owner"):
        ygift.collect(0, amount)

    ygift.collect(0, amount, {"from": giftee})
    assert token.balanceOf(giftee) == amount
