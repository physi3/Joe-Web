from .thmdtokenizer import STType
import regex as re

numberStrings = [
    "zero", "one", "two", "three", "four",
    "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen",
    "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",
    "twenty"
]


def get_referenced_characters(content):
    return list(set(re.findall(r"\b[A-Z]{2,}(?:\s+[A-Z]{2,})?\b", content)))

class Script:
    def __init__(self, scriptLines):
        self.scriptLines = scriptLines
        
        self.headers = [(h, i) for i, h in enumerate(self.scriptLines) if type(h) is Header]
        self.speakers = list(set([l.speaker for l in self.scriptLines if type(l) is DialogueLine]))

    def ReferencedCharacters(self):
        referencedCharacters = []
        for l in self.scriptLines:
            referencedCharacters.extend(l.ReferencedCharacters())
        return list(set(referencedCharacters))

    def FindActStart(self, act):
        for h, i in self.headers:
            if h.hType == 1 and h.index == act:
                return i
        return -1

    def GetAct(self, act):
        start = self.FindActStart(act)
        if start == -1:
            raise ValueError(f"No Act {act} in script")
        end = self.FindActStart(act + 1)
        if end == -1:
            return Script(self.scriptLines[start:])
        return Script(self.scriptLines[start:end])
    
    def FindSceneStart(self, act, scene, singleAct = False):
        if singleAct:
            actScript = self
        else:
            actScript = self.GetAct(act)

        for h, i in actScript.headers:
            if h.hType == 2 and h.index == scene:
                return i
        return -1

    def GetScene(self, act, scene):
        actScript = self.GetAct(act)

        start = actScript.FindSceneStart(act, scene, True)
        if start == -1:
            raise ValueError(f"No Act {act}, Scene {scene} in script")
        end = actScript.FindSceneStart(act, scene + 1, True)
        if end == -1:
            return Script(actScript.scriptLines[start:])
        return Script(actScript.scriptLines[start:end])

    @classmethod
    def Parse(cls, tokens):
        scriptLines = []
        tokens = list(tokens)

        i = 0
        while i < len(tokens):
            token = tokens[i]

            try:
                match token.type:
                    case STType.HEADER:
                        scriptLines.append(Header(token))
                    case STType.STAGE_DIRECTION:
                        scriptLines.append(StageDirection(token))
                    case STType.SPEAKER_NAME:
                        dialogueTokens = [token]

                        while i + 1 < len(tokens):
                            i += 1
                            token = tokens[i]

                            j = i + 1
                            nextTokenType = STType.NEW_LINE

                            while j < len(tokens) and (nextTokenType := tokens[j].type) == STType.NEW_LINE:
                                j += 1

                            if token.type == STType.NEW_LINE:
                                if nextTokenType in [STType.DIALOGUE, STType.STAGE_DIRECTION]:
                                    dialogueTokens.append(token)
                            elif token.type == STType.DIALOGUE:
                                dialogueTokens.append(token)
                            elif token.type == STType.STAGE_DIRECTION and (nextTokenType in [STType.DIALOGUE, STType.STAGE_DIRECTION] or tokens[i - 1].type != STType.NEW_LINE):
                                dialogueTokens.append(token)
                            else:
                                i -= 1
                                break
                        
                        scriptLines.append(DialogueLine(dialogueTokens))
                        
                    case STType.DIALOGUE:
                        print(f"Misplaced dialogue: \"{token}\" at {i}")

                i += 1

            except Exception as e:
                print(f"Issue parsing token: {repr(token)}, index: {i}")
                raise e

        return cls(scriptLines)

    def Markdown(self):
        return "\n\n".join(l.Markdown() for l in self.scriptLines)

    def SceneIndices(self):
        act = 0
        scene = 0
        for h in self.headers:
            if h[0].hType == 1:
                act = h[0].index
            elif h[0].hType == 2:
                scene = h[0].index
                yield (act, scene)

    def __add__(self, other):
        return Script(self.scriptLines + other.scriptLines)

    def HTML(self, template=None):
        if template is None:
            template = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Script</title>
    <link rel="stylesheet" href="style.css">
    <meta charset="UTF-8">
  </head>
  <body>
    {content}
  </body>
