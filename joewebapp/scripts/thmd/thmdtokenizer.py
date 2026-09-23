from enum import Enum, auto
import regex as re

class STType(Enum):
    HEADER = auto()
    SPEAKER_NAME = auto()
    DIALOGUE = auto()
    STAGE_DIRECTION = auto()
    NEW_LINE = auto()

class ScriptToken:
    def __init__(self, stType, value = ''):
        self.type = stType
        self.value = value

    def __str__(self):
        match self.type:
            case STType.HEADER:
                return self.value
            case STType.SPEAKER_NAME:
                return f"**{self.value}**: "
            case STType.DIALOGUE:
                return f"{self.value} "
            case STType.STAGE_DIRECTION:
                return f"_{self.value}_ "
            case STType.NEW_LINE:
                return "\n\n"

    def __repr__(self):
        return f"<{self.type}:{self.value}>"

def GetLineTokens(line):
    if not line.strip():
        return []

    if line[0] == '#':
        return [ScriptToken(STType.HEADER, line)]

    if (speaker := re.search(r'\*+([A-Z ]+)\*+', line)):
        return [ScriptToken(STType.SPEAKER_NAME, speaker.group(1)) , *GetLineTokens(line[speaker.span()[1]:])]

    if (stageDir := re.search(r'(?:_.+?_[A-Z (),.]*)+', line)):
        realStageDir = re.search(r'_\s*(.*)\s*_', stageDir.group())
        if realStageDir is None:
            return [ScriptToken(STType.DIALOGUE, line)]
        adjustedSpan = (
            stageDir.span()[0] + realStageDir.span(1)[0],
            stageDir.span()[0] + realStageDir.span(1)[1]
        )

        rawDirection = realStageDir.group(1)
        rawDirection = rawDirection.replace("_", "")

        return [
            *GetLineTokens(line[:adjustedSpan[0]-1]),
            ScriptToken(STType.STAGE_DIRECTION, rawDirection), 
            *GetLineTokens(line[adjustedSpan[1]+1:])
            ]

    if (stageDir := re.search(r'(\(.*?\))', line)):
        return [
            *GetLineTokens(line[:max(stageDir.span()[0]-1, 0)]),
            ScriptToken(STType.STAGE_DIRECTION, stageDir.group()), 
            *GetLineTokens(line[stageDir.span()[1]+1:])
            ]        

    line = line.lstrip(":").strip()

    return [ScriptToken(STType.DIALOGUE, line)] if line else []
    
def Tokenise(script):
    lines = script.split('\n')

    for line in lines:
        newtokens = GetLineTokens(line)
        if not newtokens:
            continue
        yield from newtokens + [ScriptToken(STType.NEW_LINE)]
