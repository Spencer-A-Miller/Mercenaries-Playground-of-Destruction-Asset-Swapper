"""
Copyright (c) 2024 Baldy

Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the "Software"), to deal 
in the Software without restriction, including without limitation the rights 
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in 
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.

See More about the MIT Open Source License: https://opensource.org/license/MIT

DEPENDENCIES:
    - Legal iso copy of Mercenaries
    - Python: https://www.python.org/downloads/
    - Apache 3: https://www.romhacking.net/utilities/584/
    
HOW TO USE:
    - Extract ASSETS.DSK from your Mercenaries ISO with Apache 3
    - Backup your ASSET.DSK file in another directory
    - Install latest python release (If you don't have it already)
    - Open your Command Prompt(Windows) and change to the directory (cd) where 
        this file is being stored
    - From the command prompt type: "python assetSwap_PRE_ALPHA.py"
    - A file explorer will appear. Use this to select your ASSET.DSK
        file and hit "open"
    - Make your replacements
    - When finished, use apache 3 to replace the ASSET.DSK file
        in your Mercs ISO. ("Replace Selected File in Apache 3")
    - Browse and select the ASSET.DSK file you modified
    - Uncheck Update TOC
    - Check Ignore File Size Difference
    - "Replace File"
    - Your Modded ISO is now ready.
    - Open PCSX2 > CDVD > ISO Selector > Browse > Your modded ISO
    - Boot ISO
    
CHANGE-LOG:
    5/11/2024
        - Ammo templates Supported
        - Weapon templates Supported
        
    5/14/2024
        - Ammo Randomizer Support
        - Weapon Randomizer Support
        
    6/30/2024
        - Human Randomizer support (limited - See known bugs section)
        - All Randomizers now have settings menu for checking boxes per item
        
    7/27/2024
        - Changed logic in human swapper. Humans name templates don't
          follow the same naming conventions as ammo and weapons so as a result
          the template must be provided in this script by the programmer.
          This is also applies to vehicles.
        
KNOWN BUGS:
    7/8/2024
    
    All Randomizers:
        - Some/many swaps shown in the output console are not accurate.
    
    Human Randomizer:
        - Some humans do not spawn in level after swap
          This bug can halt game progression when HQ bouncers 
          do not spawn as expected. This likely extends to any 
          human npc critical to mission scripts.
          
OBSERVATIONS:
    
    The following are things I noticed in weapon template swapping.
    These were noticed when playtesting the randomizer
    
    2) Some weapons in vehicles share the same weapon templates.
    For example, the apache rocket template is used on the apache and
    WZ-9. So changing this weapon template leads to changes in other
    weapons unintuitively. Please keep this in mind.
    
    3) Some swaps with result in weapons no longer functioning
    
    4) Some weapon swaps may appear to be swapped, but are not in reality.
    This could be due to obervation 2
    
    
    
While not finished, I hope you find some enjoyment in this script. Thank you
for reading and have fun with this asset swapper. Feel free to modify, 
record gameplay, and share. Best of lusk to you <3

"""

import re
import sys
import struct
import random
import tkinter as tk
import tkinter.messagebox
from pathlib import PurePath
from tkinter import ttk, Menu
from tkinter import filedialog

ZERO = b'\x00'
UNIX_NEW_LINE = b'\x0A'
TEMPLATE_AMM = b'template_amm_'
TEMPLATE_WEP = b'template_wep_'

def ask_for_assetDSK_file() -> None:
    root = tk.Tk()
    
    # Hide the main window
    root.withdraw()
    
    # Raise the file dialog prompting the user to select 'ASSETS.DSK'
    assetDSKFilePath = filedialog.askopenfilename(title="Select your ASSETS.DSK file",
                                           filetypes=[("DSK files", "*.DSK")])
   
    print(f"assetDSKFilePath = {assetDSKFilePath}")
    return assetDSKFilePath

def generate_template_amm_dict(filePath) -> dict:
    
    # Initialize an empty dictionary to store the variables and their addresses
    templateAmmoDict = {}
    
    with open(filePath, 'rb') as assetFile:
        
        # Read the file byte by byte
        content = assetFile.read()

        # Find all occurrences of "template_amm_"
        start = 0
        
        while start < len(content):
            start = content.find(TEMPLATE_AMM, start)
            if start == -1:  # No more occurrences
                break

            # Extract the variable name (ends when we hit a space)
            end = content.find(ZERO, start)
            
            if end == -1:  # No space found, so we take the rest of the string
                end = len(content)
            templateAmmoInstance = content[start:end]

            # Look back 8 bytes to find the address
            address_start = max(0, start - 8)
            address = content[address_start:start - 4]

            # Convert the address to hexadecimal and format it with spaces
            address = ' '.join(f'{byte:02x}' for byte in address)

            # Add the variable and its address to the dictionary
            templateAmmoDict[templateAmmoInstance] = address

            # Move the start position forward to continue searching
            start = end + 1

    return templateAmmoDict

