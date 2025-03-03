import inspect
from dataclasses import dataclass, asdict, astuple
from functools import wraps
from typing import List

from gql import Client, gql
from gql.dsl import DSLSchema, dsl_gql, DSLQuery, DSLFragment
import aiohttp
from gql.transport.websockets import WebsocketsTransport
from gql.transport.aiohttp import AIOHTTPTransport


from lucupy.minimodel import ProgramID, Program, Semester, Observation, ObservationID, ALL_SITES, Site
from lucupy.odb.blueprint import QueryBlueprint


__all__ = [
    'LucumaClient',
]



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


def with_session():
    def decorator(func):
        @wraps(func)
        async def wrapper(self,
                          *args,
                          blueprint: QueryBlueprint=QueryBlueprint(),
                          **kwargs):
            # Check if the function is a coroutine
            if not inspect.iscoroutinefunction(func):
                raise TypeError(f"{func.__name__} must be an async function")
            async with self._client as session:
                # Inject the session into the method call
                self._ds = DSLSchema(self._client.schema)
                self._fragments = self._load_fragments(blueprint)
                return await func(self, *args, session=session, blueprint=blueprint, **kwargs)
        return wrapper
    return decorator

class LucumaClient:
    """
    GQL client to connect to the GPP odb database.
    TODO: Transport now is AIOHTTP but it should be websocket so it can be
    TODO: reuse for subscriptions.
    """

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


    def _load_fragments(self, blueprint: QueryBlueprint):
        """
        Load all fragments to the session.
        TODO: This is getting way to big, probably needs his own separate file.
        """
        atom_north_fragment = DSLFragment('lucupyAtomNorth')
        atom_north_fragment.on(self._ds.GmosNorthAtom)
        atom_north_fragment.select(
            self._ds.GmosNorthAtom.id,
            self._ds.GmosNorthAtom.description,
            self._ds.GmosNorthAtom.observeClass,
            self._ds.GmosNorthAtom.steps.select(
                self._ds.GmosNorthStep.id,
                self._ds.GmosNorthStep.estimate.select(
                    self._ds.StepEstimate.total.select(
                        self._ds.TimeSpan.seconds
                    )
                )
            )
        )

        atom_south_fragment = DSLFragment('lucupyAtomSouth')
        atom_south_fragment.on(self._ds.GmosSouthAtom)
        atom_south_fragment.select(
            self._ds.GmosSouthAtom.id,
            self._ds.GmosSouthAtom.description,
            self._ds.GmosSouthAtom.observeClass,
            self._ds.GmosSouthAtom.steps.select(
                self._ds.GmosSouthStep.id,
                self._ds.GmosSouthStep.estimate.select(
                    self._ds.StepEstimate.total.select(
                        self._ds.TimeSpan.seconds
                    )
                )
            )
        )


        seq_fragment = DSLFragment('lucupySequence')
        seq_fragment.on(self._ds.Execution)

        base_seq_fragment = []
        north_seq_fragment = self._ds.ExecutionConfig.gmosNorth.select(
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
        )
        south_seq_fragment = self._ds.ExecutionConfig.gmosSouth.select(
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

        if Site.GN in blueprint.site:
            base_seq_fragment.append(north_seq_fragment)
        if Site.GS in blueprint.site:
            base_seq_fragment.append(south_seq_fragment)
        if not base_seq_fragment:
            raise ValueError('Empty site selection on QueryBlueprint')

        seq_fragment.select(
            self._ds.Execution.config.select(*base_seq_fragment),
            self._ds.Execution.digest.select(
                self._ds.ExecutionDigest.setup.select(
                    self._ds.SetupTime.full.select(self._ds.TimeSpan.seconds)
                )
            )
        )

        target_fragment = DSLFragment('lucupyTarget')
        target_fragment.on(self._ds.Target)
        target_fragment.select(
            self._ds.Target.id,
            self._ds.Target.existence,
            self._ds.Target.name
        )

        target_env_fragment = DSLFragment('lucupyTargetEnv')
        target_env_fragment.on(self._ds.TargetEnvironment)
        target_env_fragment.select(
            self._ds.TargetEnvironment.asterism.select(target_fragment),
            # self._ds.TargetEnvironment.explicitBase.select(target_fragment),
            # self._ds.TargetEnvironment.guideEnvironment.select(target_fragment),
            self._ds.TargetEnvironment.firstScienceTarget.select(target_fragment),
        )

        constraints_fragment = DSLFragment('lucupyConstraints')
        constraints_fragment.on(self._ds.ConstraintSet)
        constraints_fragment.select(
            self._ds.ConstraintSet.imageQuality,
            self._ds.ConstraintSet.cloudExtinction,
            self._ds.ConstraintSet.skyBackground,
            self._ds.ConstraintSet.waterVapor,
            self._ds.ConstraintSet.elevationRange
        )


        # timing_windows_fragment = DSLFragment('lucupyTimingWindows')
        # timing_windows_fragment.on(self._ds.TimingWindow)
        # timing_windows_fragment.select(
        #    self._ds.TimingWindow.inclusion,
        #    self._ds.TimingWindow.startUtc,
        #    self._ds.TimingWindow.end.select(
        #        self._ds.TimingWindowEndAt.atUtc,
        #        self._ds.TimingWindowEndAfter.after.select(self._ds.TimeSpan.seconds),
        #        self._ds.TimingWindowEndAfter.repeat.select(
        #            self._ds.TimingWindowRepeat.period.select(self._ds.TimeSpan.seconds),
        #            self._ds.TimingWindowRepeat.times
        #        )
        #    )
        # )


        obs_fragment = DSLFragment('lucupyObservation')
        obs_fragment.on(self._ds.Observation)
        obs_base_fragment = [
            self._ds.Observation.id,
            self._ds.Observation.reference.select(self._ds.ObservationReference.label),
            self._ds.Observation.title,
            self._ds.Observation.instrument,
            self._ds.Observation.scienceBand,
            self._ds.Observation.workflow.select(
              self._ds.ObservationWorkflow.state
            ),
            self._ds.Observation.program.select(
                self._ds.Program.id,
            ),
            self._ds.Observation.observationDuration.select(
                self._ds.TimeSpan.seconds
            ),
            self._ds.Observation.observationTime,
            # self._ds.Observation.targetEnvironment.select(target_fragment),
            self._ds.Observation.observingMode.select(
                self._ds.ObservingMode.instrument,
                self._ds.ObservingMode.mode
            ),
            self._ds.Observation.groupId,
            self._ds.Observation.groupIndex,
            # self._ds.Observation.configuration.select(constraints_fragment),

        ]
        obs_with_sequence = self._ds.Observation.execution.select(seq_fragment)
        if blueprint.obs_with_sequence:
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
                           session,
                           blueprint) -> Program:
        """
        List of programs based on a Semester and a set of status.
        This can't be done with whole observations but with groups.
        """
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
    async def get_program(self, p_id: ProgramID, session, blueprint) -> Program:
        """
        Retrieve a program by ID. Can't be used with observation fragment.
        """

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
    async def get_observations(self, p_id: ProgramID, states: List[str], session, blueprint) -> dict:
        """
        Deliver a list of observations based on program and a series of states.
        This can only be performed for obs_with_sequence = False
        """
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

    @with_session()
    async def get_observation(self, obs_id: str, session, blueprint) -> dict:
        """
        Retrieve an observation by ID.
        """

        atom_fragments = []

        if Site.GS in blueprint.site:
            atom_fragments.append(self._fragments.atom_south)
        if Site.GN in blueprint.site:
            atom_fragments.append(self._fragments.atom_north)

        query = dsl_gql(
            DSLQuery(
                self._ds.Query.observation.args(
                    **{"observationId": obs_id},
                ).select(
                    self._fragments.observation
                )
            ),
            self._fragments.observation,
            self._fragments.sequence,
            *atom_fragments
        )
        res = await session.execute(query)
        return res





