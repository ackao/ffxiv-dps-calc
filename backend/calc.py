"""
calc.py
Contains mathematical breakdowns of the stats used to calculate damage, and also contains a function
(CharacterStats: calc_damage) to estimate the DPS of a character given the party composition and gear stats.
"""
from __future__ import annotations
from enum import Enum, auto
import itertools
import math
from typing import ClassVar


class Stats(Enum):
    """
    Contains math factors for each individual stat.

    base: the base value for each stat
    m_factor: ???
    m_scalar: ???
    """
    MAINSTAT = (340, 165, 0)
    DET = (340, 130, 0)
    CRIT = (380, 200, 400)
    DH = (380, 1250, 0)
    SPEED = (380, 130, 0)
    TEN = (380, 100, 0)
    PIE = (340, 1, 0)
    GCD = (2500, 1, 0)  # in milliseconds
    PRECISION = (1000, 1, 0)  # defaulting to 3 digits of precision

    def __init__(self, base: int, m_factor: int, m_scalar: int):
        self.base = base
        self.m_factor = m_factor
        self.m_scalar = m_scalar


class Stat:
    """
    For each stat, gives a multiplier. Also holds the value of each stat.
    """
    def __init__(self, stat: Stats, value: int):
        """
        :param stat: from Stats enum.
        :param value: the current value of the stat.
        """
        self.stat = stat
        self.value = value

    def get_multiplier(self) -> float:
        """
        Calculates the multiplier based on the stat.
        :return: A floating point number representing the multiplier.
        """
        if self.stat == Stats.DH:
            return 1.25

        magic_num = 3300
        if self.stat == Stats.MAINSTAT:
            magic_num = 340  # don't ask me why dude
        delta = self.value - self.stat.base
        return self.stat.m_factor * delta // magic_num + self.stat.m_scalar


