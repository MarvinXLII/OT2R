import os
import sys
import hjson
import random
from Manager import Manager
from Graph import Graph, Edge, Node
from Utility import get_filename, time_func
from Scripts import Script
from DataJson import DataJsonFile
from copy import deepcopy
import pickle
import lzma

from FLAGS import NEVERUSE, TESTFLAG, DUMMY


class Tracker:
    def __init__(self, value):
        self._value = value
        self._initial_value = value

    def reset(self):
        self._value = self._initial_value

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

script_index_tracker = Tracker(100)


class EventsAndItems:
    num_start_pc = 1
    start_pc = 'Random'

    # Stories
    include_main_story = False
    include_galdera = False

    # Key Items
    include_key_items = False
    include_assassins = False
    include_ex_abil = False
    include_pcs = False
    include_guard = False
    include_inventor_parts = False
    include_rusty_weapons = False
    include_galdera_items = False

    # Slots only
    include_guilds = False
    omit_guild_conjuror = False

    # Spawns
    include_ships_spawn = False
    include_guild_spawn = False
    include_altar_spawn = False
    include_assassins_spawn = False

    @classmethod
    def any_on(cls):
        return cls.include_main_story \
            or cls.include_galdera \
            or cls.include_pcs \
            or cls.include_guilds \
            or cls.include_ex_abil \
            or cls.include_guard \
            or cls.include_ships_spawn \
            or cls.include_guild_spawn \
            or cls.include_altar_spawn \
            or cls.include_assassins_spawn \
            or cls.include_key_items \
            or cls.include_assassins \
            or cls.include_inventor_parts \
            or cls.include_rusty_weapons \
            or cls.include_galdera_items

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

    #@time_func
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
        # add_to_data('json/logic/items.json')
        # add_to_data('json/logic/rusty_weapons.json')

        #### OPTIONAL FILES ####
        add_to_data('json/logic/altars.json', option=self.include_altar_spawn) # SPAWNING altars, NOT ex abilities from altars
        add_to_data('json/logic/ex_abilities.json', option=self.include_ex_abil) # Ex Abil from BOTH altars and final chapters
        add_to_data('json/logic/assassins_spawn.json', option=self.include_assassins_spawn)
        add_to_data('json/logic/guilds.json', option=self.include_guilds)
        add_to_data('json/logic/guilds_spawn.json', option=self.include_guild_spawn)
        add_to_data('json/logic/blocks.json', option=self.include_guard)
        add_to_data('json/logic/ships.json', option=self.include_ships_spawn)

        # THE STORY STUFF -- should have the same option for all
        add_to_data('json/logic/story_recruit.json', option=self.include_pcs)
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

        # GALDERA SIDEQUESTS STORIES
        add_to_data('json/logic/sidequest_the_travelers_bag.json', option=self.include_galdera)
        add_to_data('json/logic/sidequest_procuring_peculiar_tomes.json', option=self.include_galdera)
        add_to_data('json/logic/sidequest_from_the_far_reaches_of_hell.json', option=self.include_galdera)
        add_to_data('json/logic/sidequest_a_gate_between_worlds.json', option=self.include_galdera)

        # KEY ITEMS
        add_to_data('json/logic/item_agnea_theater_ticket.json', option=self.include_key_items)
        add_to_data('json/logic/item_agnea_wooden_sword.json', option=self.include_key_items)
        add_to_data('json/logic/item_agnea_cute_shoes.json', option=self.include_key_items)
        add_to_data('json/logic/item_castti_rosas_medicine.json', option=self.include_key_items)
        add_to_data('json/logic/item_hikari_weapons_deal_details.json', option=self.include_key_items)
        add_to_data('json/logic/item_ochette_beasts.json', option=self.include_key_items)
        add_to_data('json/logic/item_temenos_notebooks.json', option=self.include_key_items)
        add_to_data('json/logic/item_temenos_vados_info.json', option=self.include_key_items)
        add_to_data('json/logic/item_throne_mask.json', option=self.include_key_items)
        add_to_data('json/logic/item_throne_horse_coin.json', option=self.include_key_items)
        add_to_data('json/logic/item_throne_habit.json', option=self.include_key_items)
        add_to_data('json/logic/item_throne_keys.json', option=self.include_key_items)
        add_to_data('json/logic/item_osvald_library.json', option=self.include_key_items)
        add_to_data('json/logic/item_osvald_black_crystals.json', option=self.include_key_items)
        add_to_data('json/logic/item_partitio_clockite.json', option=self.include_key_items)
        add_to_data('json/logic/item_partitio_scent_of_commerce.json', option=self.include_key_items)
        add_to_data('json/logic/item_cloudy_mirror.json', option=self.include_key_items)
        add_to_data('json/logic/item_cop_tt.json', option=self.include_key_items)
        add_to_data('json/logic/item_cop_ah.json', option=self.include_key_items)
        add_to_data('json/logic/item_cop_op.json', option=self.include_key_items)
        add_to_data('json/logic/inventor_parts.json', option=self.include_inventor_parts)
        add_to_data('json/logic/rusty_weapons.json', option=self.include_rusty_weapons)
        add_to_data('json/logic/item_als_bag.json', option=self.include_galdera_items)
        add_to_data('json/logic/item_peculiar_tomes.json', option=self.include_galdera_items)
        add_to_data('json/logic/item_from_the_far_reaches_of_hell.json', option=self.include_galdera_items)
        add_to_data('json/logic/item_hire_foreign_assassins.json', option=self.include_assassins)

        # Turn all slots on
        for slot in self.rando_slots:
            assert slot in self.node_dict, slot
            self.node_dict[slot].is_slot = True

        if EventsAndItems.omit_guild_conjuror:
            self.node_dict['finish_guild_con'].is_slot = False


    #@time_func
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

        starting_nodes = {
            'Hikari': 'Hinoeuma',
            'Ochette': "Toto'haha",
            'Castti': 'Harbourlands',
            'Partitio': 'Wildlands',
            'Temenos': 'Crestlands',
            'Osvald': 'Winterlands',
            'Throne': 'Brightlands',
            'Agnea': 'Leaflands',
        }

        # Always doing this random sample ensure that randomly picking
        # PC X and selecting PC X will give the same results
        self.start_pc = random.sample(sorted(starting_characters.keys()), 1)[0]
        if EventsAndItems.picked_start_pc != 'Random':
            assert EventsAndItems.picked_start_pc in starting_characters
            self.start_pc = EventsAndItems.picked_start_pc
        self.always_have.append(starting_characters[self.start_pc])
        self.always_have.append(starting_characters[self.start_pc].replace('start', 'item'))
        self.start_node = starting_nodes[self.start_pc]

        self.other_pcs = []
        if self.num_start_pc > 1:
            pcs = list(starting_characters.keys())
            pcs.remove(self.start_pc)
            other_pcs = random.sample(pcs, self.num_start_pc-1)
            for pc in other_pcs:
                x = starting_characters[pc].replace('start', 'item')
                self.always_have.append(x)
                self.other_pcs.append(pc.lower())

        # Turn PC recruitment slots off
        self.node_dict[f'get_{self.start_pc.lower()}'].is_slot = False
        for pc in self.other_pcs:
            self.node_dict[f'get_{pc}'].is_slot = False

    @time_func
    def _shuffle(self):
        # Must turn off the recruit PC slot of the starting PC
        slot_name = 'get_' + self.start_pc.lower()
        assert slot_name in self.node_dict
        self.node_dict[slot_name].is_slot = False

        start = self.node_dict[self.start_node]
        self.graph.reset()
        self.graph.store_node_costs(start)
        # Repeat until all key item slots are filled
        # (shouldn't ever repeat, but done as a precaution)
        while not self.graph.shuffle(start, self.rando_cand, self.always_have):
            print('not all key item slots were filled; retrying')
        self.rings = self.graph.get_rings(self.always_have, rank_on=False)

        self.rando_map = {}
        self.rando_map_inv = {}
        for node in sorted(self.graph.nodes):
            if node.is_slot:
                self.rando_map[node.name] = sorted(node.slots)
                for c in node.slots:
                    assert c not in self.rando_map_inv
                    self.rando_map_inv[c] = node.name

    #@time_func
    def _finalize(self):
        fill_everything(self.rando_map, self.rando_map_inv, self.start_pc, self.other_pcs)
        # self._print_shuffler()
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

        with open(get_filename('json/slot_descriptions.json'), 'r', encoding='utf-8') as file:
            slots_data = hjson.load(file)

        slots_keys = list(slots_data.keys())

        ring_num = 0
        missing = []
        for ring in self.rings:

            names = []
            for node in ring:
                if not node.is_slot:
                    continue
                cand = []
                if node.name not in slots_data:
                    missing.append(node.name)
                    continue
                for c in node.slots:
                    try:
                        desc = candidates_data[c]['name']
                    except:
                        desc = ' '.join([ci.capitalize() for ci in c.split('_')])
                    cand.append(desc)

                names.append((node.name, cand))

            if not names:
                continue

            # Print descriptions in order of the descriptions json
            # This is an done inefficiently, but whatever....
            names.sort(key=lambda x: slots_keys.index(x[0]))
            
            ring_num += 1
            print('Group', ring_num)
            print('')
            for name, cand in names:
                print('  ', slots_data[name])
                for c in cand:
                    print('     ', c)
                print('')

        # if missing:
        #     print('')
        #     print('')
        #     print('')
        #     print('MISSING')
        #     for mi in missing:
        #         print('  ', missing)

        sys.stdout = sys.__stdout__

    def _print_shuffler(self):
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
            try:
                cand_to_slot[key] = slots_data[slot][0]['description']
            except:
                print(slot, 'not in slots_data')
                cand_to_slot[key] = slot
            max_size = max(max_size, len(key))

        outfile = os.path.join(self.outpath, 'spoiler_events_and_items.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')
        for cand, slot in cand_to_slot.items():
            print('  ', cand.ljust(max_size, ' '), ' <-- ', slot)
        sys.stdout = sys.__stdout__


