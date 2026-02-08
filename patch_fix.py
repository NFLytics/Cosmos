import re
import os

def patch_import_mismatch():
    print('Initiating Auto-Patch for Import Mismatch...')
    stat_tests_path = os.path.join('src', 'statistical_tests.py')
    main_v2_path = os.path.join('src', 'main_v2.py')
    
    found_class = None
    if os.path.exists(stat_tests_path):
        with open(stat_tests_path, 'r') as f:
            content = f.read()
            matches = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
            for m in matches:
                if 'Interpretation' in m:
                    found_class = m
                    break
            if not found_class and len(matches) == 1:
                found_class = matches[0]

    if found_class:
        print(f'Found target class: {found_class}')
        with open(main_v2_path, 'r') as f:
            main_content = f.read()
        
        # Patch the specific import line
        if 'from src.statistical_tests import Interpretation' in main_content:
            new_content = main_content.replace(
                'from src.statistical_tests import Interpretation', 
                f'from src.statistical_tests import {found_class} as Interpretation'
            )
            with open(main_v2_path, 'w') as f:
                f.write(new_content)
            print('Patch applied successfully.')
        else:
            print('Import line already matches or not found.')
    else:
        print('Could not resolve class name automatically.')

if __name__ == '__main__':
    patch_import_mismatch()
