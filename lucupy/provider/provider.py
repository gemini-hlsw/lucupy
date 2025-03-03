from typing import Optional

from lucupy.minimodel import ProgramID, Program, ObservationID, Observation
from lucupy.odb import QueryBlueprint, LucumaClient
from .converter import converter

__all__ = [
    'Provider',
]


class Provider:
    """
    Uses the Lucuma client to generate minimodel objects.
    """
    def __init__(self, client: LucumaClient):
        self.client = client

    async def  get_observation(self,
                               obs_id: ObservationID,
                               blueprint: Optional[QueryBlueprint]= None) -> Observation:
        if blueprint is None:
            blueprint = QueryBlueprint() # set default parameters
        json_obs = await self.client.get_observation(obs_id.id, blueprint=blueprint)
        return converter.structure(json_obs['observation'], Observation)