class Candidate:
    def __init__(self, unlock, name, has_script=False, give_item=False):
        self.basename = f'scripts/generated/{unlock}'
        self.script = Script.load(self.basename)
        self.name = name
        self.give_item = give_item

    @property
    def flag(self):
        sys.exit('not flag set for Candidate:', self.basename, self.name)


class CandidateWithFlag(Candidate):
    def __init__(self, unlock, name, flag, item_key, has_script=False, give_item=False):
        super().__init__(unlock, name, has_script, give_item)
        self._flag = flag
        self.item_key = item_key

    @property
    def flag(self):
        return self._flag

    @classmethod
    def data_factory(cls, unlock, data):
        return cls(unlock, data['name'], data['flag'], data['item_key'], data['has_script'], data['give'])



class SlotManager:
    def __init__(self):
        self.slots = {}
        self.slots_filename = {}
        self.nicknames = {}

    def create_slot(self, filename, slotname, indices, remove=None):
        if self.has_file(filename):
            slot = self.slots_filename[filename]
        else:
            slot = Slot(filename, slotname, indices, remove)
        self.add_slot(filename, slotname, slot)

    def create_slot_shop(self, slotname, placement_key, purchase_key, index, new_script=True, case='A'):
        slot = SlotShop(slotname, placement_key, purchase_key, index, new_script, case)
        self.add_slot(slot.filename, slotname, slot)

    def create_slot_hear(self, slotname, placement_key, hear_key, index, new_script=True, case='A'):
        assert slotname.startswith('hear_'), slotname
        slot = SlotHear(slotname, placement_key, hear_key, index, new_script, case)
        self.add_slot(slot.filename, slotname, slot)

    def create_slot_chest(self, slotname, treasure_key):
        slot = SlotChest(slotname, treasure_key)
        self.add_slot(slot.filename, slotname, slot)

    def add_slot(self, filename, slotname, slot):
        if slotname not in self.slots:
            self.slots[slotname] = {}
        if filename not in self.slots[slotname]:
            self.slots[slotname][filename] = slot
        if filename not in self.slots_filename:
            self.slots_filename[filename] = slot

    def get_file(self, filename):
        return self.slots_filename[filename]

    def get_slot(self, name, filename=None):
        if filename:
            return self.slots[name][filename]
        assert len(self.slots[name]) == 1, f'{name} has multiple files; not sure which to return!'
        return self.get_slot_list(name)[0]

    def get_slot_list(self, name):
        return list(self.slots[name].values())

    def has_slot(self, name):
        return name in self.slots

    def has_file(self, filename):
        return filename in self.slots_filename

    def reset(self):
        for slots in self.slots.values():
            for s in slots.values():
                s.reset()

    def finalize(self):
        for slots in self.slots.values():
            for s in slots.values():
                s.insert()


class Slot:
    def __init__(self, filename, slotname, indices, remove=None):
        self.script = Manager.get_json(filename)
        self.filename = filename
        self.slotname = slotname
        self.indices = indices
        self.unique_item_only = False
        if remove:
            remove = sorted([self._positive_index(i) for i in remove], reverse=True)
            for ri in remove:
                self.remove_command(ri)
        self.subscripts = {}

    def reset(self):
        self.subscripts = {}

    @property
    def indices(self):
        return self._indices

    @indices.setter
    def indices(self, indices):
        self._indices = sorted([self._positive_index(i) for i in indices])

    def _positive_index(self, index):
        if index < 0:
            return len(self.script.json_list) + index
        return index

    def remove_command(self, index):
        index = self._positive_index(index)
        self.script.remove_command(index)
        # Update indexing to account for any removed commands
        for i, idx in enumerate(self._indices):
            if idx > index:
                self._indices[i] -= 1

    def add_candidate(self, candidate_script, *args):
        if candidate_script not in self.subscripts:
            self.subscripts[deepcopy(candidate_script)] = False

    def insert(self):
        for subscript, inserted in self.subscripts.items():
            if not inserted:
                self.subscripts[subscript] = True
                for i, index in enumerate(self._indices):
                    self.script.insert_script(deepcopy(subscript), index)
                    offset = len(subscript.json_list)
                    for j in range(i+1, len(self._indices)):
                        self._indices[j] += offset

    def __eq__(self, other):
        return self.filename == other.filename \
            and self.slotname == other.slotname \
            and self.script == other.script

    def __hash__(self):
        return hash(f'{self.filename}_{self.slotname}')
    

# NPC shop (purchase, steal, etc.)
class SlotShop(Slot):
    def __init__(self, slotname, placement_key, purchase_key, index, new_script=True, case='A'):
        self.slotname = slotname
        self.placement_key = placement_key
        self.purchase_key = purchase_key
        self.case = case
        self.subscripts = {}
        self.unique_item_only = False

        placement_data = Manager.get_table('PlacementData')
        purchase = Manager.get_table('PurchaseItemTable')
        self.shop = getattr(purchase, purchase_key)
        self.placement = getattr(placement_data, placement_key)

        # Might be able to which branch to take based on the EventLabel
        self.new_script = new_script
        if self.new_script:
            self.filename = self._create_script()
        else:
            event_case = getattr(self.placement, f'EventType_{self.case}')
            assert event_case == 'eFC_PURCHASE_ITEM'
            self.filename = getattr(self.placement, f'EventLabel_{self.case}')
        self.script = Manager.get_json(self.filename)
        self.indices = [self._positive_index(index)]

    def _create_script(self):
        new_script_name = self._duplicate_script()
        new_script = Manager.get_json(new_script_name)
        new_script.reset()

        patch = Script.load('scripts/template')
        new_script.insert_script(patch, 0)
        return new_script_name

    def _duplicate_script(self):
        event_list = Manager.get_table('EventList')
        value = script_index_tracker.value
        orig_name = 'DELIVERY_DIALOG_TEST'
        new_name = f'{orig_name}_{value}'

        Manager.Pak.duplicate_file(orig_name, new_name)
        event_list.duplicate_data(orig_name, new_name)
        el = getattr(event_list, new_name)
        el.ExecCode = new_name

        return new_name

    def add_candidate(self, candidate_script, candidate, *args):
        self.shop.ItemLabel = candidate.item_key
        if self.new_script:
            fill_event(self.placement_key, 0, candidate.flag, self.filename, 'eFC_PURCHASE_ITEM', candidate.item_key, '1')
        else:
            setattr(self.placement, f'EventParam_{self.case}_1', candidate.item_key)
        if not candidate.give_item: # Prevent giving item again; sometimes needs to be kept, e.g. need clockite x5, but otherwise would only get 1
            candidate_script.remove_give_item(candidate.item_key)
        candidate_script.remove_display_item(candidate.item_key)
        super().add_candidate(candidate_script)


# NPC info (scrutinize, etc.)
class SlotHear(SlotShop):
    def __init__(self, slotname, placement_key, hear_key, index, new_script=True, case='A'):
        self.slotname = slotname
        self.placement_key = placement_key
        self.hear_key = hear_key
        self.case = case
        self.subscripts = {}
        self.unique_item_only = True

        placement_data = Manager.get_table('PlacementData')
        hear_info = Manager.get_table('NPCHearInfoData')
        self.hear = getattr(hear_info, hear_key)
        self.placement = getattr(placement_data, placement_key)

        # Might be able to which branch to take based on the EventLabel
        self.new_script = new_script
        if self.new_script:
            self.filename = self._create_script()
        else:
            event_case = getattr(self.placement, f'EventType_{self.case}')
            assert event_case == 'eFC_SEARCH'
            self.filename = getattr(self.placement, f'EventLabel_{self.case}')
        self.script = Manager.get_json(self.filename)
        self.indices = [self._positive_index(index)]

    def add_candidate(self, candidate_script, candidate, *args):
        self.hear.NotificationID = 'None'
        self.hear.ItemID = candidate.item_key
        if self.new_script:
            fill_event(self.placement_key, 0, candidate.flag, self.filename, 'eFC_SEARCH', candidate.item_key, '1')
        else:
            setattr(self.placement, f'EventParam_{self.case}_1', candidate.item_key)
        if not candidate.give_item: # Prevent giving item again; sometimes needs to be kept, e.g. need clockite x5, but otherwise would only get 1
            candidate_script.remove_give_item(candidate.item_key)
        candidate_script.remove_display_item(candidate.item_key)
        super(SlotShop, self).add_candidate(candidate_script)


class SlotChest(SlotShop):
    def __init__(self, slotname, treasure_key):
        self.slotname = slotname
        self.treasure_key = treasure_key
        self.placement_key = treasure_key
        self.case = 'A'
        self.subscripts = {}
        self.unique_item_only = False

        placement_data = Manager.get_table('PlacementData')
        treasures = Manager.get_table('ObjectData')
        self.treasure = getattr(treasures, self.treasure_key)
        self.placement = getattr(placement_data, self.placement_key)

        # Might be able to which branch to take based on the EventLabel
        self.new_script = True
        self.filename = self._create_script()
        self.script = Manager.get_json(self.filename)
        self.indices = [1]

    def add_candidate(self, candidate_script, candidate, *args):
        self.treasure.HaveItemLabel = candidate.item_key
        fill_event(self.placement_key, 0, candidate.flag, self.filename, 'eFC_PURCHASE_ITEM', candidate.item_key, '1')
        if not candidate.give_item: # Prevent giving item again; sometimes needs to be kept, e.g. need clockite x5, but otherwise would only get 1
            candidate_script.remove_give_item(candidate.item_key)
        candidate_script.remove_display_item(candidate.item_key)
        super(SlotShop, self).add_candidate(candidate_script)