class ProbabalisticStat(Stat):
    """
    Derived from Stat class, used for stats that increase the chance of something happening such as critical hit and
    direct hit.

    p_factor: something
    p_scalar: something else
    """

    # Class variable to convert stats
    crit_convert: ClassVar[dict[Stats, tuple[int, int]]] = {
        Stats.CRIT: (200, 50),
        Stats.DH: (550, 0),
    }
    DEFAULT_PSTATS: ClassVar[tuple[int, int]] = (1, 0)

    def __init__(self, stat: Stats, value: int):
        """
        :param stat: from Stats enum.
        :param value: the current value of the stat.
        :param p_factor: ???
        :param p_scalar: ???
        """
        super().__init__(stat, value)
        self.p_factor, self.p_scalar = ProbabalisticStat.crit_convert.get(stat, ProbabalisticStat.DEFAULT_PSTATS)

    def get_p(self) -> float:
        """
        calculates p?
        :return: returns p?
        """
        delta = self.value - self.stat.base
        return (self.p_factor * delta // 3300 + self.p_scalar) / Stats.PRECISION.base


class CharacterStats:
    """
    The main class where damage is calculated. Initialized by providing the character's stats.
    """

    # TODO: Consider breaking out a lot of these parameters into a dict since that's a lot of params
    def __init__(self, job: Jobs, wd: int, mainstat: int, det: int, crit: int, dh: int, speed: int, ten: int, pie: int):
        self.job = job
        self.wd = wd
        self.mainstat = Stat(Stats.MAINSTAT, mainstat)
        self.det = Stat(Stats.DET, det)
        self.crit = ProbabalisticStat(Stats.CRIT, crit)
        self.dh = ProbabalisticStat(Stats.DH, dh)
        self.speed = Stat(Stats.SPEED, speed)
        self.ten = Stat(Stats.TEN, ten)
        self.pie = Stat(Stats.PIE, pie)

    @classmethod
    def truncate(cls, val: int, precision=1000) -> float:
        return (precision + val) / precision

    @classmethod
    def multiply_and_truncate(cls, val, factor, precision=1000):
        return math.floor(val * cls.truncate(factor, precision))

    @classmethod
    def apply_stat(cls, damage, stat):
        return cls.multiply_and_truncate(damage, stat.get_multiplier())

    def calc_damage(self, potency: int, comp: Comp, is_dot=False, crit_rate=None, dh_rate=None) -> float:
        """
        Calculates the estimated DPS based on the team composition and current character stats
        :param potency: Potency calculated on expected rotation
        :param comp: Team composition.
        :param is_dot: ???
        :param crit_rate: ???
        :param dh_rate: ???
        :return: the DPS number
        """

        # modify mainstat according to number of roles
        modified_mainstat = Stat(Stats.MAINSTAT, math.floor(self.mainstat.value * (1 + 0.01 * comp.n_roles)))

        # damage effect of non-probabalistic stats
        damage = potency * (self.wd + (340 * self.job.job_mod // 1000)) * (
                    100 + modified_mainstat.get_multiplier()) // 100  # cursed tbh
        damage = self.apply_stat(damage, self.det)
        damage = self.apply_stat(damage, self.ten)
        if is_dot:
            damage = self.apply_stat(damage, self.speed)

        damage //= 100  # why? i do not know. cargo culted

        # damage effect of job traits / stance
        # todo: pull out traits
        if self.job.role == Roles.HEALER:
            damage = math.floor(damage * 1.3)  # magic and mend

        # todo: effect of raid buffs

        # damage effect of probabalistic stats
        crit_damage = self.apply_stat(damage, self.crit)
        dh_damage = damage * self.dh.stat.m_factor // 1000
        cdh_damage = crit_damage * self.dh.stat.m_factor // 1000

        # use expected crit rate based on stats if none is supplied
        if not crit_rate:
            crit_rate = self.crit.get_p()
        if not dh_rate:
            dh_rate = self.dh.get_p()

        # apply party crit/dh buffs
        for buff in comp.raidbuffs:
            if buff in Buffs.crit_buffs():
                crit_rate += buff.avg_buff_effect()
            elif buff in Buffs.dh_buffs():
                dh_rate += buff.avg_buff_effect()

        cdh_rate = crit_rate * dh_rate
        normal_rate = 1 - crit_rate - dh_rate + cdh_rate
        return damage * normal_rate + crit_damage * (crit_rate - cdh_rate) + dh_damage * (
                    dh_rate - cdh_rate) + cdh_damage * cdh_rate


class Roles(Enum):
    """
    An enum used to calculate the stat bonuses for having one of each role.
    """
    TANK = auto()
    HEALER = auto()
    MELEE = auto()
    RANGED = auto()
    CASTER = auto()


class Buffs(Enum):
    """
    List of all buffs in the game. Each buff has three parameters:

    multiplier: The amount that the damage of the ability is increased
    duration_sec: How long the buff lasts, in seconds.
    cooldown_sec: How long until the buff may be used again, in seconds.

    """
    # aoe
    CHAIN = (0.1, 15, 120)
    DIV = (0.06, 15, 120)  # 3 seal div
    TRICK = (0.05, 15, 60)
    LITANY = (0.1, 20, 180)
    BROTHERHOOD = (0.05, 15, 90)
    BV = (0.2, 20, 180)
    BARD_CRIT = (0.02, 30, 80)
    BARD_DH = (0.03, 20, 80)
    TECH = (0.05, 20, 120)
    DEVOTION = (0.05, 15, 180)
    EMBOLDEN = (0.1, 20, 120)  # need to handle buff decay
    # single target
    CARD = (0.06, 15, 30)
    LORD_LADY = (0.08, 15, 30)
    DSIGHT_SELF = (0.1, 20, 120)
    DSIGHT_OTHER = (0.05, 20, 120)
    DEVILMENT = (0.2, 20, 120)

    # todo: should probably add standard, personal tank buffs

    def __init__(self, multiplier: float, duration_sec: int, cooldown_sec: int):
        self.multiplier = multiplier
        self.duration_sec = duration_sec
        self.cooldown_sec = cooldown_sec

    @classmethod
    def crit_buffs(cls):
        return {cls.CHAIN, cls.LITANY, cls.DEVILMENT, cls.BARD_CRIT}

    @classmethod
    def dh_buffs(cls):
        return {cls.BV, cls.BARD_DH, cls.DEVILMENT}

    def avg_buff_effect(self) -> float:
        """Gives the dps expected from a buff"""
        return self.multiplier * self.duration_sec / self.cooldown_sec


class Jobs(Enum):
    """
    Contains job related info.

    job_mod: The bonus given to the main stat.
    role: The Role of the job
    raidbuff: A list of all raidbuffs that the job has

    job modifiers from https://www.akhmorning.com/allagan-studies/modifiers/
    """
    SCH = (115, Roles.HEALER, [Buffs.CHAIN])
    AST = (115, Roles.HEALER, [Buffs.DIV])
    WHM = (115, Roles.HEALER, [])
    PLD = (110, Roles.TANK, [])
    WAR = (110, Roles.TANK, [])
    DRK = (110, Roles.TANK, [])
    GNB = (110, Roles.TANK, [])
    NIN = (110, Roles.MELEE, [Buffs.TRICK])
    DRG = (115, Roles.MELEE, [Buffs.LITANY])
    MNK = (110, Roles.MELEE, [Buffs.BROTHERHOOD])
    SAM = (112, Roles.MELEE, [])
    MCH = (115, Roles.RANGED, [])
    DNC = (115, Roles.RANGED, [Buffs.TECH])
    BRD = (115, Roles.RANGED, [Buffs.BV, Buffs.BARD_CRIT, Buffs.BARD_DH])
    SMN = (115, Roles.CASTER, [Buffs.DEVOTION])
    BLM = (115, Roles.CASTER, [])
    RDM = (115, Roles.CASTER, [Buffs.EMBOLDEN])

    def __init__(self, job_mod: int, role: Roles, raidbuff: list[Buffs]):
        self.job_mod = job_mod
        self.role = role
        self.raidbuff = raidbuff


class Comp:
    """
    The party composition.

    jobs: A list of all jobs in the party (can contain duplicates).
    raidbuffs: All unique raidbuffs in the party.
    n_roles: All unique roles in the party.
    """

    def __init__(self, jobs: list[Jobs]):
        self.jobs = jobs
        self.raidbuffs = set(itertools.chain.from_iterable([job.raidbuff for job in jobs]))
        self.n_roles = len(set([job.role for job in jobs]))