</html>    
            """

        content = "\n".join(l.HTML() for l in self.scriptLines)

        return template.format(content=content)

class ScriptLine:
    def Markdown(self):
        raise NotImplementedError()
    
    def HTML(self):
        raise NotImplementedError()

    def ReferencedCharacters(self):
        return []

class Header(ScriptLine):
    def __init__(self, token):
        self.hType = len(token.value.split(" ")[0]) # 1 - Title, 2 - Scene
        
        content = token.value[self.hType + 1:]
        
        self.index = 0
        self.title = ""
        if self.hType == 1:
            self.title = content
        else:
            splt = content.split(": ")

            # Find index
            indexStr = " ".join(splt[0].split(" ")[1:]).lower()
            if indexStr.isnumeric():
                self.index = int(indexStr)
            elif indexStr in numberStrings:
                self.index = numberStrings.index(indexStr)
            else:
                raise Exception(f"Issue parsing header: {token.value}")

            # Find title
            if len(splt) > 1:
                self.title = splt[1]

    def String(self):
        match self.hType:
            case 1:
                return self.title
            case 2:
                return f"Scene {numberStrings[self.index].capitalize()}" + (f": {self.title}" if self.title else "")
        
    def Markdown(self):
        return f"{"#"*self.hType} {self.String()}"
    
    def TypeString(self):
        return [None, "title", "scene"][self.hType]

    def HTML(self):
        return f"<h{self.hType} class=\"{self.TypeString()}\">{self.String()}</h{self.hType}>"

class StageDirection(ScriptLine):
    def __init__(self, token):
        self.content = token.value
        self.referencedCharacters = get_referenced_characters(self.content)
    
    def Markdown(self):
        return f"_{self.content}_ "
    
    def ReferencedCharacters(self):
        return self.referencedCharacters

    def HTML(self):
        return f"<i class=\"stage-direction {' '.join(self.ReferencedCharacters())}\">{self.content} </i>"

class Dialogue(ScriptLine):
    def __init__(self, token):
        self.content = token.value

    def Markdown(self):
        return f"{self.content} "
    
    def HTML(self):
        return f"{self.content} "

class LineBreak(ScriptLine):
    def __init__(self, token):
        pass

    def Markdown(self):
        return "\n\n"

    def HTML(self):
        return f"<br>"

class DialogueLine(ScriptLine):
    def __init__(self, tokens):
        if tokens[0].type != STType.SPEAKER_NAME:
            raise Exception("DialogueLine doesn't begin with speaker")

        self.speaker = tokens[0].value
        self.subLines = []
        for token in tokens[1:]:
            match token.type:
                case STType.DIALOGUE:
                    self.subLines.append(Dialogue(token))
                case STType.STAGE_DIRECTION:
                    self.subLines.append(StageDirection(token))
                case STType.NEW_LINE:
                    self.subLines.append(LineBreak(token))
                case _:
                    raise Exception("Wrong token type passed to DialogueLine")
        
        while type(self.subLines[-1]) is LineBreak:
            self.subLines.pop(-1)
        
    def WordCount(self):
        return sum([len(l.content.split(" ")) for l in self.subLines if type(l) is Dialogue])

    def Markdown(self):
        return f"**{self.speaker}**: " + "".join(l.Markdown() for l in self.subLines)

    def HTML(self):
        return f"<div class=\"dialogue {self.speaker}\"><p class=\"speaker\">{self.speaker}:</p><p>" + "".join(l.HTML() for l in self.subLines) + "</p></div>"

    def ReferencedCharacters(self):
        referencedCharacters = [self.speaker]
        for l in self.subLines:
            referencedCharacters.extend(l.ReferencedCharacters())
        return list(set(referencedCharacters))