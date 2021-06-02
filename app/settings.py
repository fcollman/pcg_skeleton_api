from pydantic import BaseSettings


class PCGSettings(BaseSettings):
    server_address: str = "https://global.daf-apis.com"
    refine: str = "all"
    root_point_search_radius: int = 3000
    collapse_soma_if_possible: bool = True
    collapse_radius: float = 7500.0
    root_point_resolution: list = [4, 4, 40]
    invalidation_d: int = 3
    n_parallel: int = 4
    auth_token: str
    segmentation_fallback: bool = True
    fallback_mip: int = 3
    cache: str = "sqllite.cache"
    save_to_cache: bool = True
