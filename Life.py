from .EventManager import EventManager
from .AgeManager import AgeManager
from typing import Callable, Dict, List, Iterator
from .Talent import Talent
import os
import json
from .PropertyManager import PropertyManager
from .TalentManager import TalentManager
import random
import itertools

class HandlerException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class Life:
    talent_randomized = 20
    talent_choose = 5

    @staticmethod
    def load(datapath):
        with open(os.path.join(datapath, 'talents.json'), encoding='utf8') as fp:
            TalentManager.load(json.load(fp))
        with open(os.path.join(datapath, 'age.json'), encoding='utf8') as fp:
            AgeManager.load(json.load(fp))
        with open(os.path.join(datapath, 'events.json'), encoding='utf8') as fp:
            EventManager.load(json.load(fp))
        #with open(os.path.join(datapath, 'achievement.json'), encoding='utf8') as fp:
        #    EventManager.load(json.load(fp))

    def _init_managers(self):
        self.property : PropertyManager = PropertyManager(self)
        self.talent : TalentManager = TalentManager(self, self._rnd)
        self.age : AgeManager = AgeManager(self)
        self.event : EventManager = EventManager(self, self._rnd)

    def __init__(self, rnd=None):
        self._talent_inherit = None
        self._talenthandler : Callable[[List[Talent]], int] = None
        self._propertyhandler : Callable[[int], Dict[str, int]] = None
        self._errorhandler : Callable[[Exception], None] = None
        self._rnd = rnd or random.Random()
        self._init_managers()

    def restart(self,inhert_num=None):
        next_tms = self.property.TMS + 1
        if inhert_num:
            self._talent_inherit = self.talent.talents[inhert_num - 1]
        self._init_managers()
        self.property.TMS = next_tms

    def _prefix(self) -> Iterator[str]:
        yield f'【你{self.property.AGE}岁了，颜值:{self.property.CHR} 智力:{self.property.INT} 体力:{self.property.STR} 财富:{self.property.MNY} 快乐:{self.property.SPR}】'

    def setErrorHandler(self, handler: Callable[[Exception], None]) -> None:
        '''
        handler recv randomized talents
        ret chosen talent ids (will be called couple of times)
        '''
        self._errorhandler = handler
    def setTalentHandler(self, handler: Callable[[List[Talent]], int]) -> None:
        '''
        handler recv randomized talents
        ret chosen talent ids (will be called couple of times)
        '''
        self._talenthandler = handler
    def setPropertyhandler(self, handler: Callable[[int], List[int]]) -> None:
        '''
        handler recv total props
        ret prop alloc
        '''
        self._propertyhandler = handler

    def _alive(self): 
        return self.property.LIF > 0

    def run(self) -> Iterator[List[str]]:
        '''
        returns: information splited by day
        '''
        while self._alive():
            self.age.grow()
            for t in self.age.getTalents(): self.talent.addTalent(t)
            
            tal_log = self.talent.updateTalent()
            evt_log = self.event.runEvents(self.age.getEvents())

            yield list(itertools.chain(self._prefix(), evt_log, tal_log))

    def choose(self):
        talents = list(self.talent.genTalents(Life.talent_randomized))
        tdict = dict((t.id, t) for t in talents)

        while len(self.talent.talents) < Life.talent_choose:
            try:
                t = tdict[self._talenthandler(talents)]
                for t2 in self.talent.talents:
                    if t2.isExclusiveWith(t):
                        return False
                        # raise HandlerException(f'talent chosen conflict with {t2}')
                self.talent.addTalent(t)

                talents.remove(t)
                tdict.pop(t.id)
            except Exception as e:
                self._errorhandler(e)

        self.talent.updateTalentProp()

        while True:
            try:
                eff = self._propertyhandler(self.property.total)
                pts = [eff[k] for k in eff]
                if sum(pts) != self.property.total or max(pts) > 10 or min(pts) < 0:
                    return False
                    # raise HandlerException(f'property allocation points incorrect')
                self.property.apply(eff)
                break
            except Exception as e:
                self._errorhandler(e)

        return True