def generate_template_wep_dict(filePath) -> dict:
    
    # Initialize an empty dictionary to store the variables and their addresses
    templateWepDict = {}
    
    with open(filePath, 'rb') as assetFile:
        
        # Read the file byte by byte
        content = assetFile.read()

        # Find all occurrences of "template_amm_"
        start = 0
        
        while start < len(content):
            start = content.find(TEMPLATE_WEP, start)
            if start == -1:  # No more occurrences
                break

            # Extract the variable name (ends when we hit a space)
            end = content.find(ZERO, start)
            
            if end == -1:  # No space found, so we take the rest of the string
                end = len(content)
            templateWepInstance = content[start:end]

            # Look back 8 bytes to find the address
            address_start = max(0, start - 8)
            address = content[address_start:start - 4]

            # Convert the address to hexadecimal and format it with spaces
            address = ' '.join(f'{byte:02x}' for byte in address)

            # Add the variable and its address to the dictionary
            templateWepDict[templateWepInstance] = address

            # Move the start position forward to continue searching
            start = end + 1

    return templateWepDict

def generate_template_human_dict(filePath) -> dict:
    
    # Initialize an empty dictionary to store the variables and their addresses
    templateHumanDict = {}
    
    with open(filePath, 'rb') as assetFile:
        
        # Read the file byte by byte
        content = assetFile.read()

        template_human_list = [b'template_allies_starter',
                               b'template_allies_driver',
                               b'template_allies_gunner',
                               b'template_allies_soldier',
                               b'template_allies_heavy',
                               b'template_allies_officer',
                               b'template_allies_pilot',
                               b'template_allies_bouncer',
                               b'template_allies_boss',
                               b'template_sk_starter',
                               b'template_sk_driver',
                               b'template_sk_gunner',
                               b'template_sk_soldier',
                               b'template_sk_elite',
                               b'template_sk_officer',
                               b'template_china_spy',
                               b'template_sk_bouncer',
                               b'template_mafia_starter',
                               b'template_mafia_driver',
                               b'template_mafia_gunner',
                               b'template_mafia_soldier',
                               b'template_mafia,bouncer',
                               b'template_china_starter',
                               b'template_china_driver',
                               b'template_china_gunner',
                               b'template_china_soldier',
                               b'template_china_heavy',
                               b'template_china_officer',
                               b'template_china_bouncer',
                               b'template_nk_soldier_easy',
                               b'template_nk_driver',
                               b'template_nk_gunner',
                               b'template_nk_soldier',
                               b'template_nk_heavy',
                               b'template_nk_elite',
                               b'template_nk_officer',
                               b'template_nk_clubace',
                               b'template_nk_diamondace',
                               b'template_nk_heartncard',
                               b'template_nk_heartfacecard',
                               b'template_nk_spadesace',
                               b'template_nk_spadesfacecard',
                               b'template_civ_doctor',
                               b'template_civ_cameraman',
                               b'template_civ_civilian01',
                               b'template_civ_civilian02',
                               b'template_civ_civilian03',
                               b'template_civ_civilian04',
                               b'template_civ_worker',
                               b'template_civ_prisoner']
        
        human_instance_list = [b'allies_hum_officer',
                               b'allies_hum_heavy',
                               b'allies_hum_soldier',
                               b'china_hum_officer',
                               b'china_hum_heavy',
                               b'china_hum_soldier',
                               b'mafia_hum_officer',
                               b'mafia_hum_soldier',
                               b'nk_hum_elite',
                               b'nk_hum_heavy',
                               b'nk_hum_officer',
                               b'nk_hum_soldier',
                               b'sk_hum_elite',
                               b'sk_hum_officer',
                               b'sk_hum_sentry',
                               b'sk_hum_soldier']
        
                               #b'deck_diamonds04',
        
        for template_human in template_human_list:
            start = 0
            while start < len(content):
                start = content.find(template_human, start)
                if start == -1:  # No more occurrences
                    break
    
                # Extract the variable name (matches exactly with an entry in template_human_list)
                end = start + len(template_human)
                templateHumanInstance = content[start:end]
                
                # Look back 8 bytes to find the address
                address_start = max(0, start - 8)
                address = content[address_start:start - 4]
    
                # Convert the address to hexadecimal and format it with spaces
                address = ' '.join(f'{byte:02x}' for byte in address)
    
                # Add the variable and its address to the dictionary
                templateHumanDict[templateHumanInstance] = address
    
                # Move the start position forward to continue searching
                start = end + 1

    return templateHumanDict