#@time_func
def fill_everything(rando_map, rando_map_inv, start_pc, other_pcs):

    #########
    # SETUP #
    #########

    # Reset tracker
    script_index_tracker.reset()
    
    # Extract everything needed
    event_list = Manager.get_table('EventList')
    hear_info = Manager.get_table('NPCHearInfoData')
    main_story = Manager.get_table('MainStory')
    npc_data = Manager.get_table('NPCData')
    placement_data = Manager.get_table('PlacementData')
    placement_list = Manager.get_table('PlacementList')
    purchase = Manager.get_table('PurchaseItemTable')
    substory = Manager.get_table('SubStoryTask')
    treasures = Manager.get_table('ObjectData')

    # Construct everything needed
    add_new_items()
    candidates = load_candidates()
    slot_manager = load_slots(rando_map, rando_map_inv)

    # Functions to simplify stuff
    def add_scripts(candname, slotname):
        replacement = candidates[candname]
        for slot in slot_manager.get_slot_list(slotname):
            slot.add_candidate(deepcopy(replacement.script), replacement)

    # This is only called for inventor & blacksmith
    def add_scripts_notcand(replacement, slotname):
        for slot in slot_manager.get_slot_list(slotname):
            assert isinstance(slot, Slot) # Cannot be SlotShop, SlotHear, SlotChest
            slot.add_candidate(deepcopy(replacement))

    # Used for moving NPCs that guard a chest out of the way.
    # Prevents having to knock them out again on the off chance they respawn.
    def npc_copy_shift(old_key, list_key, flag, dx=0, dy=0, dz=0):
        old_npc = getattr(placement_data, old_key)
        new_key = f'{old_key}_2'
        placement_data.duplicate_data(old_key, new_key)

        new_npc = getattr(placement_data, new_key)
        new_npc.SpawnPosX += dx
        new_npc.SpawnPosY += dy
        new_npc.SpawnPosZ += dz
        old_npc.SpawnEndFlag = flag
        new_npc.SpawnStartFlag = flag

        p_list = getattr(placement_list, list_key)
        p_list.LabelList.append(new_key)

    ##################
    # FINALIZE SLOTS #
    ##################

    # Patch
    if EventsAndItems.include_key_items:
        patch = Script.load(f'scripts/scent_of_commerce_boat_truncated')
        slot = slot_manager.get_slot('finish_soc_grand_terry')
        slot.script.insert_script(patch, 0)

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

    if EventsAndItems.include_key_items:
        # Start with Castti and go to Beastling Island with Grand Terry
        # By default won't trigger cutscene with Al.
        key = 'Trigger_SS_TIsland12_Tutorial_0100'
        new_key = f'{key}_2'
        placement_data.duplicate_data(key, new_key)
        p = getattr(placement_data, new_key)
        p.NotCoexistencePlacementLabel[0] = 'Trigger_SS_TIsland13_Tutorial_Enable'
        p.SpawnPosX = -300.0
        p.SpawnPosY = -4200.0
        p.SpawnPosZ = 200.0
        p.EventLabel_A = 'SC_FI13_Tutorial_0100'
        placement_list.Fld_Isd_1_3.LabelList.append(new_key)

    #####################################
    # FIXES FOR END GAME STARTING EARLY #
    #####################################

    if EventsAndItems.include_main_story:
        ########## SPAWNING ##########

        # Get Dispatches from Beastling Island (for unlocking galdera)
        placement_data.NPC_SS_TMount21_0200_0200.NotSpawnFinal = False
        # Unusual Tome Specialist
        placement_data.NPC_SS_TMount21_0200_0100.NotSpawnFinal = False
        # Al from Far Reaches of Hell
        placement_data.NPC_SS_TMount21_0400_0100.NotSpawnFinal = False
        # Al at Gates of Hell
        placement_data.EV_TRIGGER_SS_GAK_10_0100.NotSpawnFinal = False
        placement_data.EV_TRIGGER_SS_GAL_10_0210.NotSpawnFinal = False

        # Tutorial Als
        placement_data.NPC_SS_TCity13_Tutorial_0100.NotSpawnFinal = False
        placement_data.NPC_SS_TDesert11_Tutorial_0100.NotSpawnFinal = False
        placement_data.NPC_SS_TForest13_Tutorial_0100.NotSpawnFinal = False
        placement_data.NPC_SS_TIsland12_Tutorial_0100.NotSpawnFinal = False
        placement_data.NPC_SS_TIsland13_Tutorial_0100.NotSpawnFinal = False
        placement_data.NPC_SS_TMount12_Tutorial_0100.NotSpawnFinal = False
        placement_data.NPC_SS_TSea13_Tutorial_0100.NotSpawnFinal = False
        placement_data.NPC_SS_TSnow12_Tutorial_0100.NotSpawnFinal = False
        placement_data.NPC_SS_TWilderness13_Tutorial_0100.NotSpawnFinal = False

        placement_data.NPC_SS_TCity13_Tutorial_0200.NotSpawnFinal = False
        placement_data.NPC_SS_TDesert11_Tutorial_0200.NotSpawnFinal = False
        placement_data.NPC_SS_TForest13_Tutorial_0200.NotSpawnFinal = False
        placement_data.NPC_SS_TIsland12_Tutorial_0200.NotSpawnFinal = False
        placement_data.NPC_SS_TIsland13_Tutorial_0200.NotSpawnFinal = False
        placement_data.NPC_SS_TMount12_Tutorial_0200.NotSpawnFinal = False
        placement_data.NPC_SS_TSea13_Tutorial_0200.NotSpawnFinal = False
        placement_data.NPC_SS_TSnow12_Tutorial_0200.NotSpawnFinal = False
        placement_data.NPC_SS_TWilderness13_Tutorial_0200.NotSpawnFinal = False

        placement_data.Trigger_SS_TCity13_Tutorial_0100.NotSpawnFinal = False
        placement_data.Trigger_SS_TCity13_Tutorial_Enable.NotSpawnFinal = False
        placement_data.Trigger_SS_TCity13_Tutorial_Ongoing.NotSpawnFinal = False
        placement_data.Trigger_SS_TDesert11_Tutorial_0100.NotSpawnFinal = False
        placement_data.Trigger_SS_TDesert11_Tutorial_Enable.NotSpawnFinal = False
        placement_data.Trigger_SS_TDesert11_Tutorial_Ongoing.NotSpawnFinal = False
        placement_data.Trigger_SS_TForest13_Tutorial_0100.NotSpawnFinal = False
        placement_data.Trigger_SS_TForest13_Tutorial_Enable.NotSpawnFinal = False
        placement_data.Trigger_SS_TForest13_Tutorial_Ongoing.NotSpawnFinal = False
        placement_data.Trigger_SS_TIsland12_Tutorial_0100.NotSpawnFinal = False
        placement_data.Trigger_SS_TIsland12_Tutorial_Enable.NotSpawnFinal = False
        placement_data.Trigger_SS_TIsland12_Tutorial_Ongoing.NotSpawnFinal = False
        # placement_data.Trigger_SS_TIsland13_Tutorial_0100.NotSpawnFinal = False
        placement_data.Trigger_SS_TIsland13_Tutorial_Enable.NotSpawnFinal = False
        placement_data.Trigger_SS_TIsland13_Tutorial_Ongoing.NotSpawnFinal = False
        placement_data.Trigger_SS_TMount12_Tutorial_0100.NotSpawnFinal = False
        placement_data.Trigger_SS_TMount12_Tutorial_Enable.NotSpawnFinal = False
        placement_data.Trigger_SS_TMount12_Tutorial_Ongoing.NotSpawnFinal = False
        placement_data.Trigger_SS_TSea13_Tutorial_0100.NotSpawnFinal = False
        placement_data.Trigger_SS_TSea13_Tutorial_Enable.NotSpawnFinal = False
        placement_data.Trigger_SS_TSea13_Tutorial_Ongoing.NotSpawnFinal = False
        placement_data.Trigger_SS_TSnow12_Tutorial_0100.NotSpawnFinal = False
        placement_data.Trigger_SS_TSnow12_Tutorial_Enable.NotSpawnFinal = False
        placement_data.Trigger_SS_TSnow12_Tutorial_Ongoing.NotSpawnFinal = False
        placement_data.Trigger_SS_TWilderness13_Tutorial_0100.NotSpawnFinal = False
        placement_data.Trigger_SS_TWilderness13_Tutorial_Enable.NotSpawnFinal = False
        placement_data.Trigger_SS_TWilderness13_Tutorial_Ongoing.NotSpawnFinal = False

        # Scent of Commerce events
        placement_data.EV_TRIGGER_MS_SHO_EX3_0100.NotSpawnFinal = False
        placement_data.EV_TRIGGER_MS_SHO_EX3_0110.NotSpawnFinal = False
        placement_data.EV_TRIGGER_MS_SHO_EX1_0100.NotSpawnFinal = False
        placement_data.EV_TRIGGER_MS_SHO_EX1_0110.NotSpawnFinal = False
        placement_data.EV_TRIGGER_MS_SHO_EX2_0100.NotSpawnFinal = False
        placement_data.EV_TRIGGER_MS_SHO_EX2_0200.NotSpawnFinal = False
        placement_data.NPC_SHO_EX3_0100_0000.NotSpawnFinal = False
        placement_data.NPC_SHO_EX3_0100_0010.NotSpawnFinal = False
        placement_data.NPC_SHO_EX3_0200_0000.NotSpawnFinal = False
        placement_data.NPC_SHO_EX1_0120_0000.NotSpawnFinal = False
        placement_data.NPC_SHO_EX2_0100_0000.NotSpawnFinal = False

        ######## Day & Night Display ########
        radar = Manager.get_asset('BP/RadarMap')
        initialize = radar.get_uexp_obj_2(16)
        initialize.patch_uint64(0x0000000200000273, 0x117d)

    #######################
    # LINK FLAGS TO ITEMS #
    #######################

    # Guilds
    if EventsAndItems.include_guild_spawn:
        placement_data.NPC_Twn_Dst_2_1_A_GUILD.SpawnStartFlag = candidates['unlock_guild_war'].flag
        placement_data.NPC_Fld_Isd_2_1_GUILD.SpawnStartFlag = candidates['unlock_guild_hun'].flag
        placement_data.NPC_Twn_Sea_2_1_A_GUILD.SpawnStartFlag = candidates['unlock_guild_apo'].flag
        placement_data.NPC_Fld_Wld_2_1_GUILD.SpawnStartFlag = candidates['unlock_guild_mer'].flag
        placement_data.NPC_Fld_Mnt_2_2_GUILD.SpawnStartFlag = candidates['unlock_guild_cle'].flag
        placement_data.NPC_Fld_Snw_2_2_GUILD.SpawnStartFlag = candidates['unlock_guild_sch'].flag
        placement_data.NPC_Twn_Cty_2_1_B_GUILD.SpawnStartFlag = candidates['unlock_guild_thi'].flag
        placement_data.NPC_Twn_Fst_2_1_A_GUILD.SpawnStartFlag = candidates['unlock_guild_dan'].flag
        placement_data.NPC_Fld_Cty_1_3_GUILD.SpawnStartFlag = candidates['unlock_guild_inv'].flag
        placement_data.NPC_Twn_Wld_3_1_A_GUILD.SpawnStartFlag = candidates['unlock_guild_arm'].flag
        placement_data.NPC_JOB_WIZ_0100_0000.SpawnStartFlag = candidates['unlock_guild_arc'].flag

    # Altars
    if EventsAndItems.include_altar_spawn:
        placement_data.EV_TRIGGER_KEN_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_war'].flag
        placement_data.EV_TRIGGER_KAR_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_hun'].flag
        placement_data.EV_TRIGGER_KUS_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_apo'].flag
        placement_data.EV_TRIGGER_SHO_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_mer'].flag
        placement_data.EV_TRIGGER_SIN_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_cle'].flag
        placement_data.EV_TRIGGER_GAK_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_sch'].flag
        placement_data.EV_TRIGGER_TOU_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_thi'].flag
        placement_data.EV_TRIGGER_ODO_ADVANCED_ABILITY_0000.SpawnStartFlag = candidates['unlock_altar_dan'].flag

    # NPCs
    if EventsAndItems.include_assassins_spawn:
        placement_data.NPC_Fld_Mnt_3_2_TALK_0100_N000.SpawnStartFlag = candidates['unlock_foreign_assassins'].flag

    if EventsAndItems.include_assassins:
        placement_data.NPC_Fld_Mnt_3_2_TALK_0100_N000.EventEndFlag_A = candidates['end_foreign_assassins_battle'].flag
        placement_data.NPC_Fld_Mnt_3_2_TALK_0100_N000.EventStartFlag_B = candidates['end_foreign_assassins_battle'].flag

    # Make Northern Montwise Pass Guard unbeatable
    if EventsAndItems.include_guard:
        placement_data.CLOSE_TRIGGER_Fld_Mnt_2_1_0100.SpawnEndFlag = candidates['unlock_snow_guard'].flag
        npc_data.NPC_Fld_Mnt_2_1_TALK_0100.FCmd_Battle_ID = 'None'
        npc_data.NPC_Fld_Mnt_2_1_TALK_0100.FCmd_Search_ID = 'None'
        npc_data.NPC_Fld_Mnt_2_1_TALK_0100.FCmd_Lure_ID = 'None'

    # Boats
    if EventsAndItems.include_ships_spawn:
        placement_data.NPC_SYS_LINERSHIP_5001.SpawnStartFlag = candidates['unlock_new_delsta_ship'].flag
        placement_data.NPC_SYS_LINERSHIP_5002.SpawnStartFlag = candidates['unlock_beasting_bay_ship'].flag
        placement_data.NPC_SYS_LINERSHIP_5003.SpawnStartFlag = candidates['unlock_crackridge_ship'].flag
        placement_data.NPC_SYS_LINERSHIP_0000.SpawnStartFlag = candidates['unlock_canalbrine_ship'].flag

    if EventsAndItems.include_main_story:
        # Dng_Dst_3_1 -- Hikari & Agnea
        placement_data.EV_TRIGGER_MS_END_2D_TIPS_0100.SpawnStartFlag = candidates['unlock_flame_grotto'].flag
        placement_data.EV_TRIGGER_MS_END_2D_TIPS_0300_10.SpawnStartFlag = candidates['unlock_flame_grotto'].flag
        placement_data.EV_TRIGGER_MS_END_2D_TIPS_0300_20.SpawnStartFlag = candidates['unlock_flame_grotto'].flag

        # Dng_Isd_1_1 -- Ochette & Castti Flame
        placement_data.EV_TRIGGER_MS_END_2C_TIPS_01A0.SpawnStartFlag = candidates['unlock_flame_tomb'].flag
        placement_data.EV_TRIGGER_MS_END_2C_TIPS_0300_10.SpawnStartFlag = candidates['unlock_flame_tomb'].flag
        placement_data.EV_TRIGGER_MS_END_2C_TIPS_0300_20.SpawnStartFlag = candidates['unlock_flame_tomb'].flag
        placement_data.EV_TRIGGER_MS_END_2C_0010.SpawnStartFlag = candidates['unlock_flame_tomb'].flag

        # Dng_Wld_2_2 -- Osvald & Partitio Flame
        placement_data.EV_TRIGGER_MS_END_2B_TIPS_01A0.SpawnStartFlag = candidates['unlock_flame_ruins'].flag
        placement_data.EV_TRIGGER_MS_END_2B_TIPS_0300_10.SpawnStartFlag = candidates['unlock_flame_ruins'].flag
        placement_data.EV_TRIGGER_MS_END_2B_TIPS_0300_20.SpawnStartFlag = candidates['unlock_flame_ruins'].flag

        # Twn_Mnt_1_1_A -- Throne & Temenos
        placement_data.EV_TRIGGER_MS_END_2A_0010.SpawnStartFlag = candidates['unlock_flame_church'].flag
        # Twn_Mnt_1_2_A -- Throne & Temenos
        placement_data.EV_ITEM_MS_END_2A_0100.SpawnStartFlag = candidates['unlock_flame_church'].flag

        # Scent of commerce
        placement_data.EV_TRIGGER_MS_SHO_EX1_0100.SpawnStartFlag = candidates['unlock_soc_grand_terry'].flag
        placement_data.EV_TRIGGER_MS_SHO_EX2_0100.SpawnStartFlag = candidates['unlock_soc_gramophone'].flag
        placement_data.EV_TRIGGER_MS_SHO_EX3_0100.SpawnStartFlag = candidates['unlock_soc_manuscript'].flag

    if EventsAndItems.include_galdera_items:
        # Allow "Give Al his bag back" cutscene to tigger as soon as you have Al's bag
        # rather than as soon as you fight the thief.
        placement_data.NPC_SS_TCity13_Tutorial_0100.EventStartFlag_A = candidates['item_als_bag'].flag
        placement_data.NPC_SS_TDesert11_Tutorial_0100.EventStartFlag_A = candidates['item_als_bag'].flag
        placement_data.NPC_SS_TForest13_Tutorial_0100.EventStartFlag_A = candidates['item_als_bag'].flag
        placement_data.NPC_SS_TIsland12_Tutorial_0100.EventStartFlag_A = candidates['item_als_bag'].flag
        placement_data.NPC_SS_TIsland13_Tutorial_0100.EventStartFlag_A = candidates['item_als_bag'].flag
        placement_data.NPC_SS_TMount12_Tutorial_0100.EventStartFlag_A = candidates['item_als_bag'].flag
        placement_data.NPC_SS_TSea13_Tutorial_0100.EventStartFlag_A = candidates['item_als_bag'].flag
        placement_data.NPC_SS_TSnow12_Tutorial_0100.EventStartFlag_A = candidates['item_als_bag'].flag
        placement_data.NPC_SS_TWilderness13_Tutorial_0100.EventStartFlag_A = candidates['item_als_bag'].flag

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

    elif EventsAndItems.include_pcs:
        # Default story but shuffled PCs
        # Unlock stories with new PC flags
        # Default PC flags are still set in recruit events
        # to help manage NPCs
        # Skip the protagonist who will never get their flag set!
        assert not EventsAndItems.include_main_story

        if start_pc != 'Hikari':
            main_story.MS_KEN_01.ReleaseFlag[0] = candidates['item_hikari'].flag

        if start_pc != 'Ochette':
            main_story.MS_KAR_01.ReleaseFlag[0] = candidates['item_ochette'].flag
            main_story.MS_KAR_02.ReleaseFlag[0] = candidates['item_ochette'].flag
            main_story.MS_KAR_03.ReleaseFlag[0] = candidates['item_ochette'].flag

        if start_pc != 'Castti':
            main_story.MS_KUS_01.ReleaseFlag[0] = candidates['item_castti'].flag
            main_story.MS_KUS_02.ReleaseFlag[0] = candidates['item_castti'].flag

        if start_pc != 'Partitio':
            main_story.MS_SHO_01.ReleaseFlag[0] = candidates['item_partitio'].flag
            main_story.MS_SHO_10.ReleaseFlag[0] = candidates['item_partitio'].flag
            main_story.MS_SHO_11.ReleaseFlag[0] = candidates['item_partitio'].flag
            main_story.MS_SHO_12.ReleaseFlag[0] = candidates['item_partitio'].flag
            placement_data.EV_TRIGGER_MS_SHO_EX1_0100.SpawnStartFlag = candidates['item_partitio'].flag
            placement_data.EV_TRIGGER_MS_SHO_EX2_0100.SpawnStartFlag = candidates['item_partitio'].flag
            placement_data.EV_TRIGGER_MS_SHO_EX3_0100.SpawnStartFlag = candidates['item_partitio'].flag

        if start_pc != 'Temenos':
            main_story.MS_SIN_01.ReleaseFlag[0] = candidates['item_temenos'].flag

        if start_pc != 'Osvald':
            main_story.MS_GAK_02.ReleaseFlag[0] = candidates['item_osvald'].flag

        if start_pc != 'Throne':
            main_story.MS_TOU_01.ReleaseFlag[0] = candidates['item_throne'].flag
            main_story.MS_TOU_02.ReleaseFlag[0] = candidates['item_throne'].flag

        if start_pc != 'Agnea':
            main_story.MS_ODO_01.ReleaseFlag[0] = candidates['item_agnea'].flag


    ###################
    # Updates for PCs #
    ###################

    if EventsAndItems.include_pcs:
        # Remove recruit events from the world map
        main_story.MS_KEN_00.StartWMapLocation = 'None'
        main_story.MS_KUS_00.StartWMapLocation = 'None'
        main_story.MS_KAR_00.StartWMapLocation = 'None'
        main_story.MS_SHO_00.StartWMapLocation = 'None'
        main_story.MS_SIN_00.StartWMapLocation = 'None'
        main_story.MS_GAK_00.StartWMapLocation = 'None'
        main_story.MS_TOU_00.StartWMapLocation = 'None'
        main_story.MS_ODO_00.StartWMapLocation = 'None'

        ## DOES NOTHING
        # main_story.MS_GAK_01.StartWMapLocation = 'None'
        # main_story.MS_GAK_01.ReleaseFlag[0] = 0
        ## Prevent Osvald Ch 2 from spawning on world map
        ## NEVER set flag 7020
        placement_data.NPC_PROFESSOR_0000_0100.SpawnEndFlag = 37517
        placement_data.NPC_PROFESSOR_0000_0100.EventEndFlag_A = placement_data.NPC_PROFESSOR_0000_0100.SpawnEndFlag

        # Replace all scripts with the appropriate template
        def patch_recruit(name):
            # Skip for the starting PC since it's slot is omitted
            slot_name = f'get_{name}'
            if not slot_manager.has_slot(slot_name):
                return

            patch = Script.load(f'scripts/recruit_{name}')
            for slot in slot_manager.get_slot_list(slot_name):
                slot.script.insert_script(patch, 0)
                slot.indices = [len(patch.json_list)-1]

        patch_recruit('hikari')
        patch_recruit('ochette')
        patch_recruit('castti')
        patch_recruit('partitio')
        patch_recruit('temenos')
        patch_recruit('osvald')
        patch_recruit('throne')
        patch_recruit('agnea')


    ################
    # TEXT UPDATES #
    ################

    if EventsAndItems.include_pcs:
        gameText = Manager.get_table('GameTextEN')

        # Text displayed when recruiting PCs and asking if you want to play their chapter 1
        gameText.PROLOGUE_FLASHBACK.Text = "The flashback won't work here.\nJust skip it."

    if EventsAndItems.include_ex_abil:
        gameText = Manager.get_table('GameTextEN')

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
            reward = Script.load('scripts/inventor_reward')
            for ci in c:
                reward.insert_script(candidates[ci].script, 8)
            add_scripts_notcand(reward, s)
        elif s == 'finish_guild_arm':
            reward = Script.load('scripts/armsmaster_reward')
            for ci in c:
                reward.insert_script(candidates[ci].script, 1)
            add_scripts_notcand(reward, s)
        elif slot_manager.has_slot(s):
            for ci in c:
                add_scripts(ci, s)
        else:
            print('TODO: slot', s, 'must be filled manually')

    for pc in other_pcs:
        add_scripts(f'item_{pc}', 'finish_chapter_1')

    ###########################
    # Finalize Key Item Stuff #
    ###########################

    if EventsAndItems.include_key_items:
        # Horse Coin
        add_delivery('NPC_TOU_2A_0400_0000', 'ITM_TRE_TOU_2A_0010', '1')
        # Mask
        add_delivery('NPC_TOU_2A_0300_0000', 'ITM_TRE_TOU_2A_0020', '1')
        # Habit
        add_delivery('EV_TRIGGER_MS_TOU_3A_0300', 'ITM_TRE_TOU_3A_0010', '1')
        # Harvey Info
        add_delivery('EV_TRIGGER_MS_GAK_40_0520', 'ITM_INF_GAK_40_05C0', '1', 'ITM_INF_GAK_40_05A0', '1', 'ITM_INF_GAK_40_05B0', '1')
        # Black Crystals
        add_delivery('EV_TRIGGER_MS_GAK_50_0600', 'ITM_TRE_GAK_50_0010', '5')
        # Weapons Deal Details
        add_delivery('EV_TRIGGER_MS_KEN_30_0400', 'ITM_INF_KEN_30_0100', '1')
        # True Identity knowledge
        default_item = candidates['item_vados_info']
        # End whenever the true identity knowledge gets aquired
        placement_data.CLOSE_TRIGGER_SIN_20_0200.SpawnEndFlag = default_item.flag
        placement_data.NACT_SIN_20_0100_0000.SpawnEndFlag = default_item.flag
        placement_data.NACT_SIN_20_0200_0000.SpawnEndFlag = default_item.flag
        placement_data.NACT_SIN_20_0400_0000.SpawnEndFlag = default_item.flag
        placement_data.NACT_SIN_20_0800_0000.SpawnEndFlag = default_item.flag
        # Mysterious Notebook
        item = candidates[rando_map['get_mysterious_notebook'][0]]
        treasures.EventItem_MS_SIN_3B_0100.HaveItemLabel = item.item_key
        treasures.EventItem_MS_SIN_3B_0100_1000.HaveItemLabel = item.item_key
        slot = slot_manager.get_slot('get_mysterious_notebook')
        assert len(slot.subscripts) == 1
        subscript = list(slot.subscripts.keys())[0]
        subscript.remove_give_item(item.item_key)
        subscript.remove_display_item(item.item_key)
        add_delivery('EV_TRIGGER_MS_SIN_3B_1000', 'ITM_TRE_SIN_3B_0020', '1')
        # Kaldena's Notebook
        add_delivery('EV_TRIGGER_MS_SIN_40_03A0', 'ITM_TRE_SIN_3B_0030', '1')
        add_delivery('EV_TRIGGER_MS_SIN_40_03B0', 'ITM_TRE_SIN_3B_0030', '1')
        add_delivery('EV_TRIGGER_MS_SIN_40_03C0', 'ITM_TRE_SIN_3B_0030', '1')
        # Remove receiving Mother's Key from its cutscene
        assert not slot_manager.has_file('MS_TOU_3A_1000')
        mom_key_script = Manager.get_json('MS_TOU_3A_1000')
        mom_key_script.remove_command(9)
        # Remove receiving Fathers's Key from its cutscene
        assert not slot_manager.has_file('MS_TOU_3B_1000')
        dad_key_script = Manager.get_json('MS_TOU_3B_1000')
        dad_key_script.remove_command(11)
        # Make door dependent on having both Mother's and Father's keys
        add_delivery('EV_TRIGGER_MS_TOU_40_0410', 'ITM_TRE_TOU_3A_0030', '1', 'ITM_TRE_TOU_3B_0010', '1')
        # Beasts
        acta = candidates['item_beast_acta']
        tera = candidates['item_beast_tera']
        glacis = candidates['item_beast_glacis']
        add_delivery('EV_TRIGGER_MS_KAR_30_0200', acta.item_key, '1', tera.item_key, '1', glacis.item_key, '1')
        # Crosspath Throne & Temenos
        # Move guard after collecting Folded Paper
        item = candidates[rando_map['get_folded_paper'][0]]
        npc_copy_shift('NPC_COP_ST2_0100_0000', 'Twn_Sea_2_1_B', item.flag, dy=-100)
        # Require both Cloudy Mirror Fragment and Folded Paper to trigger
        # cutscene in the Cavern of the Moon and Sun
        add_delivery('EV_TRIGGER_MS_COP_ST2_0500', 'ITM_TRE_COP_ST1_0010', '1', 'ITM_TRE_COP_ST2_0010', '1')

    if EventsAndItems.include_galdera_items:
        # Move guard after collecting From the Far Reaches of Hell
        item = candidates[rando_map['get_tome_hell'][0]]
        npc_copy_shift('NPC_Twn_Wld_2_1_A_TALK_1900_D000', 'Twn_Wld_2_1_A', item.flag, dy=200)

    if EventsAndItems.include_rusty_weapons:
        # Rusty sword
        item = candidates[rando_map['get_rusty_sword'][0]]
        sub = substory.SS_SNW2_0200
        sub.RewardParam.pop(0) # Remove Rusty sword from sidequest reward
        sub.RewardParam.pop(0)
        sub.RewardParam += ['None', 'None']
        assert not slot_manager.has_file('SC_SS_TSnow21_0200_02A0')
        script = Manager.get_json('SC_SS_TSnow21_0200_02A0')
        script.insert_script(item.script, 70)
        # Move rusty polearm guard
        item = candidates[rando_map['get_rusty_polearm'][0]]
        npc_copy_shift('NPC_Twn_Fst_3_1_B_TALK_0900_D000', 'Twn_Fst_3_1_B', item.flag, dy=120)
        
    if EventsAndItems.include_inventor_parts:
        # Move mythical horn guard
        item = candidates[rando_map['get_mythical_horn'][0]]
        npc_copy_shift('NPC_Twn_Isd_3_1_A_TALK_0700_D000', 'Twn_Isd_3_1_A', item.flag, dx=-60, dy=120)
        npc_copy_shift('SIN_40_NPC_Twn_Isd_3_1_A_TALK_0700_D000', 'Twn_Isd_3_1_A', item.flag, dx=-60, dy=140)
        
    # ###### REPLACE ITEM ######
    # def replace_slot(candname, slotname):
    #     # cand = candidates[candname]
    #     # Only works if one file is modified!
    #     slot = slot_manager.get_slot(slotname)
    #     slot.subscripts = {}
    #     add_scripts(candname, slotname)

    # # replace_slot('item_tin_toy', 'get_tin_toy')

    ##############################################
    # FINALIZE EVENTS AFFECTED BY SPECIFIC FLAGS #
    ##############################################

    def set_recruit_flags(pc, *keys):
        slot_name = f'get_{pc}'
        if EventsAndItems.include_pcs and slot_name in rando_map:
            # PCs are shuffled and PC is not recruited when chapter 1 finishes
            # Must ensure recruitment event stays on until it's item is received
            item = candidates[rando_map[slot_name][0]]
            flag = item.flag
        elif pc in other_pcs:
            # PC is gotten at the end of chapter 1
            # Regardless of whether PCs are shuffled,
            # make sure the PC's event can never occur
            flag = 9000
        else:
            # Don't do anything for the protagonist
            # (could do the same as other_pcs, actually....)
            return

        for key in keys:
            p = getattr(placement_data, key)
            p.SpawnEndFlag = flag

    set_recruit_flags('hikari', 'NPC_FENCER_0000_0000', 'NPC_FENCER_0000_0100', \
                      'NPC_FENCER_0000_0200', 'NPC_FENCER_0000_0300', 'NPC_FENCER_0000_0400', \
                      'NPC_FENCER_0000_0500', 'NPC_FENCER_0000_0600', 'NPC_FENCER_0000_0700')
    set_recruit_flags('ochette', 'NPC_HUNTER_0000_0000')
    set_recruit_flags('castti', 'NPC_ALCHEMIST_0000_0200', 'NPC_ALCHEMIST_0000_0300')
    set_recruit_flags('partitio', 'PC_Party_Join_SHO_0000')
    set_recruit_flags('temenos', 'CLOSE_TRIGGER_SIN_10_0200', 'NPC_PRIEST_0000_0000', 'NPC_PRIEST_0000_0300')
    set_recruit_flags('osvald', 'NPC_PROFESSOR_0000_0000')
    set_recruit_flags('throne', 'NPC_THIEF_0000_0000', 'NPC_THIEF_0000_0100', 'NPC_THIEF_0000_0300', 'NPC_THIEF_0000_0400')
    set_recruit_flags('agnea', 'NPC_DANCER_0000_0000', 'NPC_DANCER_0000_0100', 'NPC_DANCER_0000_0000_0010')

    if EventsAndItems.include_main_story:
        # Always a possibility of flame extinguishing before recruiting temenos
        # Move him so he can always be accessed
        placement_data.NPC_PRIEST_0000_0000.SpawnEndFlag = 9000
        placement_data.NPC_PRIEST_0000_0100.SpawnStartFlag = 9000
        placement_data.NPC_PRIEST_0000_0100.EventStartFlag_A = 9000
        placement_data.NPC_PRIEST_0000_0100.SpawnPosX -= 1600
        if start_pc == 'Temenos':
            # Don't let Temenos spawn if he is the protagonist
            placement_data.NPC_PRIEST_0000_0100.SpawnEndFlag = 9000
        elif 'get_temenos' in rando_map: # e.g. include_pcs = True
            # Let Temenos spawn until his swapped item has been received
            item = candidates[rando_map['get_temenos'][0]]
            placement_data.NPC_PRIEST_0000_0100.EventEndFlag_A = item.flag
            placement_data.NPC_PRIEST_0000_0100.SpawnEndFlag = item.flag
        else:
            print('Temenos recruitment is moved but will still spawn normally until collected')

    ####################
    # FOREIN ASSASSINS #
    ####################

    if EventsAndItems.include_assassins:
        # Need to change the flag set since 25520 is also linked to Hired Help Foreign Assassin
        slot = slot_manager.get_slot('get_hire_foreign_assassins')
        slot.script.change_flag(25520, candidates['end_foreign_assassins_battle'].flag)

    #########
    # BUILD #
    #########

    ### TESTING ONLY ###
    # add_scripts('item_grand_terry', 'finish_chapter_1')
    # add_scripts('item_als_bag', 'get_als_bag')
    # for c in candidates:
    #     add_scripts(c, 'finish_the_travelers_bag')
    ####################

    slot_manager.finalize()

    ###########
    # PATCHES #
    ###########

    if EventsAndItems.include_main_story:
        patch_end_on = Script.load('scripts/patch_toggle_end_on')
        patch_end_off = Script.load('scripts/patch_toggle_end_off')

        ################################
        # EXTINGUISH FLAMECHURCH FLAME #
        ################################

        script = Manager.get_json('MS_END_2A_0020')
        patch = Script.load('scripts/patch_extinguish_flamechurch_flame')
        script.insert_script(patch, -1)

        #####################################################
        # REMOVE FLAME EXTINGUISH AFTER REIGNITING COMMANDS #
        #####################################################

        filenames = [
            'MS_KAR_30_2500', 'MS_SIN_40_1200', 'MS_GAK_50_1300', 'MS_COP_OK2_0800',
            'MS_SHO_40_1800', 'MS_KUS_40_1200', 'MS_KEN_50_2000', 'MS_END_10_01D0',
        ]

        for filename in filenames:
            script = Manager.get_json(filename)
            script.filter_out_command(8920)

        ############################################
        # EVENTS DURING END BEFORE IGNITING FLAMES #
        ############################################

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

        ############################################
        #### Prevent Ochette w/o Acta Softlocks ####
        ############################################

        # Seems to work for both bosses
        hun_bos_A = Manager.get_asset('ENG_BOS_HUN_C03_010_A')
        export = hun_bos_A.get_uexp_obj_2(16)
        export.toggle_bool_off(0x2a)

        # Included just in case
        hun_bos_B = Manager.get_asset('ENG_BOS_HUN_C03_010_B')
        export = hun_bos_B.get_uexp_obj_2(14)
        export.toggle_bool_off(0x2a)

        ######################
        # OCHETTE 2A AFTER 3 #
        ######################

        # Make sure acta won't get added if it is shuffled as a key
        # item.  The check for beating ochette ch 3 is included in the
        # acta item scripts.
        if not EventsAndItems.include_key_items:
            # prevent receiving a second acta
            patch_ochette = Script.load('scripts/patch_ochette_2a')
            script = Manager.get_json('MS_KAR_2A_0600')
            script.insert_script(patch_ochette, -1)
            script = Manager.get_json('MS_KAR_2M_01A0')
            script.insert_script(patch_ochette, -1)

        ###########################
        # MUSIC IS ON FOR BATTLES #
        ###########################

        # Recruit Temenos battle is fine as is; no need to mod.
        # Hikari & Throne have bugs if playing without
        # including PCs in the item pool.
        # Just ignore their lack of music.
        
        # # Recruit Throne battle
        # start_battle = Manager.get_json('MS_TOU_00_0100')
        # start_battle.insert_script(patch_end_off, 49)
        # start_battle = Manager.get_json('MS_TOU_00_0200')
        # start_battle.insert_script(patch_end_off, 24)
        # end_battle = Manager.get_json('MS_TOU_00_0300')
        # end_battle.insert_script(patch_end_on, 0)

        # # Recruit Hikari battle
        # start_battle = Manager.get_json('MS_KEN_00_0100')
        # start_battle.insert_script(patch_end_off, 66)
        # start_battle = Manager.get_json('MS_KEN_00_0200')
        # start_battle.insert_script(patch_end_off, 46)
        # end_battle = Manager.get_json('MS_KEN_00_0300')
        # end_battle.insert_script(patch_end_on, 0)

        #### These work for typical battles.
        #### Key Item battles can finish with different scripts,
        #### resulting in all flags staying off.
        #### Keep for reference, but need to find a more general solution.
        # # Osvald Mug
        # start = Manager.get_json('FC_GAK_ROB_Before_1')
        # start.insert_script(patch_end_off, 0)
        # start = Manager.get_json('FC_GAK_ROB_Before_2')
        # start.insert_script(patch_end_off, 0)
        # end = Manager.get_json('FC_GAK_ROB_Failure')
        # end.insert_script(patch_end_on, 0)
        # end = Manager.get_json('FC_GAK_ROB_Success')
        # end.insert_script(patch_end_on, 0)

        # # Temenos Inquire
        # start = Manager.get_json('FC_SIN_REVEAL_Before_1')
        # start.insert_script(patch_end_off, 0)
        # start = Manager.get_json('FC_SIN_REVEAL_Before_2')
        # start.insert_script(patch_end_off, 0)
        # end = Manager.get_json('FC_SIN_REVEAL_Failure')
        # end.insert_script(patch_end_on, 0)
        # end = Manager.get_json('FC_SIN_REVEAL_Success_1')
        # end.insert_script(patch_end_on, 0)
        # end = Manager.get_json('FC_SIN_REVEAL_Success_2')
        # end.insert_script(patch_end_on, 0)

        # # Hikari Battle
        # start = Manager.get_json('FC_KEN_BATTLE_Before_1')
        # start.insert_script(patch_end_off, 0)
        # start = Manager.get_json('FC_KEN_BATTLE_Before_2')
        # start.insert_script(patch_end_off, 0)
        # end = Manager.get_json('FC_KEN_BATTLE_Failure')
        # end.insert_script(patch_end_on, 0)
        # end = Manager.get_json('FC_KEN_BATTLE_Success')
        # end.insert_script(patch_end_on, 0)

        # # Ochette Battle
        # start = Manager.get_json('FC_KAR_MONSTER_Before_1')
        # start.insert_script(patch_end_off, 0)
        # start = Manager.get_json('FC_KAR_MONSTER_Before_2')
        # start.insert_script(patch_end_off, 0)
        # end = Manager.get_json('FC_KAR_MONSTER_Failure')
        # end.insert_script(patch_end_on, 0)
        # end = Manager.get_json('FC_KAR_MONSTER_Success')
        # end.insert_script(patch_end_on, 0)


    #################
    # ENEMY SCALING #
    #################

    if EventsAndItems.include_key_items:
        #### OCEAN ENCOUNTERS ####
        enc_vol = Manager.get_table('EncountVolumeData')

        vol1d = deepcopy(enc_vol.EVM_DNG_MNT_1_1_WTR_DAY.EncounterList[0]) # 5
        vol1n = deepcopy(enc_vol.EVM_DNG_MNT_1_1_WTR_NGT.EncounterList[0]) # 5
        vol2d = deepcopy(enc_vol.EVM_FLD_DST_1_1_WTR_DAY.EncounterList[0]) # 11
        vol2n = deepcopy(enc_vol.EVM_FLD_DST_1_1_WTR_NGT.EncounterList[0]) # 11
        vol3d = deepcopy(enc_vol.EVM_FLD_CTY_2_1_WTR_DAY.EncounterList[2]) # 22
        vol3n = deepcopy(enc_vol.EVM_FLD_CTY_2_1_WTR_NGT.EncounterList[2]) # 22
        vol4d = deepcopy(enc_vol.EVM_FLD_OCN_1_1_SEA_1_DAY.EncounterList[0]) # 34
        vol4n = deepcopy(enc_vol.EVM_FLD_OCN_1_1_SEA_1_NGT.EncounterList[0]) # 34

        vol1d['ProgressBorder'].value = 0
        vol1n['ProgressBorder'].value = 0
        vol2d['ProgressBorder'].value = 8
        vol2n['ProgressBorder'].value = 8
        vol3d['ProgressBorder'].value = 24
        vol3n['ProgressBorder'].value = 24
        vol4d['ProgressBorder'].value = 40
        vol4n['ProgressBorder'].value = 40

        enc_vol.EVM_FLD_OCN_1_1_SEA_1_DAY.EncounterList[0] = vol1d
        enc_vol.EVM_FLD_OCN_1_1_SEA_1_NGT.EncounterList[0] = vol1n
        enc_vol.EVM_FLD_OCN_1_1_SEA_1_DAY.EncounterList[1] = vol2d
        enc_vol.EVM_FLD_OCN_1_1_SEA_1_NGT.EncounterList[1] = vol2n
        enc_vol.EVM_FLD_OCN_1_1_SEA_1_DAY.EncounterList[2] = vol3d
        enc_vol.EVM_FLD_OCN_1_1_SEA_1_NGT.EncounterList[2] = vol3n
        enc_vol.EVM_FLD_OCN_1_1_SEA_1_DAY.EncounterList[3] = vol4d
        enc_vol.EVM_FLD_OCN_1_1_SEA_1_NGT.EncounterList[3] = vol4n


