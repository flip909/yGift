import brownie


def test_controller(ygift, controller, minter, token):
    assert ygift.symbol() == "yGIFT"
    assert ygift.controller() == controller

    ygift.setController(minter)
    assert ygift.controller() == minter

    with brownie.reverts():
        ygift.setController(controller)