# NOT YET IMPLEMENTED
def generate_template_veh_dict(filePath):
    
    # Initialize an empty dictionary to store the variables and their addresses
    templateVehDict = {}
    
    with open(filePath, 'rb') as assetFile:
        
        # Read the file byte by byte
        content = assetFile.read()

        # THIS LIST DOES NOT FILTER AS EXPECTED

        # template_veh_list = [b'template_allies_chinook',
        #                       b'template_allies_blackhawk',
        #                       b'template_allies_apache',
        #                       b'template_allies_bradley',
        #                       b'template_allies_cargotruck',
        #                       b'template_allies_avenger',
        #                       b'template_allies_humvee',
        #                       b'template_allies_lavstryker',
        #                       b'template_allies_abrams',
        #                       b'template_sk_pavelow',
        #                       b'template_sk_blackhawk',
        #                       b'template_sk_comanche',
        #                       b'template_sk_humveeat',
        #                       b'template_sk_humveemg',
        #                       b'template_sk_cargotruck',
        #                       b'template_sk_kafv',
        #                       b'template_sk_kafv_empty',
        #                       b'template_mafia_cargotruck',
        #                       b'template_mafia_NKLittleBird',
        #                       b'template_mafia_h2',
        #                       b'template_mafia_technicalmg',
        #                       b'template_mafia_technicalat',
        #                       b'template_mafia_cargocopter',
        #                       b'template_mafia_blackhawk',
        #                       b'template_mafia_littlebird',
        #                       b'template_mafia_ka50',
        #                       b'template_china_jeep',
        #                       b'template_china_mi17',
        #                       b'template_china_wz9',
        #                       b'template_china_s70blackhawk',
        #                       b'template_china_tunguska',
        #                       b'template_china_type80',
        #                       b'template_china_type96',
        #                       b'template_china_apc',
        #                       b'template_nk_cargotruck',
        #                       b'template_nk_mgnest',
        #                       b'template_nk_controltruck',
        #                       b'template_nk_type89',
        #                       b'template_nk_brdm',
        #                       b'template_nk_zsu-57aa',
        #                       b'template_nk_type54',
        #                       b'template_nk_type62tank'
        #                       b'template_nk_mi17',
        #                       b'template_nk_jeepmgun_gunneronly',
        #                       b'template_nk_frog7',
        #                       b'template_nk_sa8sam',
        #                       b'template_nk_btr60',
        #                       b'template_nk_jeepmgun',
        #                       b'template_nk_bmp-1apc',
        #                       b'template_nk_m1978',
        #                       b'template_nk_oh6littlebird',
        #                       b'template_nk_mi2hoplite',
        #                       b'template_nk_transport',
        #                       b'template_nk_mi35hind',
        #                       b'template_civ_baggagetruck',
        #                       b'template_civ_markettruck',
        #                       b'template_civ_forklift',
        #                       b'template_civ_cargotruck',
        #                       b'template_civ_presstruck',                          
        #                       b'template_civ_bus',
        #                       b'template_civ_unaidtruck',   
        #                       b'template_civ_lada124',
        #                       b'template_civ_50skgbcar']
        
        template_veh_list =[b'allies_veh_apache',
                      		b'allies_veh_avenger',
                      		b'allies_veh_blackhawk',
                      		b'allies_veh_cargotruck',
                      		b'allies_veh_humvee',
                      		b'allies_veh_lavstryker',
                      		b'allies_veh_m1a2',
                      		b'allies_veh_m3bradley',
                      		b'china_veh_bj2020',
                      		b'china_veh_cargotruck',
                      		b'china_veh_s70blackhawk',
                      		b'china_veh_tunguska',
                      		b'china_veh_type66',
                      		b'china_veh_type80',
                      		b'china_veh_type89tow',
                      		b'china_veh_type96',
                      		b'china_veh_wz9',
                      		b'civ_veh_57kgbcar',
                      		b'civ_veh_80civic',
                      		b'civ_veh_baggagetruck',
                      		b'civ_veh_bus',
                      		b'civ_veh_cargotruck',
                      		b'civ_veh_daewoo',
                      		b'civ_veh_generictruck',
                      		b'civ_veh_lada124',
                      		b'civ_veh_markettruck',
                      		b'civ_veh_presstruck',
                      		b'civ_veh_sportscar',
                      		b'civ_veh_suv',
                      		b'civ_veh_unaidtruck' ,
                      		b'global_veh_emplacedgl',
                      		b'global_veh_emplacedmg',
                      		b'global_veh_emplacedrr',
                      		b'mafia_veh_h2',
                      		b'mafia_veh_ka50',
                      		b'mafia_veh_littlebird',
                      		b'mafia_veh_mi26halo',
                      		b'mafia_veh_mi28havoc',
                      		b'mafia_veh_technicalAT',
                      		b'mafia_veh_technicalGL',
                      		b'mafia_veh_technicalMG',
                      		b'nk_veh_bmp-1apc',
                      		b'nk_veh_brdm-2',
                      		b'nk_veh_btr60',
                      		b'nk_veh_cargotruck',
                      		b'nk_veh_controltruck',
                      		b'nk_veh_frog7',
                      		b'nk_veh_jeepmgun',
                      		b'nk_veh_m1978artillery',
                      		b'nk_veh_mi17hip',
                      		b'nk_veh_mi2hoplite',
                      		b'nk_veh_mi35hind',
                      		b'nk_veh_oh6littlebird',
                      		b'nk_veh_sa8sam',
                      		b'nk_veh_supergun',
                      		b'nk_veh_testgun',
                      		b'nk_veh_transport',
                      		b'nk_veh_type54',
                      		b'nk_veh_type62tank' ,
                      		b'nk_veh_type66',
                      		b'nk_veh_zsu-57aa',
                      		b'sk_veh_blackhawk',
                      		b'sk_veh_cargotruck',
                      		b'sk_veh_comanche',
                      		b'sk_veh_humveeat',
                      		b'sk_veh_humveemg' 
                      		b'sk_veh_KAFV',
                      		b'sk_veh_KIFV-EW']
        
        for template_veh in template_veh_list:
            start = 0
            while start < len(content):
                start = content.find(template_veh, start)
                if start == -1:  # No more occurrences
                    break
    
                # Extract the variable name (matches exactly with an entry in template_veh_list)
                end = start + len(template_veh)
                templateVehInstance = content[start:end]
                
                # Look back 8 bytes to find the address
                address_start = max(0, start - 8)
                address = content[address_start:start - 4]
    
                # Convert the address to hexadecimal and format it with spaces
                address = ' '.join(f'{byte:02x}' for byte in address)
    
                # Add the variable and its address to the dictionary
                templateVehDict[templateVehInstance] = address
    
                # Move the start position forward to continue searching
                start = end + 1

    return templateVehDict

