SUBJECT_GROUPS:dict[str,str]={
    "Physics":"stem",
    "Chemistry":"stem",
    "Biology":"stem",
    "Math":"math",
    "Bangla":"pros",
    "English":"pros",
    "History":"pros",
    "Geography":"pros",
    "Philosophy":"pros",
    "Literature":"pros",
    "Social Science":"pros",
    "Religion":"pros",

}

SUBJECTS:list[str]=list(SUBJECT_GROUPS.keys())
GROUPS:set[str]=set(SUBJECT_GROUPS.values())

def group_for_subject(subject:str)->str:
    """
    Returns the group for a given subject.
    If the subject is not found, returns 'unknown'.
    """

    try:
        return SUBJECT_GROUPS[subject]
    except KeyError:
        raise ValueError(
            f"Subject '{subject}' not found in SUBJECT_GROUPS. Available subjects: {list(SUBJECT_GROUPS.keys())}"
        )from None