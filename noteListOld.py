import pitchMath
import stepwise, stochasticGrammar
import bangleize
import note
import random
import copy


class noteList:
    def __init__(self, updownfactor, grammarseed):
        self.updownfactor = updownfactor  # decimal from 0 to 1, percentage
        # higher percentange, each repetition of the grammar more likely to go down
        # dictates movement of each repetition of grammar - up or down
        self.grammarseed = grammarseed  # seed for the grammar
        self.B = bangleize.bangleize()

    def groupList(self, theList, factor, beats):
        currentList = theList
        measureFactor = factor
        measureBeats = beats
        currentCount = 0
        returnList = []
        subdivisions = measureFactor * measureBeats
        print(subdivisions)
        for location, item in enumerate(currentList):
            currentCount += item.dur
            print("currentCount", currentCount)
            if currentCount == subdivisions:
                if location != len(currentList) - 1:
                    currentList[location + 1].measureFlag = True
                alteredDuration = copy.deepcopy(currentList[location])
                alteredDuration.dur = alteredDuration.dur / measureFactor
                returnList.append(alteredDuration)
                currentCount = 0
            elif currentCount > subdivisions:
                currentNote = copy.deepcopy(currentList[location])
                print("logic for ties", currentCount, subdivisions)
                overflow = currentCount - subdivisions
                print("overflow", overflow)
                preTie = currentList[location].dur - overflow
                print("pre-tie", preTie)
                currentNote.dur = preTie / measureFactor
                currentNote.tieStart = True
                returnList.append(currentNote)
                tiedNote = copy.deepcopy(currentList[location])
                tiedNote.dur = overflow / measureFactor
                tiedNote.tieEnd = True
                tiedNote.measureFlag = True
                returnList.append(tiedNote)
                currentCount = overflow
            else:
                alteredDuration = copy.deepcopy(currentList[location])
                alteredDuration.dur = alteredDuration.dur / measureFactor
                returnList.append(alteredDuration)
        for item in returnList:
            print(item.dur)
        return returnList

    def getList(
        self,
        grammarType,
        startingOctave,
        startingNote,
        generations,
        startingPitch,
        rType,
        rhythm,
        factor,
        beats
    ):
        startingList = [note.notePC(startingOctave, startingNote)]

        # swg - stepwise grammar (stochastic stepwise grammar)
        # functions on scale degrees instead of pitches

        grammar = None

        if grammarType is "SWG":
            grammar = stepwise.grammar(
                self.updownfactor, self.grammarseed, startingPitch
            )
        elif grammarType is "SG":
            grammar = stochasticGrammar.grammar(self.updownfactor, self.grammarseed)
        else:
            raise Exception('Your grammar is unacceptable.')

        pitches = grammar.makeSystem(startingList, generations)

        rhythmList = list()
        if isinstance(rhythm, int):
            passMe = [random.randint(1, rhythm) for x in range(0, 100000)]
            for x in passMe:
                rhythmList.append(note.noteRhythm(dur=x))
            if rType is "ES":
                rhythms = self.B.eSpaced(rhythm[0], rhythm[1], rhythm[2])
            elif rType is "EU":
                rhythms = self.B.euclidize(rhythmList)
        elif isinstance(rhythm, list):
            for x in rhythm:
                rhythmList.append(note.noteRhythm(dur=x))
            if rType is "ES":
                rhythms = self.B.eSpaced(rhythm[0], rhythm[1], rhythm[2])
            elif rType is "EU":
                rhythms = self.B.euclidize(rhythmList)
        noteList = list()
        for r, p in zip(rhythms, pitches):
            x = note.note(r, p.octave, p.pc)
            x.stepName, x.alter, x.accidental = x.getNoteName(startingPitch)
            noteList.append(x)
            # print("before", noteList)
        noteList = self.groupList(noteList, factor, beats)
        # print("after", noteList)
        return noteList