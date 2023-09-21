import os
import hjson
import sys
sys.path.append('src')
from Utility import get_filename

# builders
from Randomizer import Steam, Rando
from Shuffler import Shuffler, no_weights
from JP import JPCosts, AdvJPNerf
from Weapons import Weapons
from Support import Support
from Command import Command
from AbilityWeapons import AbilityWeapons
from AbilitySP import AbilitySP
from AbilityPower import AbilityPower
from JobStats import JobStatsFair, JobStatsRandom
from Treasures import Treasures
from ProcessedSpecies import Process
from Shields import Shields
from Battles import *
from EnemyGroups import *
from PathActions import *
from Bosses import *
from Nothing import Nothing
from Shuffler import no_weights
from SpurningRibbon import SpurningRibbon
from Guilds import Guilds, shuffle_requirements
from Command import separate_advanced_commands, separate_divine, separate_ex_abilities
from Support import separate_advanced_support, evasive_maneuvers_first
from Treasures import separate_chapter
from Events import InitialEvents, formation_menu_on, protagonist_unlocked
from SkipTutorials import SkipTutorials
from EventsAndItems import EventsAndItems


# Set all builder stuff using the settings dictionary
# Done like this to facilitate testing via scripts
def builder_setup(settings):
    with open(get_filename('json/gui.json'), 'r') as file:
        options = hjson.load(file)

    # Track what settings are found when looping over the gui json
    # Important to keep just in case new structures get added
    settings_used = {k:False for k in settings.keys()}
    del settings_used['release']
    del settings_used['seed']

    for tab, tab_val in options.items():
        for section, section_val in tab_val.items():
            for key, value in section_val.items():
                assert key in settings, f"setting {key} missing"
                set_option(value, settings[key])
                assert settings_used[key] == False
                settings_used[key] = True
                if 'indent' in value:
                    for ki, vi in value['indent'].items():
                        assert ki in settings, f"setting {ki} missing"
                        set_option(vi, settings[ki])
                        assert settings_used[ki] == False
                        settings_used[ki] = True

    if not all(settings_used.values()):
        for k, v in settings_used.items():
            if not v:
                print('setting', k, 'not used')
        sys.exit('not all settings used')
    

def set_option(option, setting):
    cls = eval(option['class'])
    attr = option['attribute']

    if 'builder' in option:
        bldr = eval(option['builder'])
        dflt = eval(option['default'])
        if isinstance(setting, bool):
            if setting:
                setattr(cls, attr, bldr)
            else:
                setattr(cls, attr, dflt)
        elif isinstance(setting, str):
            assert 'optionsAttr' in option
            o_attr = option['optionsAttr']
            o_val = option['options']
            if setting not in o_val:
                sys.exit(f"option {setting} not in {o_val}")
            setattr(cls, attr, bldr)
            setattr(bldr, o_attr, setting)
        else:
            sys.exit(f'Not setup for {setting}')
            
    if 'type' in option and option['type'] == 'SpinBox':
        if 'varType' in option:
            assert option['varType'] == 'double'
            to_type = float
        else:
            to_type = int
        value = to_type(setting)
        setattr(cls, attr, value)