def replace_addresses(assetDSKFilePath, template_dict, var1, var2):
    
    if not tkinter.messagebox.askokcancel("Misclick Protection", "Please Confirm your Selection"):
        return
    
    # Open the file in binary read-write mode
    with open(assetDSKFilePath, 'r+b') as assetFile:
        
        # Read the file byte by byte
        content = assetFile.read()

        for key, value in template_dict.items():
            print(f"Key: {key}, Value: {value}")

        # Find every instance of the address of var1 and replace it with the address of var2
        
        #print(type(var1))
        #print(type(var2))
        
        if not isinstance(var1, bytes):
            var1_bytes = var1.encode('latin-1')
        else:
            var1_bytes = var1
        if not isinstance(var2, bytes):
            var2_bytes = var2.encode('latin-1')
        else:
            var2_bytes = var2
            
        print(type(var1_bytes))
        print(type(var2_bytes))
        
        content = content.replace(bytes.fromhex(template_dict[var1_bytes]),
                                  bytes.fromhex(template_dict[var2_bytes]))

        # Go back to the start of the file
        assetFile.seek(0)

        # Write the modified content back to the file
        assetFile.write(content)

def randomize_addresses(assetDSKFilePath, template_dict):
    # Show a warning message
    if not tkinter.messagebox.askokcancel("Misclick Protection", "Are you sure you want to randomize?"):
        return

    for key, value in template_dict.items():
        print(f"Key: {key}, Value: {value}")

    
    # Get a list of all keys from the template_dict arguement
    original_keys = list(template_dict.keys())
    
    shuffled_keys = original_keys.copy()
    
    # Open the file in binary read-write mode
    with open(assetDSKFilePath, 'r+b') as assetFile:
    
        # Read the file byte by byte
        content = assetFile.read()
        random.shuffle(shuffled_keys)
         
        # For each key in the dictionary
        for index, key in enumerate(original_keys):
            # Select a random key to replace
            #random_key = random.choice(keys)
            
            # Call the replace_addresses function
            #replace_addresses(assetDSKFilePath, template_dict, key, shuffled_keys[index], confirmFlag)
            
            var1 = key
            var2 = shuffled_keys[index]
            
            while (var1 == var2):
                random.shuffle(shuffled_keys)
                var1 = key
                var2 = shuffled_keys[index]
                
            print(f"   >randomize_addresses (shuffled): original_key = {key} => {shuffled_keys[index]}")
            print(f"var1 = {var1}")
            print(f"var2 = {var2}\n")
            
            if not isinstance(var1, bytes):
                var1_bytes = var1.encode('latin-1')
            else:
                var1_bytes = var1
                
            if not isinstance(var2, bytes):
                var2_bytes = var2.encode('latin-1')
            else:
                var2_bytes = var2
            
            content = content.replace(bytes.fromhex(template_dict[var1_bytes]),
                                      bytes.fromhex(template_dict[var2_bytes]))
            
            assetFile.seek(0)
    
            # Write the modified content back to the file
            assetFile.write(content)
    
    print("DONE")
    #sys.exit("DONE")

