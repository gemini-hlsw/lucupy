import inspect
from dataclasses import dataclass, asdict, astuple
from functools import wraps
from typing import List

from gql import Client, gql
from gql.dsl import DSLSchema, dsl_gql, DSLQuery, DSLFragment
import aiohttp
from gql.transport.websockets import WebsocketsTransport
from gql.transport.aiohttp import AIOHTTPTransport


from lucupy.minimodel import ProgramID, Program, Semester, Observation, ObservationID


@dataclass(frozen=True)
class Fragments:
    """
    A collection of DSL fragments.
    each one represent a part of a query but also can be
    mapped as a lucupy minimodel object.
    """

    program: DSLFragment
    group: DSLFragment
    observation: DSLFragment
    sequence: DSLFragment
    atom_north: DSLFragment
    atom_south: DSLFragment


def with_session(obs_with_sequence:bool=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Check if the function is a coroutine
            if not inspect.iscoroutinefunction(func):
                raise TypeError(f"{func.__name__} must be an async function")
            async with self._client as session:
                # Inject the session into the method call
                self._ds = DSLSchema(self._client.schema)
                self._fragments = self._load_fragments(obs_with_sequence)
                return await func(self, *args, session=session, **kwargs)
        return wrapper
    return decorator

class Lucuma:

    def __init__(self, gpp_env_url: str, gpp_api_key: str):
        self._transport = AIOHTTPTransport(
            url=gpp_env_url,
            headers={"Authorization": f"Bearer {gpp_api_key}"},
            client_session_args={
               'timeout': aiohttp.ClientTimeout(
                   total=300,  # Total timeout in seconds (5 minutes)
                   connect=60,  # Connection timeout
                   sock_read=60,  # Socket read timeout
                   sock_connect=60  # Socket connect timeout
               )
           }
        )
        self._client = Client(transport=self._transport, fetch_schema_from_transport=True)
        self._ds = None
        self._fragments = None


    def _load_fragments(self, with_sequence: bool):

        atom_north_fragment = DSLFragment('lucupyAtomNorth')
        atom_north_fragment.on(self._ds.GmosNorthAtom)
        atom_north_fragment.select(
            self._ds.GmosNorthAtom.id,
            self._ds.GmosNorthAtom.description,
            self._ds.GmosNorthAtom.observeClass,
        )

        atom_south_fragment = DSLFragment('lucupyAtomSouth')
        atom_south_fragment.on(self._ds.GmosSouthAtom)
        atom_south_fragment.select(
            self._ds.GmosSouthAtom.id,
            self._ds.GmosSouthAtom.description,
            self._ds.GmosSouthAtom.observeClass,
        )


        seq_fragment = DSLFragment('lucupySequence')
        seq_fragment.on(self._ds.Execution)
        seq_fragment.select(
            self._ds.Execution.config.select(
                self._ds.ExecutionConfig.gmosNorth.select(
                    self._ds.GmosNorthExecutionConfig.acquisition.select(
                        self._ds.GmosNorthExecutionSequence.possibleFuture.select(
                            atom_north_fragment
                        )
                    ),
                    self._ds.GmosNorthExecutionConfig.science.select(
                        self._ds.GmosNorthExecutionSequence.possibleFuture.select(
                            atom_north_fragment
                        )
                    ),

                ),
                self._ds.ExecutionConfig.gmosSouth.select(
                    self._ds.GmosSouthExecutionConfig.acquisition.select(
                        self._ds.GmosSouthExecutionSequence.possibleFuture.select(
                            atom_south_fragment
                        )
                    ),
                    self._ds.GmosSouthExecutionConfig.science.select(
                        self._ds.GmosSouthExecutionSequence.possibleFuture.select(
                            atom_south_fragment
                        )
                    )
                )
            )
        )

        obs_fragment = DSLFragment('lucupyObservation')
        obs_fragment.on(self._ds.Observation)
        obs_base_fragment = [
            self._ds.Observation.id,
            self._ds.Observation.instrument,
            self._ds.Observation.scienceBand,
            self._ds.Observation.observationDuration.select(
                self._ds.TimeSpan.seconds
            ),
            self._ds.Observation.observationTime,
            self._ds.Observation.observingMode.select(
                self._ds.ObservingMode.instrument,
                self._ds.ObservingMode.mode
            ),
            self._ds.Observation.groupId,
            self._ds.Observation.groupIndex,
            self._ds.Observation.configuration.select(
                self._ds.Configuration.conditions.select(
                    self._ds.ConfigurationConditions.imageQuality
                )
            ),

        ]
        obs_with_sequence = self._ds.Observation.execution.select(seq_fragment)
        if with_sequence:
            obs_base_fragment.append(obs_with_sequence)

        obs_fragment.select(*obs_base_fragment)


        group_fragment = DSLFragment('lucupyGroup')
        group_fragment.on(self._ds.GroupElement)
        group_fragment.select(
            self._ds.GroupElement.parentGroupId,
            self._ds.GroupElement.group.select(
                self._ds.Group.id,
                self._ds.Group.parentId,
                self._ds.Group.elements.select(
                    self._ds.GroupElement.group.select(
                        self._ds.Group.id,
                        self._ds.Group.parentId,
                        self._ds.Group.parentIndex
                    ),
                    self._ds.GroupElement.observation.select(
                        self._ds.Observation.id,
                        self._ds.Observation.groupId,
                        self._ds.Observation.groupIndex
                    )
                )
            ),
            self._ds.GroupElement.observation.select(
                self._ds.Observation.id,
                self._ds.Observation.groupId,
                self._ds.Observation.groupIndex
            )
        )


        program_fragment = DSLFragment('lucupyProgram')
        program_fragment.on(self._ds.Program)
        program_fragment.select(
            self._ds.Program.id,
            self._ds.Program.type,
            self._ds.Program.allGroupElements.select(
                group_fragment
            )
        )

        return Fragments(program=program_fragment,
                         group=group_fragment,
                         observation=obs_fragment,
                         sequence=seq_fragment,
                         atom_north=atom_north_fragment,
                         atom_south=atom_south_fragment,
                         )

    @with_session()
    async def get_programs(self,
                           semester: Semester,
                           status: str,
                           session) -> Program:
        # Argument WhereProgram let you filter programs in Graphql
        where_program = {
            "AND": [{
                        "reference":{
                            "semester":{
                                "EQ": str(semester),
                        }
                    }
                },
                {
                    "proposalStatus": {
                        "EQ": status
                    }
                }
            ]
        }
        query = dsl_gql(
            DSLQuery(
                self._ds.Query.programs.args(
                    **{"WHERE":where_program},
                ).select(
                    self._ds.ProgramSelectResult.matches.select(
                        self._fragments.program
                    )
                )
            )
        # , **vars(fragments))
        ,self._fragments.program,
         self._fragments.group,)
        res = await session.execute(query)
        return res

    @with_session()
    async def get_program(self, p_id: ProgramID, session) -> Program:

        query = dsl_gql(
            DSLQuery(
                self._ds.Query.program.args(
                    **{"programId": p_id}
                ).select(self._fragments.program)
            )
        , self._fragments.program, self._fragments.group)
        res = await session.execute(query)
        return res

    @with_session()
    async def get_observations(self, p_id: ProgramID, states: List[str], session) -> Observation:

        where = {
            "AND":[
                { "program" : {
                    "id" : {
                        "EQ": str(p_id),
                    }
                }}
            ]
        }

        query = dsl_gql(
            DSLQuery(
                self._ds.Query.observationsByWorkflowState.args(
                    **{"WHERE": where, "states": states},
                ).select(
                    self._fragments.observation
                    )
                ), self._fragments.observation
            )
        res = await session.execute(query)
        return res

    @with_session(obs_with_sequence=True)
    async def get_sequence(self, obs_id: ObservationID, session) -> Observation:
        query = dsl_gql(
            DSLQuery(
                self._ds.Query.observation.args(
                    **{"observationId": obs_id},
                ).select(
                    self._fragments.observation
                )
            ), self._fragments.observation,
            self._fragments.sequence,
            self._fragments.atom_north,
            self._fragments.atom_south
        )
        res = await session.execute(query)
        return res





