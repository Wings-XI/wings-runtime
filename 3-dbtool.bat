@echo off
powershell -command "&{(get-host).ui.rawui.windowsize=@{width=120;height=35};}"
set gitPath=../git/wings

REM cd "./wings/tools"
REM py -3 dbtool.py update

set combined=combined.sql
REM del /q combined.sql

Call :append "abilities.sql"
Call :append "abilities_charges.sql"
Call :append "augments.sql"
Call :append "automaton_spells.sql"
Call :append "bcnm_battlefield.sql"
Call :append "bcnm_treasure_chests.sql"
Call :append "blue_spell_list.sql"
Call :append "blue_spell_mods.sql"
Call :append "blue_traits.sql"
Call :append "cheat_types.sql"
Call :append "despoil_effects.sql"
Call :append "exp_base.sql"
Call :append "exp_table.sql"
Call :append "fishing_area.sql"
Call :append "fishing_catch.sql"
Call :append "fishing_fish.sql"
Call :append "fishing_group.sql"
Call :append "fishing_lure.sql"
Call :append "fishing_lure_affinity.sql"
timeout /t 5 /nobreak >nul
Call :append "fishing_mob.sql"
Call :append "fishing_rod.sql"
Call :append "fishing_zone.sql"
Call :append "gardening_results.sql"
Call :append "guild_item_points.sql"
Call :append "guild_shops.sql"
Call :append "guilds.sql"
Call :append "instance_entities.sql"
Call :append "instance_list.sql"
Call :append "item_basic.sql"
timeout /t 5 /nobreak >nul
Call :append "item_equipment.sql"
Call :append "item_furnishing.sql"
Call :append "item_latents.sql"
Call :append "item_mods.sql"
Call :append "item_mods_pet.sql"
Call :append "item_puppet.sql"
Call :append "item_usable.sql"
Call :append "item_weapon.sql"
Call :append "job_points.sql"
Call :append "merits.sql"
Call :append "mob_droplist.sql"
timeout /t 5 /nobreak >nul
Call :append "mob_family_mods.sql"
Call :append "mob_family_system.sql"
Call :append "mob_groups.sql"
Call :append "mob_level_exceptions.sql"
Call :append "mob_pets.sql"
Call :append "mob_pool_mods.sql"
Call :append "mob_pools.sql"
Call :append "mob_skill_lists.sql"
Call :append "mob_skills.sql"
Call :append "mob_spawn_mods.sql"
Call :append "mob_spawn_points.sql"
Call :append "mob_spell_lists.sql"
Call :append "nm_spawn_points.sql"
Call :append "npc_list.sql"
Call :append "pet_list.sql"
Call :append "pet_name.sql"
timeout /t 5 /nobreak >nul
Call :append "skill_caps.sql"
Call :append "skill_ranks.sql"
Call :append "skillchain_damage_modifiers.sql"
Call :append "spell_list.sql"
Call :append "status_effects.sql"
Call :append "synth_recipes.sql"
Call :append "traits.sql"
Call :append "transport.sql"
Call :append "water_points.sql"
Call :append "weapon_skills.sql"
Call :append "zone_weather.sql"
Call :append "zonelines.sql"

echo "importing static sql data complete"

powershell -command "&{while((get-process mysql -erroraction silentlycontinue).count -gt 0){'*** Please wait while mysql imports finish' ; (Get-WmiObject Win32_Process -Filter {name = 'cmd.exe'} | ? commandline -like *sql-wings*).commandline; sleep 6}}"
timeout /t 30

EXIT /B %ERRORLEVEL% 
:append
echo %~1 import
start "%~1" /SEPARATE /MIN import.bat wings\sql-wings\%~1
EXIT /B 0