# Driver Code 
assetDSKFilePath = ask_for_assetDSK_file()
template_amm_dict = generate_template_amm_dict(assetDSKFilePath)
template_wep_dict = generate_template_wep_dict(assetDSKFilePath)
template_human_dict = generate_template_human_dict(assetDSKFilePath)
template_veh_dict = generate_template_veh_dict(assetDSKFilePath)

for ammInstance, address in template_amm_dict.items():
    print(f'"{ammInstance}": "{address}"')
print('\n')

for wepInstance, address in template_wep_dict.items():
    print(f'"{wepInstance}": "{address}"')
print('\n')

for humInstance, address in template_human_dict.items():
    print(f'"{humInstance}": "{address}"')
print('\n')

for vehInstance, address in template_veh_dict.items():
    print(f'"{vehInstance}": "{address}"')
print('\n')
    
    
# tkinter GUI

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Mercenaries: Playground of Destruction Asset Replacer PRE-ALPHA")

        # Create a frame for the buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side="top", fill="x")

        # Create buttons for each page
        button1 = tk.Button(button_frame, text="Ammo",
                            command=lambda: self.show_frame(PageOne))
        button1.pack(side="left")
        button2 = tk.Button(button_frame, text="Weapons",
                            command=lambda: self.show_frame(PageTwo))
        button2.pack(side="left")
        button3 = tk.Button(button_frame, text="Humans",
                            command=lambda: self.show_frame(PageThree))
        button3.pack(side="left")
        button4 = tk.Button(button_frame, text="Vehicles",
                             command=lambda: self.show_frame(PageFour))
        button4.pack(side="left")

        # Create a container for the pages
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initialize frames
        self.frames = {}

        for F in (PageOne, PageTwo, PageThree, PageFour): # , PageFour
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Credit for a Merc
        credits_label = tk.Label(self, text="Original Author: Baldy\nMade Possible by: Noot")
        credits_label.pack(side="bottom")

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Create the "Single Replacement" label
        single_replacement_label = tk.Label(self, text="Single Replacement", padx=10, pady=10)
        single_replacement_label.grid(column=1, row=0, columnspan=2)

        # Create labels
        label1 = tk.Label(self, text="Selection", padx=10, pady=10)
        label1.grid(column=1, row=1)
        label2 = tk.Label(self, text="Replacement", padx=10, pady=10)
        label2.grid(column=2, row=1)

        # Create the dropdown menus
        dropdown1 = ttk.Combobox(self, values=list(template_amm_dict.keys()), width=35)
        dropdown1.grid(column=1, row=2, padx=10, pady=10)
        dropdown2 = ttk.Combobox(self, values=list(template_amm_dict.keys()), width=35)
        dropdown2.grid(column=2, row=2, padx=10, pady=10)

        # Create the button and send the user's input to the Replacing function
        button = tk.Button(self, text="Replace", 
                           command=lambda: replace_addresses(assetDSKFilePath,
                                                             template_amm_dict,
                                                             dropdown1.get(),
                                                             dropdown2.get()))
        button.grid(column=1, row=3, columnspan=2, padx=10, pady=10)

        # Create a label for the checkbox section
        checkbox_label = tk.Label(self, text="Randomization Settings", padx=10, pady=10)
        checkbox_label.grid(column=1, row=4, columnspan=2)

        # Create a dictionary to store the checkboxes
        self.checkboxes_dict = {}

        # Create a checkbox for each entry in the dictionary
        for i, key in enumerate(template_amm_dict.keys()):
            checkbox_val = tk.BooleanVar()
            checkbox_obj = tk.Checkbutton(self, text=key.decode('latin-1'), variable=checkbox_val, state='normal',
                                          command=lambda checkbox_val=checkbox_val: self.checkbox_clicked(checkbox_obj,checkbox_val))
            checkbox_obj.grid(column=i%4, row=i//4+5, sticky='w')
            self.checkboxes_dict[key] = (checkbox_obj, checkbox_val)  # Store both the Checkbutton and the BooleanVar

        # Create 'Enable All' and 'Disable All' buttons
        enable_all_button = tk.Button(self, text="Enable All", 
                                      command=self.enable_all_checkboxes)
        enable_all_button.grid(column=1, row=6+len(self.checkboxes_dict)//4, padx=10, pady=10)

        disable_all_button = tk.Button(self, text="Disable All", 
                                       command=self.disable_all_checkboxes)
        disable_all_button.grid(column=2, row=6+len(self.checkboxes_dict)//4, padx=10, pady=10)

        randomize_button = tk.Button(self, text="Randomize Ammo", 
                             command=self.randomize_ammo) # Too Damn complicated
        randomize_button.grid(column=1, row=7+len(self.checkboxes_dict)//4, columnspan=2, padx=10, pady=10)

    def checkbox_clicked(self, checkbox_obj, checkbox_val):
        # This function is called when a checkbox is clicked
        if not checkbox_val.get():
            print("Checkbox was checked")
            checkbox_obj.select()
            checkbox_val.set(True)
        else:
            checkbox_obj.deselect()
            checkbox_val.set(False)
            print("Checkbox was unchecked")  

    def enable_all_checkboxes(self):
        # Enable all checkboxes
        for checkbox_obj, var in self.checkboxes_dict.values():
            checkbox_obj.select()
            var.set(True)

    def disable_all_checkboxes(self):
        # Disable all checkboxes
        for checkbox_obj, var in self.checkboxes_dict.values():
            checkbox_obj.deselect()
            var.set(False)
        
    def randomize_ammo(self):
        # Prepare the dictionary argument for the randomize_addresses function
        selected_items_dict = {}
        for key, (checkbox_obj, var) in self.checkboxes_dict.items():
            if var.get():
                selected_items_dict[key] = template_amm_dict[key]
                
        for ammInstance, address in selected_items_dict.items():
            print(f'"{ammInstance}": "{address}"')

                #print(f"selected_items.items() = {selected_items.items()}")
                
        # Call the randomize_addresses function
        randomize_addresses(assetDSKFilePath, selected_items_dict)
        
class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Create the "Single Replacement" label
        single_replacement_label = tk.Label(self, text="Single Replacement", padx=10, pady=10)
        single_replacement_label.grid(column=1, row=0, columnspan=2)

        # Create labels
        label1 = tk.Label(self, text="Selection", padx=10, pady=10)
        label1.grid(column=1, row=1)
        label2 = tk.Label(self, text="Replacement", padx=10, pady=10)
        label2.grid(column=2, row=1)

        # Create the dropdown menus
        dropdown1 = ttk.Combobox(self, values=list(template_wep_dict.keys()), width=35)
        dropdown1.grid(column=1, row=2, padx=10, pady=10)
        dropdown2 = ttk.Combobox(self, values=list(template_wep_dict.keys()), width=35)
        dropdown2.grid(column=2, row=2, padx=10, pady=10)

        # Create the button and send the user's input to the Replacing function
        button = tk.Button(self, text="Replace", 
                           command=lambda: replace_addresses(assetDSKFilePath,
                                                             template_wep_dict,
                                                             dropdown1.get(),
                                                             dropdown2.get()))
        button.grid(column=1, row=3, columnspan=2, padx=10, pady=10)

        # Create a label for the checkbox section
        checkbox_label = tk.Label(self, text="Randomization Settings", padx=10, pady=10)
        checkbox_label.grid(column=1, row=4, columnspan=2)

        # Create a dictionary to store the checkboxes
        self.checkboxes_dict = {}

        # Create a checkbox for each entry in the dictionary
        for i, key in enumerate(template_wep_dict.keys()):
            checkbox_val = tk.BooleanVar()
            checkbox_obj = tk.Checkbutton(self, text=key.decode('latin-1'), variable=checkbox_val, state='normal',
                                          command=lambda checkbox_val=checkbox_val: self.checkbox_clicked(checkbox_obj,checkbox_val))
            checkbox_obj.grid(column=i%4, row=i//4+5, sticky='w')
            self.checkboxes_dict[key] = (checkbox_obj, checkbox_val)  # Store both the Checkbutton and the BooleanVar

        # Create 'Enable All' and 'Disable All' buttons
        enable_all_button = tk.Button(self, text="Enable All", 
                                      command=self.enable_all_checkboxes)
        enable_all_button.grid(column=1, row=6+len(self.checkboxes_dict)//4, padx=10, pady=10)

        disable_all_button = tk.Button(self, text="Disable All", 
                                       command=self.disable_all_checkboxes)
        disable_all_button.grid(column=2, row=6+len(self.checkboxes_dict)//4, padx=10, pady=10)

        randomize_button = tk.Button(self, text="Randomize Weapons", 
                             command=self.randomize_weapons)
        randomize_button.grid(column=1, row=7+len(self.checkboxes_dict)//4, columnspan=2, padx=10, pady=10)

    def checkbox_clicked(self, checkbox_obj, checkbox_val):
        # This function is called when a checkbox is clicked
        if not checkbox_val.get():
            print("Checkbox was checked")
            checkbox_obj.select()
            checkbox_val.set(True)
        else:
            checkbox_obj.deselect()
            checkbox_val.set(False)
            print("Checkbox was unchecked")  

    def enable_all_checkboxes(self):
        # Enable all checkboxes
        for checkbox_obj, var in self.checkboxes_dict.values():
            checkbox_obj.select()
            var.set(True)

    def disable_all_checkboxes(self):
        # Disable all checkboxes
        for checkbox_obj, var in self.checkboxes_dict.values():
            checkbox_obj.deselect()
            var.set(False)
        
    def randomize_weapons(self):
        # Prepare the dictionary argument for the randomize_addresses function
        selected_items_dict = {}
        for key, (checkbox_obj, var) in self.checkboxes_dict.items():
            if var.get():
                selected_items_dict[key] = template_wep_dict[key]
                
        for wepInstance, address in selected_items_dict.items():
            print(f'"{wepInstance}": "{address}"')

        # Call the randomize_addresses function
        randomize_addresses(assetDSKFilePath, selected_items_dict)

class PageThree(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Create the "Single Replacement" label
        single_replacement_label = tk.Label(self, text="Single Replacement", padx=10, pady=10)
        single_replacement_label.grid(column=1, row=0, columnspan=2)

        # Create labels
        label1 = tk.Label(self, text="Selection", padx=10, pady=10)
        label1.grid(column=1, row=1)
        label2 = tk.Label(self, text="Replacement", padx=10, pady=10)
        label2.grid(column=2, row=1)

        # Create the dropdown menus
        dropdown1 = ttk.Combobox(self, values=list(template_human_dict.keys()), width=35)
        dropdown1.grid(column=1, row=2, padx=10, pady=10)
        dropdown2 = ttk.Combobox(self, values=list(template_human_dict.keys()), width=35)
        dropdown2.grid(column=2, row=2, padx=10, pady=10)

        # Create the button and send the user's input to the Replacing function
        button = tk.Button(self, text="Replace", 
                           command=lambda: replace_addresses(assetDSKFilePath,
                                                             template_human_dict,
                                                             dropdown1.get(),
                                                             dropdown2.get()))
        button.grid(column=1, row=3, columnspan=2, padx=10, pady=10)

        # Create a label for the checkbox section
        checkbox_label = tk.Label(self, text="Randomization Settings", padx=10, pady=10)
        checkbox_label.grid(column=1, row=4, columnspan=2)

        # Create a dictionary to store the checkboxes
        self.checkboxes_dict = {}

        # Create a checkbox for each entry in the dictionary
        for i, key in enumerate(template_human_dict.keys()):
            checkbox_val = tk.BooleanVar()
            checkbox_obj = tk.Checkbutton(self, text=key.decode('latin-1'), variable=checkbox_val, state='normal',
                                          command=lambda checkbox_val=checkbox_val: self.checkbox_clicked(checkbox_obj,checkbox_val))
            checkbox_obj.grid(column=i%4, row=i//4+5, sticky='w')
            self.checkboxes_dict[key] = (checkbox_obj, checkbox_val)  # Store both the Checkbutton and the BooleanVar

        # Create 'Enable All' and 'Disable All' buttons
        enable_all_button = tk.Button(self, text="Enable All", 
                                      command=self.enable_all_checkboxes)
        enable_all_button.grid(column=1, row=6+len(self.checkboxes_dict)//4, padx=10, pady=10)

        disable_all_button = tk.Button(self, text="Disable All", 
                                       command=self.disable_all_checkboxes)
        disable_all_button.grid(column=2, row=6+len(self.checkboxes_dict)//4, padx=10, pady=10)

        randomize_button = tk.Button(self, text="Randomize Humans", 
                             command=self.randomize_humans)
        randomize_button.grid(column=1, row=7+len(self.checkboxes_dict)//4, columnspan=2, padx=10, pady=10)

    def checkbox_clicked(self, checkbox_obj, checkbox_val):
        # This function is called when a checkbox is clicked
        if not checkbox_val.get():
            print("Checkbox was checked")
            checkbox_obj.select()
            checkbox_val.set(True)
        else:
            checkbox_obj.deselect()
            checkbox_val.set(False)
            print("Checkbox was unchecked")  

    def enable_all_checkboxes(self):
        # Enable all checkboxes
        for checkbox_obj, var in self.checkboxes_dict.values():
            checkbox_obj.select()
            var.set(True)

    def disable_all_checkboxes(self):
        # Disable all checkboxes
        for checkbox_obj, var in self.checkboxes_dict.values():
            checkbox_obj.deselect()
            var.set(False)
        
    def randomize_humans(self):
        # Prepare the dictionary argument for the randomize_addresses function
        selected_items_dict = {}
        for key, (checkbox_obj, var) in self.checkboxes_dict.items():
            if var.get():
                selected_items_dict[key] = template_human_dict[key]
                
        for humanInstance, address in selected_items_dict.items():
            print(f'"{humanInstance}": "{address}"')

        # Call the randomize_addresses function
        randomize_addresses(assetDSKFilePath, selected_items_dict)

class PageFour(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Create the "Single Replacement" label
        single_replacement_label = tk.Label(self, text="Single Replacement", padx=10, pady=10)
        single_replacement_label.grid(column=1, row=0, columnspan=2)

        # Create labels
        label1 = tk.Label(self, text="Selection", padx=10, pady=10)
        label1.grid(column=1, row=1)
        label2 = tk.Label(self, text="Replacement", padx=10, pady=10)
        label2.grid(column=2, row=1)

        # Create the dropdown menus
        dropdown1 = ttk.Combobox(self, values=list(template_veh_dict.keys()), width=35)
        dropdown1.grid(column=1, row=2, padx=10, pady=10)
        dropdown2 = ttk.Combobox(self, values=list(template_veh_dict.keys()), width=35)
        dropdown2.grid(column=2, row=2, padx=10, pady=10)

        # Create the button and send the user's input to the Replacing function
        button = tk.Button(self, text="Replace", 
                           command=lambda: replace_addresses(assetDSKFilePath,
                                                             template_veh_dict,
                                                             dropdown1.get(),
                                                             dropdown2.get()))
        button.grid(column=1, row=3, columnspan=2, padx=10, pady=10)

        # Create a label for the checkbox section
        checkbox_label = tk.Label(self, text="Randomization Settings", padx=10, pady=10)
        checkbox_label.grid(column=1, row=4, columnspan=2)

        # Create a dictionary to store the checkboxes
        self.checkboxes_dict = {}

        # Create a checkbox for each entry in the dictionary
        for i, key in enumerate(template_veh_dict.keys()):
            checkbox_val = tk.BooleanVar()
            checkbox_obj = tk.Checkbutton(self, text=key.decode('latin-1'), variable=checkbox_val, state='normal',
                                          command=lambda checkbox_val=checkbox_val: self.checkbox_clicked(checkbox_obj,checkbox_val))
            checkbox_obj.grid(column=i%4, row=i//4+5, sticky='w')
            self.checkboxes_dict[key] = (checkbox_obj, checkbox_val)  # Store both the Checkbutton and the BooleanVar

        # Create 'Enable All' and 'Disable All' buttons
        enable_all_button = tk.Button(self, text="Enable All", 
                                      command=self.enable_all_checkboxes)
        enable_all_button.grid(column=1, row=6+len(self.checkboxes_dict)//4, padx=10, pady=10)

        disable_all_button = tk.Button(self, text="Disable All", 
                                       command=self.disable_all_checkboxes)
        disable_all_button.grid(column=2, row=6+len(self.checkboxes_dict)//4, padx=10, pady=10)

        randomize_button = tk.Button(self, text="Randomize Vehicles", 
                             command=self.randomize_vehicles)
        randomize_button.grid(column=1, row=7+len(self.checkboxes_dict)//4, columnspan=2, padx=10, pady=10)

    def checkbox_clicked(self, checkbox_obj, checkbox_val):
        # This function is called when a checkbox is clicked
        if not checkbox_val.get():
            print("Checkbox was checked")
            checkbox_obj.select()
            checkbox_val.set(True)
        else:
            checkbox_obj.deselect()
            checkbox_val.set(False)
            print("Checkbox was unchecked")  

    def enable_all_checkboxes(self):
        # Enable all checkboxes
        for checkbox_obj, var in self.checkboxes_dict.values():
            checkbox_obj.select()
            var.set(True)

    def disable_all_checkboxes(self):
        # Disable all checkboxes
        for checkbox_obj, var in self.checkboxes_dict.values():
            checkbox_obj.deselect()
            var.set(False)
        
    def randomize_vehicles(self):
        # Prepare the dictionary argument for the randomize_addresses function
        selected_items_dict = {}
        for key, (checkbox_obj, var) in self.checkboxes_dict.items():
            if var.get():
                selected_items_dict[key] = template_veh_dict[key]
                
        for vehicleInstance, address in selected_items_dict.items():
            print(f'"{vehicleInstance}": "{address}"')

        # Call the randomize_addresses function
        randomize_addresses(assetDSKFilePath, selected_items_dict)

app = Application()
app.mainloop()