def add_new_items():
    items = Manager.get_table('ItemDB')
    gameText = Manager.get_table('GameTextEN')
    
    # Load all data
    with open(get_filename('json/candidates.json'), 'r', encoding='utf-8') as file:
        candidates = hjson.load(file)

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

    for unlock, data in candidates.items():
        add_item(data)

    # Manually add Black Crystals
    items.duplicate_data('ITM_TRE_GAK_50_0010', 'ITM_TRE_GAK_50_0010_2')
    items.duplicate_data('ITM_TRE_GAK_50_0010', 'ITM_TRE_GAK_50_0010_3')
    items.duplicate_data('ITM_TRE_GAK_50_0010', 'ITM_TRE_GAK_50_0010_4')
    items.duplicate_data('ITM_TRE_GAK_50_0010', 'ITM_TRE_GAK_50_0010_5')


def load_candidates():
    with open(get_filename('json/candidates.json'), 'r', encoding='utf-8') as file:
        cand_data = hjson.load(file)

    candidates = {}
    for unlock, data in cand_data.items():
        assert unlock not in candidates, unlock
        candidates[unlock] = CandidateWithFlag.data_factory(unlock, data)

    return candidates


def load_slots(rando_map, rando_map_inv):
    with open(get_filename('json/slots.json'), 'r', encoding='utf-8') as file:
        slot_data = hjson.load(file)

    slot_manager = SlotManager()
    for slotname, slots in slot_data.items():
        # ONLY load slots that are needed.
        if slotname in rando_map:
            for data in slots:
                filename = data['filename']
                insert = data['insert']
                remove = data['remove']
                item = data['item']
                if item in rando_map_inv:
                    # remove default item from script
                    slot_manager.create_slot(filename, slotname, insert, remove)
                else:
                    slot_manager.create_slot(filename, slotname, insert)

    if EventsAndItems.include_key_items:
        # Agnea 2: Theater Ticket (formerly new_change_shop_item; no need for a new script)
        slot_manager.create_slot_shop('get_theater_ticket', 'NPC_ODO_20_0100_0000', 'NPC_ODO_20_0100_NPCBUY_01', 0, new_script=False)

        # Agnea 3: Wooden Sword
        slot_manager.create_slot_shop('get_wooden_sword', 'NPC_ODO_30_0500_0000', 'NPC_ODO_30_0500_NPCBUY_01', 0, new_script=False)

        # Agnea 4: Cute Shoes
        slot_manager.create_slot_shop('get_cute_shoes', 'NPC_ODO_40_0100_0000', 'NPC_ODO_40_0100_NPCBUY_01', 0, new_script=False)

        # Castti 2 (Winterbloom Route): Rosa's Medicine
        assert slot_manager.has_slot('get_rosas_medicine')

        # Hikari 3: Weapons Deal Details
        slot_manager.create_slot_hear('hear_weapons_deal_details', 'NPC_KEN_30_0100_0000', 'FC_INFOLINK_NPC_KEN_30_0100', -1, new_script=False)
        add_delivery('EV_TRIGGER_MS_KEN_30_0400', 'ITM_INF_KEN_30_0100', '1')

        # Ochette 2: Beasts
        assert slot_manager.has_slot('finish_chapter_ochette_2a') # Acta
        assert slot_manager.has_slot('finish_chapter_ochette_2b') # Tera
        assert slot_manager.has_slot('finish_chapter_ochette_2c') # Glacis
        enemies = Manager.get_table('EnemyDB')
        enemies.ENE_BOS_HUN_C02_010.TameEnable = False # Tera
        enemies.ENE_BOS_HUN_C02_010.LegendTameMonster = False
        enemies.ENE_BOS_HUN_C02_010.InvadeMonsterID = 'None'
        enemies.ENE_BOS_HUN_C02_020.TameEnable = False # Glacis
        enemies.ENE_BOS_HUN_C02_020.LegendTameMonster = False
        enemies.ENE_BOS_HUN_C02_020.InvadeMonsterID = 'None'

        # Temenos 2: The Cuplrit's True Identity
        slot_manager.create_slot_hear('hear_vados_info', 'NPC_SIN_20_1000_0000', 'FC_INFOLINK_NPC_SIN_20_1000', 0)
        slot_manager.create_slot_hear('hear_vados_info', 'NPC_SIN_20_1010_0000', 'FC_INFOLINK_NPC_SIN_20_1010', 0, new_script=False)

        # Temenos 3 (Crackridge Route): Mysterious Notebook
        assert slot_manager.has_slot('get_mysterious_notebook')

        # Throne 2 (Mother's Route): Mask
        slot_manager.create_slot_shop('get_mask', 'NPC_TOU_2A_0200_0000', 'NPC_TOU_2A_0200_NPCBUY_01', -1, new_script=False)
        add_delivery('NPC_TOU_2A_0300_0000', 'ITM_TRE_TOU_2A_0020', '1')

        # Throne 2 (Mother's Route): Horse Coin
        slot_manager.create_slot_shop('get_horse_coin', 'NPC_TOU_2A_0100_0000', 'NPC_TOU_2A_0100_NPCBUY_01', 0, new_script=False)
        add_delivery('NPC_TOU_2A_0400_0000', 'ITM_TRE_TOU_2A_0010', '1')

        # Throne 3 (Mother's Route): Habit
        slot_manager.create_slot_shop('get_habit', 'NPC_TOU_3A_0200_0000', 'NPC_TOU_3A_0200_NPCBUY_01', -1, new_script=False)
        add_delivery('EV_TRIGGER_MS_TOU_3A_0300', 'ITM_TRE_TOU_3A_0010', '1')

        # Throne 3: Keys
        mom_key_script = Manager.get_json('MS_TOU_3A_1000')
        mom_key_script.remove_command(9)
        assert slot_manager.has_slot('finish_chapter_throne_3a')
        dad_key_script = Manager.get_json('MS_TOU_3B_1000')
        dad_key_script.remove_command(11)
        assert slot_manager.has_slot('finish_chapter_throne_3b')
        add_delivery('EV_TRIGGER_MS_TOU_40_0410', 'ITM_TRE_TOU_3A_0030', '1', 'ITM_TRE_TOU_3B_0010', '1')

        # Osvald 4: Harvey Info
        slot_manager.create_slot_hear('hear_harveys_whereabouts', 'NPC_GAK_40_0100_0000', 'FC_INFOLINK_NPC_GAK_40_0100', 0, new_script=False)
        slot_manager.create_slot_hear('hear_harveys_eyewitness', 'NPC_GAK_40_0200_0000', 'FC_INFOLINK_NPC_GAK_40_0200', 0, new_script=False)
        slot_manager.create_slot_hear('hear_library_rumor', 'NPC_GAK_40_0300_0000', 'FC_INFOLINK_NPC_GAK_40_0300', 0, new_script=False)

        # Osvald 5: Black Crystals
        slot_manager.create_slot_shop('get_black_crystal_1', 'NPC_GAK_50_0100_0000', 'NPC_GAK_50_0100_NPCBUY_01', -1, new_script=False)
        slot_manager.create_slot_shop('get_black_crystal_2', 'NPC_GAK_50_0600_0010', 'NPC_GAK_50_0600_NPCBUY_01', -1, new_script=False)
        slot_manager.create_slot_shop('get_black_crystal_3', 'NPC_GAK_50_0700_0010', 'NPC_GAK_50_0700_NPCBUY_01', -1, new_script=False)
        slot_manager.create_slot_shop('get_black_crystal_4', 'NPC_GAK_50_0800_0010', 'NPC_GAK_50_0800_NPCBUY_01', 8, new_script=False)
        slot_manager.create_slot_shop('get_black_crystal_5', 'NPC_GAK_50_0900_0010', 'NPC_GAK_50_0900_NPCBUY_01', 8, new_script=False)
        add_delivery('EV_TRIGGER_MS_GAK_50_0600', 'ITM_TRE_GAK_50_0010', '5')

        # Partitio 2: Clockite
        assert slot_manager.has_slot('get_clockite')

        # Partitio 3: SOC
        assert slot_manager.has_slot('finish_soc_grand_terry')
        assert slot_manager.has_slot('finish_soc_manuscript')
        assert slot_manager.has_slot('finish_soc_gramophone')

        # COP TT 1: Folded Paper
        slot_manager.create_slot_shop('get_folded_paper', 'NPC_COP_ST2_0200_0000', 'NPC_COP_ST2_0200_NPCBUY_01', -1, new_script=False)

        # COP TT 2: Cloudy Mirror Fragment & Folded Paper needed
        add_delivery('EV_TRIGGER_MS_COP_ST2_0500', 'ITM_TRE_COP_ST1_0010', '1', 'ITM_TRE_COP_ST2_0010', '1')

        # COP AH 1: Horse Tail Hair
        slot_manager.create_slot_shop('get_horse_tail', 'NPC_COP_OK1_0300_0000', 'NPC_COP_OK1_0300_NPCBUY_01', -1, new_script=False)

        # COP AH 2: Wine Offering, Sacred Wood, Dancer's Mask
        slot_manager.create_slot_shop('get_wine_offering', 'NPC_COP_OK2_0500_N000', 'NPC_Twn_Dst_3_1_A_TALK_0510_NPCBUY_03', 0, new_script=False)
        slot_manager.create_slot_shop('get_sacred_wood', 'NPC_COP_OK2_0300_N000', 'NPC_Twn_Dst_3_1_A_TALK_0310_NPCBUY_04', 0, new_script=False)
        slot_manager.create_slot_shop('get_dancers_mask', 'NPC_COP_OK2_0600_D000', 'NPC_Twn_Dst_3_1_B_TALK_0610_NPCBUY_03', 0, new_script=False)

        # COP OP 1: Metalworking Tool, Mirror, Precision Lens
        slot_manager.create_slot_shop('get_metalworking_tool', 'NPC_COP_GS1_0100_0000', 'NPC_COP_GS1_0100_NPCBUY_01', 0, new_script=False)
        slot_manager.create_slot_shop('get_mirror', 'NPC_COP_GS1_0200_0000', 'NPC_COP_GS1_0200_NPCBUY_01', 0, new_script=False)
        slot_manager.create_slot_shop('get_precision_lens', 'NPC_COP_GS1_0300_0000', 'NPC_COP_GS1_0300_NPCBUY_01', 0, new_script=False)

    if EventsAndItems.include_galdera_items:
        slot_manager.create_slot_shop('get_tome_dispatches', 'NPC_SS_TMount21_0200_0200', 'NPC_SS_TM21_0200_0200_NPCBUY_01', -1, new_script=True)
        slot_manager.create_slot_shop('get_tome_great_wall', 'NPC_Fld_Snw_3_1_TALK_0600_D000', 'NPC_Fld_Snw_3_1_TALK_0600_NPCBUY_01', -1, new_script=True)
        slot_manager.create_slot_chest('get_tome_hell', 'Treasure_SS_TMnt21_0200_010')
        slot_manager.create_slot_hear('hear_decipher_unknown_languages', 'NPC_SS_TMount21_0400_0200', 'FC_INFOLINK_NPC_SS_TM21_0400_0200', -1, new_script=True)

    if EventsAndItems.include_rusty_weapons:
        slot_manager.create_slot_chest('get_rusty_polearm', 'Treasure_Twn_Fst_3_1_B_05')
        slot_manager.create_slot_chest('get_rusty_dagger', 'Treasure_Dng_Ocn_1_1_06')
        slot_manager.create_slot_chest('get_rusty_axe', 'Treasure_Dng_Dst_2_2_01')
        slot_manager.create_slot_chest('get_rusty_bow', 'Treasure_Dng_Isd_2_1_06')
        slot_manager.create_slot_chest('get_rusty_staff', 'Treasure_Dng_Mnt_2_2_07')

    if EventsAndItems.include_inventor_parts:
        slot_manager.create_slot_chest('get_rainbow_glass_bottle', 'Treasure_Twn_Sea_2_1_B_01')
        slot_manager.create_slot_chest('get_mythical_horn', 'Treasure_Twn_Isd_3_1_A_01')
        slot_manager.create_slot_shop('get_tin_toy', 'NPC_Twn_Fst_2_1_C_TALK_1700_N000', 'NPC_Twn_Fst_2_1_C_TALK_1700_NPCBUY_02', -1, new_script=True)
        slot_manager.create_slot_shop('get_scrap_metal', 'NPC_Twn_Cty_2_1_B_TALK_1200_D000', 'NPC_Twn_Cty_2_1_B_TALK_1200_NPCBUY_03', -1, new_script=True)
        slot_manager.create_slot_shop('get_ancient_cog', 'NPC_Twn_Sea_3_1_A_TALK_1500_N000', 'NPC_Twn_Sea_3_1_A_TALK_1500_NPCBUY_02', -1, new_script=True)
        slot_manager.create_slot_shop('get_ancient_cog', 'SHO_40_01_Twn_Sea_3_1_A_TALK_1500_N000', 'NPC_Twn_Sea_3_1_A_TALK_1500_NPCBUY_02', -1, new_script=True)
        slot_manager.create_slot_chest('get_natural_magnetite', 'Treasure_Dng_Wld_1_2_03')

    return slot_manager


def fill_event(key, start_flag, end_flag, script_name, event_type, *args, x=None):
    placement_data = Manager.get_table('PlacementData')
    placement = getattr(placement_data, key)

    if x is None:
        for x in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
            if getattr(placement, f'EventType_{x}') == '':
                break
        else:
            sys.exit('All events are full!?')

    if start_flag >= 0: setattr(placement, f'EventStartFlag_{x}', start_flag)
    if end_flag   >= 0: setattr(placement, f'EventEndFlag_{x}', end_flag)
    if script_name:     setattr(placement, f'EventLabel_{x}', script_name)
    setattr(placement, f'EventType_{x}', event_type)
    assert len(args) < 10
    for i, a in enumerate(args):
        setattr(placement, f'EventParam_{x}_{i+1}', a)


def add_delivery(key, *args, x='A'):
    fill_event(key, -1, -1, '', 'eDELIVERY_ITEM', *args, x=x)
