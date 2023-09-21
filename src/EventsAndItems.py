import os
import sys
import hjson
import random
from Manager import Manager
from Graph import Graph, Edge, Node
from Utility import get_filename
from DataJson import DataJsonFile
from copy import deepcopy
import pickle
import lzma

from FLAGS import NEVERUSE, TESTFLAG, DUMMY


class EventsAndItems:
    include_main_story = False
    include_galdera = False
    include_pcs = False
    include_guilds = False
    include_ex_abil = False
    include_guard = False
    include_assassins = False
    include_ships_spawn = False
    include_guild_spawn = False
    include_altar_spawn = False
    include_assassins_spawn = False
    num_start_pc = 1

    @classmethod
    def any_on(cls):
        return cls.include_main_story
        # return cls.include_main_story \
        #     or cls.include_pcs \
        #     or cls.include_guilds \
        #     or cls.include_ex_abil \
        #     or cls.include_guard \
        #     or cls.include_assassins \
        #     or cls.include_ships_spawn \
        #     or cls.include_guild_spawn \
        #     or cls.include_altar_spawn \
        #     or cls.include_assassins_spawn

    def __init__(self, outpath):
        self.outpath = outpath
        self.reset()

    def reset(self):
        self.always_have = []
        self.other_pcs = []
        self.rando_cand = set()
        self.all_slots = set()
        self.rando_slots = set()
        self.edges = []
        self.node_dict = {}
        self.graph = Graph()
        self.rando_map = {} 
        self.rando_map_inv = {} 

    def run(self):
        self._load_files()
        self._add_pcs()
        self._shuffle()
        self._finalize()

    def _load_files(self):
        with lzma.open(get_filename('lzma/logic.xz'), 'r') as file:
            logic = pickle.load(file)

        def add_to_data(filename, option=True):
            data = hjson.loads(logic[filename])

            if option: # "on" by default
                self.rando_cand.update(data['candidates'])
                self.rando_slots.update(data['slots'])
                self.all_slots.update(data['slots'])
            else:
                self.all_slots.update(data['slots'])
                if data['off']:
                    self.always_have.append(data['off'])
            self.edges.extend(data['edges'])

            for start, dest_data in data['edges'].items():
                if start not in self.node_dict:
                    self.node_dict[start] = Node(start)
                for dest, values in dest_data.items():
                    if dest not in self.node_dict:
                        self.node_dict[dest] = Node(dest, items=values['get'])
                    else:
                        assert self.node_dict[dest].vanilla == values['get'] 

                    self.graph.add_edge(self.node_dict[start], self.node_dict[dest], values['reqs'])

        #### MANDATORY FILES ####
        add_to_data('json/logic/start.json')
        add_to_data('json/logic/region.json')
        add_to_data('json/logic/region_ocean.json')
        add_to_data('json/logic/region_hinoeuma.json')
        add_to_data('json/logic/region_wildlands.json')
        add_to_data('json/logic/region_harbourlands.json')
        add_to_data('json/logic/region_leaflands.json')
        add_to_data('json/logic/region_crestlands.json')
        add_to_data('json/logic/region_winterlands.json')
        add_to_data('json/logic/region_brightlands.json')
        add_to_data('json/logic/region_totohaha.json')
        add_to_data('json/logic/items.json')
        add_to_data('json/logic/rusty_weapons.json')

        #### OPTIONAL FILES ####
        add_to_data('json/logic/altars.json', option=self.include_altar_spawn) # SPAWNING altars, NOT ex abilities from altars
        add_to_data('json/logic/ex_abilities.json', option=self.include_ex_abil) # Ex Abil from BOTH altars and final chapters
        add_to_data('json/logic/assassins_hire.json', option=self.include_assassins)
        add_to_data('json/logic/assassins_spawn.json', option=self.include_assassins_spawn)
        add_to_data('json/logic/guilds.json', option=self.include_guilds)
        add_to_data('json/logic/guilds_spawn.json', option=self.include_guild_spawn)
        add_to_data('json/logic/blocks.json', option=self.include_guard)
        add_to_data('json/logic/ships.json', option=self.include_ships_spawn)

        # THE STORY STUFF -- should have the same option for all
        add_to_data('json/logic/story_recruit.json', option=self.include_main_story)
        add_to_data('json/logic/story_hikari.json', option=self.include_main_story)
        add_to_data('json/logic/story_ochette.json', option=self.include_main_story)
        add_to_data('json/logic/story_castti.json', option=self.include_main_story)
        add_to_data('json/logic/story_partitio.json', option=self.include_main_story)
        add_to_data('json/logic/story_temenos.json', option=self.include_main_story)
        add_to_data('json/logic/story_osvald.json', option=self.include_main_story)
        add_to_data('json/logic/story_throne.json', option=self.include_main_story)
        add_to_data('json/logic/story_agnea.json', option=self.include_main_story)
        add_to_data('json/logic/crosspath_ah.json', option=self.include_main_story)
        add_to_data('json/logic/crosspath_oc.json', option=self.include_main_story)
        add_to_data('json/logic/crosspath_op.json', option=self.include_main_story)
        add_to_data('json/logic/crosspath_tt.json', option=self.include_main_story)
        add_to_data('json/logic/flames.json', option=self.include_main_story)

        # GALDERA SIDEQUESTS
        add_to_data('json/logic/sidequest_the_travelers_bag.json', option=self.include_galdera)
        add_to_data('json/logic/sidequest_procuring_peculiar_tomes.json', option=self.include_galdera)
        add_to_data('json/logic/sidequest_from_the_far_reaches_of_hell.json', option=self.include_galdera)
        add_to_data('json/logic/sidequest_a_gate_between_worlds.json', option=self.include_galdera)

        # Turn all slots on
        for slot in self.rando_slots:
            assert slot in self.node_dict, slot
            self.node_dict[slot].is_slot = True


    def _add_pcs(self):
        starting_characters = {
            'Hikari': 'start_hikari',
            'Ochette': 'start_ochette',
            'Castti': 'start_castti',
            'Partitio': 'start_partitio',
            'Temenos': 'start_temenos',
            'Osvald': 'start_osvald',
            'Throne': 'start_throne',
            'Agnea': 'start_agnea',
        }

        self.start_pc = random.sample(sorted(starting_characters.keys()), 1)[0]
        self.always_have.append(starting_characters[self.start_pc])
        self.always_have.append(starting_characters[self.start_pc].replace('start', 'unlock'))

        self.other_pcs = []
        if self.num_start_pc > 1:
            pcs = list(starting_characters.keys())
            pcs.remove(self.start_pc)
            other_pcs = random.sample(pcs, self.num_start_pc-1)
            for pc in other_pcs:
                x = starting_characters[pc].replace('start', 'unlock')
                self.other_pcs.append(x)
                self.always_have.append(x)

    def _shuffle(self):
        start = self.node_dict['START']
        self.graph.reset()
        self.graph.store_node_costs(start)
        self.graph.shuffle(start, self.rando_cand, self.always_have)
        self.rings = self.graph.get_rings(self.always_have)

        self.rando_map = {}
        self.rando_map_inv = {}
        self.rando_empty = []
        for node in sorted(self.graph.nodes):
            if node.is_slot:
                self.rando_map[node.name] = sorted(node.slots)
                if not node.slots:
                    self.rando_empty.append(node.name)
                for c in node.slots:
                    assert c not in self.rando_map_inv
                    self.rando_map_inv[c] = node.name


    def _finalize(self):
        fill_everything(self.rando_map, self.rando_map_inv, self.other_pcs)
        self._print_shuffler()
        self._print_rings()
        self._print_main_character()
        # self.graph.plot(f'{self.outpath}/graph.png')

    def _print_main_character(self):
        outfile = os.path.join(self.outpath, 'STARTING_CHARACTER.txt')
        with open(outfile, 'w') as file:
            file.write(self.start_pc)


    def _print_rings(self):
        outfile = os.path.join(self.outpath, 'spoiler_walkthrough.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        with open(get_filename('json/candidates.json'), 'r', encoding='utf-8') as file:
            candidates_data = hjson.load(file)
        with open(get_filename('json/slots.json'), 'r', encoding='utf-8') as file:
            slots_data = hjson.load(file)

        ring_num = 0
        for ring in self.rings:
            if not ring: continue
            ring_num += 1
            print('Group', ring_num)
            for node in ring:
                slot = slots_data[node.name]
                print('    ', slot[0]['description'])
                for cand in node.slots:
                    try:
                        desc = candidates_data[cand]['name']
                    except:
                        desc = ' '.join([ci.capitalize() for ci in cand.split('_')])
                    print('          ', desc)
                print('')
            print('')
            print('')

        sys.stdout = sys.__stdout__

    def _print_shuffler(self):
        outfile = os.path.join(self.outpath, 'spoiler_events_and_items.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        with open(get_filename('json/candidates.json'), 'r', encoding='utf-8') as file:
            candidates_data = hjson.load(file)
        with open(get_filename('json/slots.json'), 'r', encoding='utf-8') as file:
            slots_data = hjson.load(file)

        max_size = 0
        cand_to_slot = {}
        for cand in sorted(self.rando_map_inv.keys()):
            try:
                key = candidates_data[cand]['name']
            except:
                key = ' '.join([ci.capitalize() for ci in cand.split('_')])
            slot = self.rando_map_inv[cand]
            cand_to_slot[key] = slots_data[slot][0]['description']
            max_size = max(max_size, len(key))

        for cand, slot in cand_to_slot.items():
            print('  ', cand.ljust(max_size, ' '), ' <-- ', slot)

        sys.stdout = sys.__stdout__


class Tracker:
    def __init__(self, value):
        self._value = value

    @classmethod
    def data_factory(cls, data, key):
        value = 0
        for d in data:
            v = getattr(d, key)
            value = max(value, v)
        return cls(value)

    @property
    def value(self):
        self._value += 1
        return self._value


class Candidate:
    all_scripts = pickle.load(lzma.open(get_filename('lzma/scripts.xz'), 'r'))

    def __init__(self, basename, name):
        self.script = self.load_script(basename)
        self.basename = basename
        self.name = name

    @property
    def flag(self):
        sys.exit('not flag set for Candidate:', self.basename, self.name)

    @classmethod
    def load_script(cls, basename):
        data = cls.all_scripts[f'{basename}.json']
        return DataJsonFile(data)


class NewScript(Candidate):
    def __init__(self, basename, name, flag):
        super().__init__(basename, name)
        self._flag = flag

    @property
    def flag(self):
        return self._flag

    @classmethod
    def data_factory(cls, basename, data):
        return cls(basename, data['name'], data['flag'])



class SlotManager:
    def __init__(self):
        self.slots = {}
        self.nicknames = {}
        self.slots_filename = {}

    def add_slot(self, filename, name, indices, remove):
        if name not in self.slots:
            self.slots[name] = {}
        assert filename not in self.slots[name]
        self.slots[name][filename] = Slot(filename, indices, remove)
        assert filename not in self.slots_filename
        self.slots_filename[filename] = self.slots[name][filename]

    def get_slot(self, name, filename=None):
        if filename:
            return self.slots[name][filename]
        assert len(self.slots[name]) == 1, f'{name} has multiple files; not sure which to return!'
        return self.get_slot_list(name)[0]

    def get_slot_list(self, name):
        return list(self.slots[name].values())

    def reset(self):
        for slots in self.slots.values():
            for s in slots.values():
                s.reset()

    def finalize(self):
        for slots in self.slots.values():
            for s in slots.values():
                s.insert()


class Slot:
    def __init__(self, filename, indices, remove):
        self.script = Manager.get_json(filename)
        self.filename = filename
        self.indices = sorted([self._positive_index(i) for i in indices])
        remove = sorted([self._positive_index(i) for i in remove], reverse=True)
        for ri in remove:
            self.remove_command(ri)
        self.subscripts = {}

    def reset(self):
        self.subscripts = {}

    def _positive_index(self, index):
        if index < 0:
            return len(self.script.json_list) + index
        return index

    def remove_command(self, index):
        index = self._positive_index(index)
        self.script.remove_command(index)
        # Update indexing to account for any removed commands
        for i, idx in enumerate(self.indices):
            if idx > index:
                self.indices[i] -= 1

    def add_subscript(self, subscript):
        if subscript not in self.subscripts:
            self.subscripts[deepcopy(subscript)] = False

    def insert(self):
        for subscript, inserted in self.subscripts.items():
            if not inserted:
                self.subscripts[subscript] = True
                for i, index in enumerate(self.indices):
                    self.script.insert_script(deepcopy(subscript), index)
                    offset = len(subscript.json_list)
                    for j in range(i+1, len(self.indices)):
                        self.indices[j] += offset
        


def fill_everything(rando_map, rando_map_inv, other_pc):
    slot_manager = SlotManager()
    candidates = {}

    # Load all data
    with open(get_filename('json/candidates.json'), 'r', encoding='utf-8') as file:
        events = hjson.load(file)

    # Extract all files used
    items = Manager.get_table('ItemDB')
    gameText = Manager.get_table('GameTextEN')
    tutorial_flags = Manager.get_table('TutorialFlagPart')

    placement = Manager.get_table('PlacementData')
    npc_data = Manager.get_table('NPCData')
    main_story = Manager.get_table('MainStory')
    purchase = Manager.get_table('PurchaseItemTable')

    def add_scripts(candname, slotname):
        replacement = candidates[candname]
        for slot in slot_manager.get_slot_list(slotname):
            slot.add_subscript(replacement.script)

    def add_scripts_notcand(replacement, slotname):
        for slot in slot_manager.get_slot_list(slotname):
            slot.add_subscript(replacement)

    #################
    # ADD NEW ITEMS #
    #################

    track_index = Tracker(1000)
    track_item_id = Tracker.data_factory(items, 'ID')
    track_text_id = Tracker.data_factory(gameText, 'Id')

    def add_item(data):
        if data['item_key'] in items.keys:
            print(data['item_key'], 'already exists in the database')
            return

        base_item = 'ITM_TRE_END_2B_0010'
        base_name = 'TX_NA_ITM_TRE_END_2B_0010'
        base_desc = 'TX_CO_ITM_TRE_END_2B_0010'
        item_key = data['item_key']
        name_key = data['name_key']
        desc_key = data['desc_key']
        name = data['name']
        desc = data['description']
        
        # New item's name
        gameText.duplicate_data(base_name, name_key)
        obj_name = getattr(gameText, name_key)
        obj_name.Text = name
        obj_name._data['Text'].string_2 = name_key
        obj_name.Id = track_text_id.value

        # New item's description
        gameText.duplicate_data(base_desc, desc_key)
        obj_desc = getattr(gameText, desc_key)
        obj_desc.Text = desc
        obj_desc._data['Text'].string_2 = desc_key
        obj_desc.Id = track_text_id.value

        # New item
        items.duplicate_data(base_item, item_key)
        obj_item = getattr(items, item_key)
        obj_item.ID = track_item_id.value
        obj_item.ItemNameID = name_key
        obj_item.DetailTextID = desc_key
        obj_item.SpecialItemLabel = 'None'

        return item_key

    for unlock, data in events.items():
        add_item(data)

    ##################
    # LOAD ALL SLOTS #
    ##################
    
    with open(get_filename('json/slots.json'), 'r', encoding='utf-8') as file:
        slot_data = hjson.load(file)
        for slotname, slots in slot_data.items():
            for data in slots:
                filename = data['filename']
                insert = data['insert']
                remove = data['remove']
                slot_manager.add_slot(filename, slotname, insert, remove)

    #######################
    # LOAD ALL CANDIDATES #
    #######################

    # scripts to insert "new" items
    for unlock, data in events.items():
        assert unlock not in candidates, unlock
        candidates[unlock] = NewScript.data_factory(f'scripts/generated/{unlock}', data)

    # scripts to insert existing items
    existing = [
        # PC joins party - these might require keys (using NEVERUSE for now)
        'unlock_hikari', 
        'unlock_ochette', 
        'unlock_castti', 
        'unlock_partitio', 
        'unlock_temenos', 
        'unlock_osvald', 
        'unlock_throne', 
        'unlock_agnea',

        # EX ability - these should never require keys (go with NEVERUSE)
        'unlock_hikari_ex_abil_1',
        'unlock_ochette_ex_abil_1',
        'unlock_castti_ex_abil_1',
        'unlock_partitio_ex_abil_1',
        'unlock_temenos_ex_abil_1',
        'unlock_osvald_ex_abil_1',
        'unlock_throne_ex_abil_1',
        'unlock_agnea_ex_abil_1',
        'unlock_hikari_ex_abil_2',
        'unlock_ochette_ex_abil_2',
        'unlock_castti_ex_abil_2',
        'unlock_partitio_ex_abil_2',
        'unlock_temenos_ex_abil_2',
        'unlock_osvald_ex_abil_2',
        'unlock_throne_ex_abil_2',
        'unlock_agnea_ex_abil_2',

        # Scent of Commerce
        'unlock_grand_terry',
        'unlock_manuscript',

        # Foreign assassings
        'unlock_hire_foreign_assassins',
    ]

    for unlock in existing:
        assert unlock not in candidates, f'1 {unlock}'
        candidates[unlock] = Candidate(f'scripts/{unlock}', unlock)

    ##################
    # FINALIZE SLOTS #
    ##################

    ## THIS SCRIPT IS A PATCH, NOT A CANDIDATE!
    if EventsAndItems.include_main_story:
        patch = Candidate.load_script(f'scripts/scent_of_commerce_boat_truncated')
        slot = slot_manager.get_slot('finish_soc_grand_terry')
        slot.script.insert_script(patch, 0) # Manually do this starting at 0
        slot.index = 11

    #############
    # TUTORIALS #
    #############

    new_flags = set()
    for entry in tutorial_flags:
        new_flags.add(entry.TutorialListFlag)
        new_flags.add(entry.TutorialOpenedFlag)
        entry.TutorialListFlag = DUMMY
        entry.TutorialOpenedFlag = DUMMY
    new_flags.remove(0)
    if DUMMY in new_flags:
        new_flags.remove(DUMMY)

    initial_scripts = [
        'MS_KEN_10_0100', 'MS_KAR_10_0200', 'MS_KUS_10_0100', 'MS_SHO_10_0100',
        'MS_SIN_10_0100', 'MS_GAK_10_0100', 'MS_TOU_10_0100', 'MS_ODO_10_0100',
    ]

    patch_flags = Candidate.load_script('scripts/patch_flags')
    for filename in initial_scripts:
        script = Manager.get_json(filename)
        script.insert_script(patch_flags, 0)

    for p in placement:
        if 'TUTO_TRIGGER' in p.key:
            p.SpawnStartFlag = DUMMY
            p.SpawnEndFlag = DUMMY

    ##################
    # KNOWN SOFTLOCK #
    ##################

    if EventsAndItems.include_main_story:
        # Hikari Ch 3 won't work if done after Ch 5
        # due to flag 615. Don't let it get set!
        # No clue what it is used for.
        script = Manager.get_json('MS_KEN_50_1600')
        script.toggle_flag_off(615)

        # Temenos Chapters 3a & 3b can affect Chapter 2
        # through flag 25446 (can't get on boat)
        script = Manager.get_json('MS_SIN_3A_0000')
        script.toggle_flag_off(25446)
        script = Manager.get_json('MS_SIN_3B_0100')
        script.toggle_flag_off(25446)

    #####################
    # STUFF TO TURN OFF #
    #####################

    if EventsAndItems.include_pcs:
        # PC recruiments
        placement.NPC_DANCER_0000_0000_0010.SpawnStartFlag = NEVERUSE # (recruit Agnea)
        placement.NPC_ALCHEMIST_0000_0200.SpawnStartFlag = NEVERUSE # (recruit Castti)
        placement.NPC_HUNTER_0000_0000.SpawnStartFlag = NEVERUSE # (recruit Ochette)
        placement.PC_Party_Join_SHO_0000.SpawnStartFlag = NEVERUSE # (recruit Partitio)
        placement.NPC_PROFESSOR_0000_0000.SpawnStartFlag = NEVERUSE # (recruit Osvald)
        placement.NPC_PRIEST_0000_0000.SpawnStartFlag = NEVERUSE # (recruit Temenos)
        placement.NPC_THIEF_0000_0000.SpawnStartFlag = NEVERUSE # (recruit Throne)
        # Hikari & NPCs
        placement.NPC_FENCER_0000_0000.SpawnStartFlag = NEVERUSE # (recruit Hikari) trigger only
        placement.NPC_FENCER_0000_0100.SpawnStartFlag = NEVERUSE # (recruit Hikari) Hikari Spawn
        placement.NPC_FENCER_0000_0200.SpawnStartFlag = NEVERUSE # (recruit Hikari) NPCs (the NPCs seem to affect appearance of NPC shops; best to set flags of all of them)
        placement.NPC_FENCER_0000_0300.SpawnStartFlag = NEVERUSE # (recruit Hikari) NPCs
        placement.NPC_FENCER_0000_0400.SpawnStartFlag = NEVERUSE # (recruit Hikari) NPCs
        placement.NPC_FENCER_0000_0500.SpawnStartFlag = NEVERUSE # (recruit Hikari) NPCs
        placement.NPC_FENCER_0000_0600.SpawnStartFlag = NEVERUSE # (recruit Hikari) NPCs
        placement.NPC_FENCER_0000_0700.SpawnStartFlag = NEVERUSE # (recruit Hikari) NPCs

    #### MIGHT AS WELL KEEP ALL OF THESE SPAWNS ON REGARDLESS OF OPTIONS ####
    
    #### ENSURE AL ALWAYS SPAWNS, EVEN DURING THE FINAL EVENTS
    placement.NPC_SS_TMount21_0400_0100.NotSpawnFinal = False # Al in Montwise
    # All the Als
    placement.NPC_SS_TCity13_Tutorial_0100.NotSpawnFinal = False
    placement.NPC_SS_TDesert11_Tutorial_0100.NotSpawnFinal = False
    placement.NPC_SS_TForest13_Tutorial_0100.NotSpawnFinal = False
    placement.NPC_SS_TIsland12_Tutorial_0100.NotSpawnFinal = False
    placement.NPC_SS_TIsland13_Tutorial_0100.NotSpawnFinal = False
    placement.NPC_SS_TMount12_Tutorial_0100.NotSpawnFinal = False
    placement.NPC_SS_TSea13_Tutorial_0100.NotSpawnFinal = False
    placement.NPC_SS_TSnow12_Tutorial_0100.NotSpawnFinal = False
    placement.NPC_SS_TWilderness13_Tutorial_0100.NotSpawnFinal = False

    placement.NPC_SS_TCity13_Tutorial_0200.NotSpawnFinal = False
    placement.NPC_SS_TDesert11_Tutorial_0200.NotSpawnFinal = False
    placement.NPC_SS_TForest13_Tutorial_0200.NotSpawnFinal = False
    placement.NPC_SS_TIsland12_Tutorial_0200.NotSpawnFinal = False
    placement.NPC_SS_TIsland13_Tutorial_0200.NotSpawnFinal = False
    placement.NPC_SS_TMount12_Tutorial_0200.NotSpawnFinal = False
    placement.NPC_SS_TSea13_Tutorial_0200.NotSpawnFinal = False
    placement.NPC_SS_TSnow12_Tutorial_0200.NotSpawnFinal = False
    placement.NPC_SS_TWilderness13_Tutorial_0200.NotSpawnFinal = False

    placement.Trigger_SS_TCity13_Tutorial_0100.NotSpawnFinal = False
    placement.Trigger_SS_TCity13_Tutorial_Enable.NotSpawnFinal = False
    placement.Trigger_SS_TCity13_Tutorial_Ongoing.NotSpawnFinal = False
    placement.Trigger_SS_TDesert11_Tutorial_0100.NotSpawnFinal = False
    placement.Trigger_SS_TDesert11_Tutorial_Enable.NotSpawnFinal = False
    placement.Trigger_SS_TDesert11_Tutorial_Ongoing.NotSpawnFinal = False
    placement.Trigger_SS_TForest13_Tutorial_0100.NotSpawnFinal = False
    placement.Trigger_SS_TForest13_Tutorial_Enable.NotSpawnFinal = False
    placement.Trigger_SS_TForest13_Tutorial_Ongoing.NotSpawnFinal = False
    placement.Trigger_SS_TIsland12_Tutorial_0100.NotSpawnFinal = False
    placement.Trigger_SS_TIsland12_Tutorial_Enable.NotSpawnFinal = False
    placement.Trigger_SS_TIsland12_Tutorial_Ongoing.NotSpawnFinal = False
    # placement.Trigger_SS_TIsland13_Tutorial_0100.NotSpawnFinal = False
    placement.Trigger_SS_TIsland13_Tutorial_Enable.NotSpawnFinal = False
    placement.Trigger_SS_TIsland13_Tutorial_Ongoing.NotSpawnFinal = False
    placement.Trigger_SS_TMount12_Tutorial_0100.NotSpawnFinal = False
    placement.Trigger_SS_TMount12_Tutorial_Enable.NotSpawnFinal = False
    placement.Trigger_SS_TMount12_Tutorial_Ongoing.NotSpawnFinal = False
    placement.Trigger_SS_TSea13_Tutorial_0100.NotSpawnFinal = False
    placement.Trigger_SS_TSea13_Tutorial_Enable.NotSpawnFinal = False
    placement.Trigger_SS_TSea13_Tutorial_Ongoing.NotSpawnFinal = False
    placement.Trigger_SS_TSnow12_Tutorial_0100.NotSpawnFinal = False
    placement.Trigger_SS_TSnow12_Tutorial_Enable.NotSpawnFinal = False
    placement.Trigger_SS_TSnow12_Tutorial_Ongoing.NotSpawnFinal = False
    placement.Trigger_SS_TWilderness13_Tutorial_0100.NotSpawnFinal = False
    placement.Trigger_SS_TWilderness13_Tutorial_Enable.NotSpawnFinal = False
    placement.Trigger_SS_TWilderness13_Tutorial_Ongoing.NotSpawnFinal = False

    # Get Dispatches from Beastling Island (for unlocking galdera)
    placement.NPC_SS_TMount21_0200_0200.NotSpawnFinal = False

    # Scent of Commerce events
    placement.EV_TRIGGER_MS_SHO_EX3_0100.NotSpawnFinal = False
    placement.EV_TRIGGER_MS_SHO_EX3_0110.NotSpawnFinal = False
    placement.EV_TRIGGER_MS_SHO_EX1_0100.NotSpawnFinal = False
    placement.EV_TRIGGER_MS_SHO_EX1_0110.NotSpawnFinal = False
    placement.EV_TRIGGER_MS_SHO_EX2_0100.NotSpawnFinal = False
    placement.EV_TRIGGER_MS_SHO_EX2_0200.NotSpawnFinal = False
    placement.NPC_SHO_EX3_0100_0000.NotSpawnFinal = False
    placement.NPC_SHO_EX3_0100_0010.NotSpawnFinal = False
    placement.NPC_SHO_EX3_0200_0000.NotSpawnFinal = False
    placement.NPC_SHO_EX1_0120_0000.NotSpawnFinal = False
    placement.NPC_SHO_EX2_0100_0000.NotSpawnFinal = False

    # Unusual Tome Specialist
    placement.NPC_SS_TMount21_0200_0100.NotSpawnFinal = False
    # Al at Gates of Hell
    placement.EV_TRIGGER_SS_GAK_10_0100.NotSpawnFinal = False
    placement.EV_TRIGGER_SS_GAL_10_0210.NotSpawnFinal = False

    #######################
    # LINK FLAGS TO ITEMS #
    #######################

    # Guilds
    if EventsAndItems.include_guild_spawn:
        placement.NPC_Twn_Dst_2_1_A_GUILD.SpawnStartFlag = candidates['unlock_guild_war'].flag
        placement.NPC_Fld_Isd_2_1_GUILD.SpawnStartFlag = candidates['unlock_guild_hun'].flag
        placement.NPC_Twn_Sea_2_1_A_GUILD.SpawnStartFlag = candidates['unlock_guild_apo'].flag
        placement.NPC_Fld_Wld_2_1_GUILD.SpawnStartFlag = candidates['unlock_guild_mer'].flag
        placement.NPC_Fld_Mnt_2_2_GUILD.SpawnStartFlag = candidates['unlock_guild_cle'].flag
        placement.NPC_Fld_Snw_2_2_GUILD.SpawnStartFlag = candidates['unlock_guild_sch'].flag
        placement.NPC_Twn_Cty_2_1_B_GUILD.SpawnStartFlag = candidates['unlock_guild_thi'].flag
        placement.NPC_Twn_Fst_2_1_A_GUILD.SpawnStartFlag = candidates['unlock_guild_dan'].flag
        placement.NPC_Fld_Cty_1_3_GUILD.SpawnStartFlag = candidates['unlock_guild_inv'].flag
        placement.NPC_Twn_Wld_3_1_A_GUILD.SpawnStartFlag = candidates['unlock_guild_arm'].flag
        placement.NPC_JOB_WIZ_0100_0000.SpawnStartFlag = candidates['unlock_guild_arc'].flag

    # Altars
    if EventsAndItems.include_altar_spawn:
        placement.EV_TRIGGER_KEN_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_war'].flag
        placement.EV_TRIGGER_KAR_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_hun'].flag
        placement.EV_TRIGGER_KUS_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_apo'].flag
        placement.EV_TRIGGER_SHO_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_mer'].flag
        placement.EV_TRIGGER_SIN_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_cle'].flag
        placement.EV_TRIGGER_GAK_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_sch'].flag
        placement.EV_TRIGGER_TOU_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_thi'].flag
        placement.EV_TRIGGER_ODO_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_dan'].flag

    # NPCs
    if EventsAndItems.include_assassins_spawn:
        placement.NPC_Fld_Mnt_3_2_TALK_0100_N000.SpawnStartFlag = candidates['unlock_foreign_assassin'].flag

    if EventsAndItems.include_assassins:
        placement.NPC_Fld_Mnt_3_2_TALK_0100_N000.EventEndFlag_A = candidates['end_foreign_assassin_battle'].flag
        placement.NPC_Fld_Mnt_3_2_TALK_0100_N000.EventStartFlag_B = candidates['end_foreign_assassin_battle'].flag

    # Make Northern Montwise Pass Guard unbeatable
    if EventsAndItems.include_guard:
        placement.CLOSE_TRIGGER_Fld_Mnt_2_1_0100.SpawnEndFlag = candidates['unlock_snow_guard'].flag
        npc_data.NPC_Fld_Mnt_2_1_TALK_0100.FCmd_Battle_ID = 'None'
        npc_data.NPC_Fld_Mnt_2_1_TALK_0100.FCmd_Search_ID = 'None'
        npc_data.NPC_Fld_Mnt_2_1_TALK_0100.FCmd_Lure_ID = 'None'

    # Boats
    if EventsAndItems.include_ships_spawn:
        placement.NPC_SYS_LINERSHIP_5001.SpawnStartFlag = candidates['unlock_new_delsta_ship'].flag
        placement.NPC_SYS_LINERSHIP_5002.SpawnStartFlag = candidates['unlock_beasting_bay_ship'].flag
        placement.NPC_SYS_LINERSHIP_5003.SpawnStartFlag = candidates['unlock_crackridge_ship'].flag
        placement.NPC_SYS_LINERSHIP_0000.SpawnStartFlag = candidates['unlock_canalbrine_ship'].flag

    if EventsAndItems.include_main_story:
        # Dng_Dst_3_1 -- Hikari & Agnea -- checked
        placement.EV_TRIGGER_MS_END_2D_TIPS_0100.SpawnStartFlag = candidates['unlock_flame_grotto'].flag
        placement.EV_TRIGGER_MS_END_2D_TIPS_0300_10.SpawnStartFlag = candidates['unlock_flame_grotto'].flag
        placement.EV_TRIGGER_MS_END_2D_TIPS_0300_20.SpawnStartFlag = candidates['unlock_flame_grotto'].flag

        # Dng_Isd_1_1 -- Ochette & Castti Flame -- checked
        placement.EV_TRIGGER_MS_END_2C_TIPS_01A0.SpawnStartFlag = candidates['unlock_flame_tomb'].flag
        placement.EV_TRIGGER_MS_END_2C_TIPS_0300_10.SpawnStartFlag = candidates['unlock_flame_tomb'].flag
        placement.EV_TRIGGER_MS_END_2C_TIPS_0300_20.SpawnStartFlag = candidates['unlock_flame_tomb'].flag
        placement.EV_TRIGGER_MS_END_2C_0010.SpawnStartFlag = candidates['unlock_flame_tomb'].flag

        # Dng_Wld_2_2 -- Osvald & Partitio Flame (the one with all the notes!)
        placement.EV_TRIGGER_MS_END_2B_TIPS_01A0.SpawnStartFlag = candidates['unlock_flame_ruins'].flag
        placement.EV_TRIGGER_MS_END_2B_TIPS_0300_10.SpawnStartFlag = candidates['unlock_flame_ruins'].flag
        placement.EV_TRIGGER_MS_END_2B_TIPS_0300_20.SpawnStartFlag = candidates['unlock_flame_ruins'].flag

        # Twn_Mnt_1_1_A -- Throne & Temenos
        placement.EV_TRIGGER_MS_END_2A_0010.SpawnStartFlag = candidates['unlock_flame_church'].flag
        # Twn_Mnt_1_2_A -- Throne & Temenos
        placement.EV_ITEM_MS_END_2A_0100.SpawnStartFlag = candidates['unlock_flame_church'].flag

        # Scent of commerce
        placement.EV_TRIGGER_MS_SHO_EX1_0100.SpawnStartFlag = candidates['unlock_soc_grand_terry'].flag
        placement.EV_TRIGGER_MS_SHO_EX2_0100.SpawnStartFlag = candidates['unlock_soc_gramophone'].flag
        placement.EV_TRIGGER_MS_SHO_EX3_0100.SpawnStartFlag = candidates['unlock_soc_manuscript'].flag

    if EventsAndItems.include_galdera:
        # Allow "Give Al his bag back" cutscene to tigger as soon as you have Al's bag
        # rather than as soon as you fight the thief.
        placement.NPC_SS_TCity13_Tutorial_0100.EventStartFlag_A = candidates['unlock_als_bag'].flag
        placement.NPC_SS_TDesert11_Tutorial_0100.EventStartFlag_A = candidates['unlock_als_bag'].flag
        placement.NPC_SS_TForest13_Tutorial_0100.EventStartFlag_A = candidates['unlock_als_bag'].flag
        placement.NPC_SS_TIsland12_Tutorial_0100.EventStartFlag_A = candidates['unlock_als_bag'].flag
        placement.NPC_SS_TIsland13_Tutorial_0100.EventStartFlag_A = candidates['unlock_als_bag'].flag
        placement.NPC_SS_TMount12_Tutorial_0100.EventStartFlag_A = candidates['unlock_als_bag'].flag
        placement.NPC_SS_TSea13_Tutorial_0100.EventStartFlag_A = candidates['unlock_als_bag'].flag
        placement.NPC_SS_TSnow12_Tutorial_0100.EventStartFlag_A = candidates['unlock_als_bag'].flag
        placement.NPC_SS_TWilderness13_Tutorial_0100.EventStartFlag_A = candidates['unlock_als_bag'].flag

    ###############
    # STORY FLAGS #
    ###############

    if EventsAndItems.include_main_story:
        # Hikari
        main_story.MS_KEN_01.ReleaseFlag[0] = candidates['unlock_hikari_2'].flag
        main_story.MS_KEN_02.ReleaseFlag[0] = candidates['unlock_hikari_3'].flag
        main_story.MS_KEN_03.ReleaseFlag[0] = candidates['unlock_hikari_4'].flag
        main_story.MS_KEN_04.ReleaseFlag[0] = candidates['unlock_hikari_5'].flag

        # Ochette
        main_story.MS_KAR_01.ReleaseFlag[0] = candidates['unlock_ochette_2a'].flag
        main_story.MS_KAR_02.ReleaseFlag[0] = candidates['unlock_ochette_2b'].flag
        main_story.MS_KAR_03.ReleaseFlag[0] = candidates['unlock_ochette_2c'].flag
        main_story.MS_KAR_04.ReleaseFlag[0] = candidates['unlock_ochette_3'].flag

        # Castti
        main_story.MS_KUS_01.ReleaseFlag[0] = candidates['unlock_castti_2a'].flag
        main_story.MS_KUS_02.ReleaseFlag[0] = candidates['unlock_castti_2b'].flag
        main_story.MS_KUS_03.ReleaseFlag[0] = candidates['unlock_castti_3'].flag
        main_story.MS_KUS_04.ReleaseFlag[0] = candidates['unlock_castti_4'].flag

        # Partitio
        main_story.MS_SHO_01.ReleaseFlag[0] = candidates['unlock_partitio_2'].flag
        main_story.MS_SHO_02.ReleaseFlag[0] = candidates['unlock_partitio_3'].flag
        main_story.MS_SHO_03.ReleaseFlag[0] = candidates['unlock_partitio_4'].flag
        # Partitio - Scent of Commerce
        main_story.MS_SHO_10.ReleaseFlag[0] = candidates['unlock_soc_grand_terry'].flag
        main_story.MS_SHO_11.ReleaseFlag[0] = candidates['unlock_soc_gramophone'].flag
        main_story.MS_SHO_12.ReleaseFlag[0] = candidates['unlock_soc_manuscript'].flag

        # Temenos
        main_story.MS_SIN_01.ReleaseFlag[0] = candidates['unlock_temenos_2'].flag
        main_story.MS_SIN_02.ReleaseFlag[0] = candidates['unlock_temenos_3a'].flag
        main_story.MS_SIN_03.ReleaseFlag[0] = candidates['unlock_temenos_3b'].flag
        main_story.MS_SIN_04.ReleaseFlag[0] = candidates['unlock_temenos_4'].flag

        # Osvald
        main_story.MS_GAK_02.ReleaseFlag[0] = candidates['unlock_osvald_3'].flag
        main_story.MS_GAK_03.ReleaseFlag[0] = candidates['unlock_osvald_4'].flag
        main_story.MS_GAK_04.ReleaseFlag[0] = candidates['unlock_osvald_5'].flag

        # Throne
        main_story.MS_TOU_01.ReleaseFlag[0] = candidates['unlock_throne_2a'].flag
        main_story.MS_TOU_02.ReleaseFlag[0] = candidates['unlock_throne_2b'].flag
        main_story.MS_TOU_03.ReleaseFlag[0] = candidates['unlock_throne_3a'].flag
        main_story.MS_TOU_04.ReleaseFlag[0] = candidates['unlock_throne_3b'].flag
        main_story.MS_TOU_05.ReleaseFlag[0] = candidates['unlock_throne_4'].flag

        # Agnea
        main_story.MS_ODO_01.ReleaseFlag[0] = candidates['unlock_agnea_2'].flag
        main_story.MS_ODO_02.ReleaseFlag[0] = candidates['unlock_agnea_3'].flag
        main_story.MS_ODO_03.ReleaseFlag[0] = candidates['unlock_agnea_4'].flag
        main_story.MS_ODO_04.ReleaseFlag[0] = candidates['unlock_agnea_5'].flag

        # COP_GS - Osvald & Partitio
        main_story.COP_GS_00.ReleaseFlag[0] = candidates['unlock_cop_op_1'].flag
        main_story.COP_GS_00.ReleaseFlag[1] = 0
        main_story.COP_GS_00.ReleaseFlag[2] = 0
        main_story.COP_GS_00.ReleaseFlag[3] = 0

        main_story.COP_GS_01.ReleaseFlag[0] = candidates['unlock_cop_op_2'].flag
        main_story.COP_GS_01.ReleaseFlag[1] = 0
        main_story.COP_GS_01.ReleaseFlag[2] = 0
        main_story.COP_GS_01.ReleaseFlag[3] = 0

        # COP_KK - Ochette & Castti
        main_story.COP_KK_00.ReleaseFlag[0] = candidates['unlock_cop_oc_1'].flag
        main_story.COP_KK_00.ReleaseFlag[1] = 0
        main_story.COP_KK_00.ReleaseFlag[2] = 0
        main_story.COP_KK_00.ReleaseFlag[3] = 0

        main_story.COP_KK_01.ReleaseFlag[0] = candidates['unlock_cop_oc_2'].flag
        main_story.COP_KK_01.ReleaseFlag[1] = 0
        main_story.COP_KK_01.ReleaseFlag[2] = 0
        main_story.COP_KK_01.ReleaseFlag[3] = 0

        # COP_OK - Agnea & Hikari
        main_story.COP_OK_00.ReleaseFlag[0] = candidates['unlock_cop_ah_1'].flag
        main_story.COP_OK_00.ReleaseFlag[1] = 0
        main_story.COP_OK_00.ReleaseFlag[2] = 0
        main_story.COP_OK_00.ReleaseFlag[3] = 0

        main_story.COP_OK_01.ReleaseFlag[0] = candidates['unlock_cop_ah_2'].flag
        main_story.COP_OK_01.ReleaseFlag[1] = 0
        main_story.COP_OK_01.ReleaseFlag[2] = 0
        main_story.COP_OK_01.ReleaseFlag[3] = 0

        # COP_ST - Throne & Temenos
        main_story.COP_ST_00.ReleaseFlag[0] = candidates['unlock_cop_tt_1'].flag
        main_story.COP_ST_00.ReleaseFlag[1] = 0
        main_story.COP_ST_00.ReleaseFlag[2] = 0
        main_story.COP_ST_00.ReleaseFlag[3] = 0

        main_story.COP_ST_01.ReleaseFlag[0] = candidates['unlock_cop_tt_2'].flag
        main_story.COP_ST_01.ReleaseFlag[1] = 0
        main_story.COP_ST_01.ReleaseFlag[2] = 0
        main_story.COP_ST_01.ReleaseFlag[3] = 0

        # MS_END
        main_story.MS_END_00.ReleaseFlag[0] = NEVERUSE
        main_story.MS_END_00.ReleaseFlag[1] = 0
        main_story.MS_END_00.ReleaseFlag[2] = 0
        main_story.MS_END_00.ReleaseFlag[3] = 0

        main_story.MS_END_01.ReleaseFlag[0] = candidates['unlock_flame_grotto'].flag
        main_story.MS_END_01.ReleaseFlag[1] = 0
        main_story.MS_END_01.ReleaseFlag[2] = 0
        main_story.MS_END_01.ReleaseFlag[3] = 0

        main_story.MS_END_02.ReleaseFlag[0] = candidates['unlock_flame_tomb'].flag
        main_story.MS_END_02.ReleaseFlag[1] = 0
        main_story.MS_END_02.ReleaseFlag[2] = 0
        main_story.MS_END_02.ReleaseFlag[3] = 0

        main_story.MS_END_03.ReleaseFlag[0] = candidates['unlock_flame_church'].flag
        main_story.MS_END_03.ReleaseFlag[1] = 0
        main_story.MS_END_03.ReleaseFlag[2] = 0
        main_story.MS_END_03.ReleaseFlag[3] = 0

        main_story.MS_END_04.ReleaseFlag[0] = candidates['unlock_flame_ruins'].flag
        main_story.MS_END_04.ReleaseFlag[1] = 0
        main_story.MS_END_04.ReleaseFlag[2] = 0
        main_story.MS_END_04.ReleaseFlag[3] = 0

        main_story.MS_END_05.ReleaseFlag[0] = NEVERUSE
        main_story.MS_END_05.ReleaseFlag[1] = 0
        main_story.MS_END_05.ReleaseFlag[2] = 0
        main_story.MS_END_05.ReleaseFlag[3] = 0

        # MS_EPI
        main_story.MS_EPI_00.ReleaseFlag[0] = NEVERUSE

        # Turn off release notice flags
        # Don't always work (probably prohibited in end phase)
        main_story.COP_OK_00.ReleaseNoticeFlag = False
        main_story.COP_OK_01.ReleaseNoticeFlag = False
        main_story.COP_ST_00.ReleaseNoticeFlag = False
        main_story.COP_ST_01.ReleaseNoticeFlag = False
        main_story.COP_KK_00.ReleaseNoticeFlag = False
        main_story.COP_KK_01.ReleaseNoticeFlag = False
        main_story.COP_GS_00.ReleaseNoticeFlag = False
        main_story.COP_GS_01.ReleaseNoticeFlag = False

    ################
    # TEXT UPDATES #
    ################

    if EventsAndItems.include_pcs:
        # Text displayed when recruiting PCs and asking if you want to play their chapter 1
        gameText.PROLOGUE_FLASHBACK.Text = "The flashback won't work here.\nJust skip it."

    if EventsAndItems.include_ex_abil:
        pc = Manager.get_table('PlayableCharacterDB')
        abilitySetData = Manager.get_table('AbilitySetData')

        ex_skill_2 = abilitySetData.get_row(pc.osvald.ex_skill_two).name
        gameText.ED_GAK_ADVANCEABILITY_0020._data['Text'].string_1 = 'GameTextEN'
        gameText.ED_GAK_ADVANCEABILITY_0020._data['Text'].string_2 = 'ED_GAK_ADVANCEABILITY_0020_Text'
        gameText.ED_GAK_ADVANCEABILITY_0020.set_text(f'Osvald learned the EX skill "{ex_skill_2}"')

        ex_skill_2 = abilitySetData.get_row(pc.agnea.ex_skill_two).name
        gameText.ED_ODO_ADVANCEABILITY_0020._data['Text'].string_1 = 'GameTextEN'
        gameText.ED_ODO_ADVANCEABILITY_0020._data['Text'].string_2 = 'ED_ODO_ADVANCEABILITY_0020_Text'
        gameText.ED_ODO_ADVANCEABILITY_0020.set_text(f'Agnea learned the EX skill "{ex_skill_2}"')

    #################################
    # ASSIGNING CANDIDATES TO SLOTS #
    #################################

    for s, c in rando_map.items():
        if s == 'finish_guild_inv':
            reward = Candidate.load_script('scripts/inventor_reward')
            for ci in c:
                reward.insert_script(candidates[ci].script, 8)
            add_scripts_notcand(reward, s)
        elif s == 'finish_guild_arm':
            reward = Candidate.load_script('scripts/armsmaster_reward')
            for ci in c:
                reward.insert_script(candidates[ci].script, 1)
            add_scripts_notcand(reward, s)
        else:
            for ci in c:
                add_scripts(ci, s)

    add_scripts('unlock_unshiny_mirror', rando_map_inv['unlock_shiny_mirror'])

    for pc in other_pc:
        add_scripts(pc, 'finish_chapter_1')

    ####################
    # FOREIN ASSASSINS #
    ####################

    if EventsAndItems.include_assassins:
        # Need to change the flag set since 25520 is also linked to Hired Help Foreign Assassin
        slot = slot_manager.get_slot('finish_foreign_assassin')
        slot.script.change_flag(25520, candidates['end_foreign_assassin_battle'].flag)

    #########
    # BUILD #
    #########

    slot_manager.finalize()

    ###########
    # PATCHES #
    ###########

    if EventsAndItems.include_main_story:
        ############################################
        # EVENTS DURING END BEFORE IGNITING FLAMES #
        ############################################

        patch_end_on = Candidate.load_script('scripts/patch_toggle_end_on')
        patch_end_off = Candidate.load_script('scripts/patch_toggle_end_off')

        # Yomi won't spawn while mist is around, even with all NotSpawnFinal set to False
        cop_ah2_200 = Manager.get_json('MS_COP_OK2_0200')
        cop_ah2_500 = Manager.get_json('MS_COP_OK2_0500')
        cop_ah2_200.insert_script(patch_end_off, 9)
        cop_ah2_500.insert_script(patch_end_on, 10)

        cop_st1_100 = Manager.get_json('MS_COP_ST1_0100')
        cop_st1_400 = Manager.get_json('MS_COP_ST1_0400')
        cop_st1_100.insert_script(patch_end_off, 10)
        cop_st1_400.insert_script(patch_end_on, 14)

        # Toggle off due to patched flags -- COP TT 1, no traveling out should be needed anyway
        main_story_tasks = Manager.get_table('MainStoryTask')
        main_story_tasks.CPL_ST1_0100.UnavailableFastTravel = True
        main_story_tasks.CPL_ST1_0200.UnavailableFastTravel = True
        main_story_tasks.CPL_ST1_0210.UnavailableFastTravel = True
        main_story_tasks.CPL_ST1_0300.UnavailableFastTravel = True
        main_story_tasks.CPL_ST1_0400.UnavailableFastTravel = True
        main_story_tasks.CPL_ST1_0500.UnavailableFastTravel = True
        main_story_tasks.CPL_ST1_0600.UnavailableFastTravel = True
        main_story_tasks.CPL_ST1_0700.UnavailableFastTravel = True

        # Toggle off due to patched flags -- COP AH 2, no traveling out should be needed anyway
        main_story_tasks = Manager.get_table('MainStoryTask')
        main_story_tasks.CPL_OK2_0200.UnavailableFastTravel = True
        main_story_tasks.CPL_OK2_0300.UnavailableFastTravel = True
        main_story_tasks.CPL_OK2_0400.UnavailableFastTravel = True
        main_story_tasks.CPL_OK2_0500.UnavailableFastTravel = True
        main_story_tasks.CPL_OK2_0600.UnavailableFastTravel = True
        main_story_tasks.CPL_OK2_0700.UnavailableFastTravel = True
        main_story_tasks.CPL_OK2_0800.UnavailableFastTravel = True

        ######################
        # OCHETTE 2A AFTER 3 #
        ######################

        # prevent receiving a second acta
        patch_ochette = Candidate.load_script('scripts/patch_ochette_2a')
        script = Manager.get_json('MS_KAR_2A_0600')
        script.insert_script(patch_ochette, -1)
        script = Manager.get_json('MS_KAR_2M_01A0')
        script.insert_script(patch_ochette, -1)

