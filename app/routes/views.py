from typing import Dict

# from app.apis.skeleton.mainmod import skeletonize
# from app.apis.neuroglancer.mainmod import main_func as main_func_b
from fastapi import APIRouter, Depends, Response
from app.core.auth import get_current_user
from app.settings import PCGSettings
from annotationframeworkclient import FrameworkClient
from pcg_skel import pcg_meshwork
import cloudvolume
from datetime import datetime
import io
import logging
import numpy as np
import tempfile
import os


router = APIRouter()
settings = PCGSettings()


def skeletonize(seg_id: int,
                datastack_name: str) -> Dict[str, int]:

    client = FrameworkClient(datastack_name=datastack_name,
                             server_address=settings.server_address,
                             auth_token=settings.auth_token)

    cv = cloudvolume.CloudVolume(client.info.segmentation_source(),
                                 use_https=True,
                                 secrets={"token": settings.auth_token})

    # get a soma pt if you can
    soma_table = client.info.get_datastack_info()['soma_table']
    soma_pt = None
    if soma_table is not None:
        try:
            # TODO think of a better way to figure out soma location
            # this won't work for stale IDs
            # one idea.. use a timestamp of the seg_id, need pcg endpoint for that
            soma_df = client.materialize.live_query(soma_table,
                                                    datetime.utcnow(),
                                                    filter_equal_dict={'pt_root_id': seg_id})
            if len(soma_df) > 0:
                soma_pt = soma_df.pt_position.iloc[0]

        except ValueError:
            pass
    # TODO add resolution metadata to annotation table to get
    # soma_pt resolution dynamically
    logging.debug(settings)
    logging.debug(soma_pt)
    # TODO: get lvl2graph from cache/create
    # TODO: passs lvl2graph to pcg_skel after functionality exists
    sk = pcg_meshwork(seg_id,
                      datastack_name=datastack_name,
                      client=client,
                      cv=cv,
                      refine=settings.refine,
                      root_point=soma_pt,
                      root_point_resolution=np.array(
                          settings.root_point_resolution),
                      root_point_search_radius=settings.root_point_search_radius,
                      collapse_radius=settings.collapse_radius,
                      collapse_soma=settings.collapse_soma_if_possible,
                      invalidation_d=settings.invalidation_d,
                      segmentation_fallback=settings.segmentation_fallback,
                      fallback_mip=settings.fallback_mip,
                      cache=settings.cache,
                      save_to_cache=settings.save_to_cache,
                      n_parallel=settings.n_parallel)

    return sk, soma_pt


@router.get("/skeleton/datastack/{datastack}/seg_id/{seg_id}", tags=["skeleton"])
async def hdf_skeleton(datastack: str, seg_id: int) -> Response:
    #logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    # TODO: ADD CACHING
    # TODO: ADD RECREATE FLAG
    mwsk, soma_pt = skeletonize(seg_id,
                                datastack_name=datastack)

    with tempfile.NamedTemporaryFile(
            suffix=".h5", mode='w', delete=False) as tf:
        temppath = os.path.join(tempfile.gettempdir(), tf.name)
        mwsk.save_meshwork(temppath, overwrite=True)

    with open(temppath, 'rb') as fp:
        bytes = fp.read()

    resp = Response(content=bytes,
                    status_code=200,
                    media_type="application/x-hdf")
    os.remove(temppath)
    yield resp

# @router.get("/api_b/{num}", tags=["api_b"])
# async def view_b(num: int, auth=Depends(get_current_user)) -> Dict[str, int]:
#     return main_func_b(num)
