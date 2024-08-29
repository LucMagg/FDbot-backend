from typing import Literal

ColorType = Literal['Red','Green','Blue','Light','Dark']
ClassType = Literal['Archer','Assassin','Barbarian','Bard','Druid','Elementalist','Guardian','Healer','Hunter','Javelineer','Knight','Mage','Monk','Paladin','Pirate','Princess','Ranger','Rogue','Warlock','Warrior','Witch']
SpeciesType = Literal['Beastfolk','Dragonborn','Dwarf','Elf','Human','Orc']
TypeType = Literal['Melee','Ranged','Melee/Ranged','Magic']
PatternType = Literal['Cross','Star','Star/Cross']
AscendType = Literal['A0','A1','A2','A3']
TalentPositionType = Literal['', 'base','silver','gold','full',
                             'base 1','base 2','base 3','base 4','base 5','base 6','ascend 1','ascend 2','ascend 3',
                             'merge 1','merge 2','merge 3','merge 4','merge 5','merge 6','merge 7','merge 8','merge 9','merge 10']