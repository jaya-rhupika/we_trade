from analytics_etl.transform import transform


def test_transform_is_importable():
    assert callable(transform)