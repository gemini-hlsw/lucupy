GET_PROGRAM_NOTE = """
query getProgramNote($programNoteId: ProgramNoteId!) {
    programNote(programNoteId: $programNoteId) {
        {fields}
    }
}
"""

GET_PROGRAM_NOTES = """
query getProgramNotes(
    $where: WhereProgramNote,
    $offset: ProgramNoteId,
    $limit: NonNegInt,
    $includeDeleted: Boolean = false
) {
    programNotes(
        WHERE: $where,
        OFFSET: $offset,
        LIMIT: $limit,
        includeDeleted: $includeDeleted
    ) {
        matches {
            {fields}
        }
        hasMore
    }
}
"""

CREATE_PROGRAM_NOTE = """
mutation createProgramNote($input: CreateProgramNoteInput!) {
    createProgramNote(input: $input) {
        programNote {
            {fields}
        }
    }
}
"""

UPDATE_PROGRAM_NOTES = """
mutation updateProgramNotes($input: UpdateProgramNotesInput!) {
    updateProgramNotes(input: $input) {
        programNotes {
            {fields}
        }
        hasMore
    }
}
"""

DEFAULT_FIELDS = """
    id
    program {
        id
        name
    }
    title
    text
    isPrivate
    existence
"""
