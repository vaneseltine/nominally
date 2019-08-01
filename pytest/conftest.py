import pytest


@pytest.fixture(scope="module", autouse=True, params=["", None])
def empty_attribute_value(request):
    from nameparser.config import CONSTANTS

    CONSTANTS.empty_attribute_default = request.param
    # from  request.param
