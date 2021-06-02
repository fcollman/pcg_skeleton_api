from app.apis.skeleton.mainmod import main_func as main_func_a
from app.apis.neuroglancer.mainmod import main_func as main_func_b


def test_func_main_a() -> None:
    seed = 420
    result = main_func_a(seed)
    assert isinstance(result, dict) is True
    assert result.get("seed") == seed
