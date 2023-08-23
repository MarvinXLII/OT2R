from Assets import Data

class Testing:
    def __init__(self):
        self.enemyDB = Data.getInstance('EnemyDB')
        self.objectDB = Data.getInstance('ObjectData')
        self.shopDB = Data.getInstance('PurchaseItemTable')

    def run(self):
        for enemy in self.enemyDB.table:
            if enemy.key == 'ENE_BOS_DAN_C05_010':
                enemy.Param['HP'] = 2000 # Weird event stuff
            else:
                enemy.Param['HP'] = 20
            enemy.Param['HP'] = 999999
            enemy.Param['MP'] = 1
            enemy.Param['ATK'] = 1
            enemy.Param['MATK'] = 1
            enemy.Param['DEF'] = 999
            enemy.Param['MDEF'] = 999
            enemy.Param['ACC'] = 999
            enemy.Param['EVA'] = 1
            enemy.Param['AGI'] = 1
            enemy.Exp *= 1000
            enemy.JobPoint *= 100
            enemy.Money *= 1000

        # Chests and hidden items
        for i, obj in enumerate(self.objectDB.table):
            if obj.ObjectType <= 5:
                # Skip key items
                if obj.skipShuffling:
                    continue
                if obj.vanilla == '':
                    continue
                # Change everything else to money
                obj.IsMoney = True
                obj.HaveItemLabel = 'None'
                obj.HaveItemCnt = i + 1

        # NPC shops
        for i, shop in enumerate(self.shopDB.table):
            if shop.FCPrice:
                shop.FCPrice = i + 1
                # shop.FCPrice = 1
            # if shop.ProperSteal:
            #     shop.ProperSteal = -15

        
        # # INVENTOR testing
        abil = Data.getInstance('AbilityData').table
        abilSet = Data.getInstance('AbilitySetData').table
        # for s in abilSet:
        #     print(s.InventorTurn)
        #     s.InventorTurn = 99

        # # updateInv("WAR")

        # a = abilSet.ABI_SET_INV_010
        # b = abilSet.ABI_SET_WAR_010
        # for k in a.__dict__():
        #     if k == 'ID': continue
        #     if k == 'AbilitySetID': continue
        #     if k == 'MenuType': continue
        #     setattr(a, k, getattr(b, k))

        # a = abil.ABI_INV_010_01
        # b = abil.ABI_WAR_010_01

        # b.CostType = a.CostType
        # b.CostValue = 0

        
        ## TEST ALL ABILITIES FOR INVENTOR
        # def updateAbility(ability):
        #     try:
        #         a = getattr(abil, ability)
        #         print(ability, 'worked')
        #     except:
        #         return
        #     a.CostType = 'EABILITY_COST_TYPE::eINVENTOR'
        #     a.CostValue = 0

        # for aSet in abilSet:
        #     aSet.InventorTurn = 1
        #     aSet.MenuType = 'ECOMMAND_MENU_TYPE::eINVENTOR_ITEM'
        #     updateAbility(aSet.NoBoost)
        #     updateAbility(aSet.BoostLv1)
        #     updateAbility(aSet.BoostLv2)
        #     updateAbility(aSet.BoostLv3)

        def updateAbility(ability):
            print('updating ability', ability)
            a = getattr(abil, ability)
            a.CostType = 'EABILITY_COST_TYPE::eINVENTOR'
            a.CostValue = 0

        def updateHigherMagic(jobAbil):
            if jobAbil == 'None': return
            aSet = getattr(abilSet, jobAbil)
            aSet.MenuType = 'ECOMMAND_MENU_TYPE::eINVENTOR_ITEM'
            updateAbility(aSet.NoBoost)
            updateAbility(aSet.BoostLv1)
            updateAbility(aSet.BoostLv2)
            updateAbility(aSet.BoostLv3)

        def copyToInventor(invAbil, jobAbil):
            iSet = getattr(abilSet, invAbil)
            aSet = getattr(abilSet, jobAbil)
            for k in iSet.__dict__():
                if k == 'ID': continue
                if k == 'AbilitySetID': continue
                if k == 'MenuType': continue
                if k == 'InventorTurn': continue
                setattr(iSet, k, getattr(aSet, k))
            iSet.InventorTurn = 1
            iSet.RestrictWeaponLabel = 'None'
            updateAbility(iSet.NoBoost)
            updateAbility(iSet.BoostLv1)
            updateAbility(iSet.BoostLv2)
            updateAbility(iSet.BoostLv3)
            updateHigherMagic(aSet.SuperMagicLabel)
            updateHigherMagic(aSet.HyperMagicLabel)

        c = 'WIZ'
        copyToInventor('ABI_SET_INV_010', f'ABI_SET_{c}_010')
        copyToInventor('ABI_SET_INV_020', f'ABI_SET_{c}_020')
        copyToInventor('ABI_SET_INV_030', f'ABI_SET_{c}_030')
        copyToInventor('ABI_SET_INV_040', f'ABI_SET_{c}_040')
        copyToInventor('ABI_SET_INV_050', f'ABI_SET_{c}_050')
        copyToInventor('ABI_SET_INV_060', f'ABI_SET_{c}_060')
        copyToInventor('ABI_SET_INV_070', f'ABI_SET_{c}_070')
        # copyToInventor('ABI_SET_INV_080', f'ABI_SET_{c}_080')  ### THIS SLOT DOESN'T WORK
        copyToInventor('ABI_SET_INV_010', f'ABI_SET_{c}_080')
        # copyToInventor('ABI_SET_INV_020', f'ABI_SET_{c}_090')
        # copyToInventor('ABI_SET_INV_030', f'ABI_SET_{c}_100')

        # Allow all PCs to use all weapons
        jobs = Data.getInstance('JobData').table
        for j in jobs:
            j.ProperEquipment[:6] = [True]*6
