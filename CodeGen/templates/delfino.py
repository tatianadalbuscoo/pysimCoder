import os
import sys

def create_project_structure(model):
    project_dir = f"./{model}_project"
    src_dir = os.path.join(project_dir, "src")
    include_dir = os.path.join(project_dir, "include")

    # Crea le cartelle
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(include_dir, exist_ok=True)

    # Crea il file main.c
    main_file = os.path.join(src_dir, "main.c")
    with open(main_file, 'w') as f:
        f.write(f'#include "{model}.h"\n\n')
        f.write('int main(void) {\n')
        f.write(f'    {model}_init();\n')
        f.write('    while (1) {\n')
        f.write(f'        {model}_isr();\n')
        f.write('    }\n')
        f.write('    return 0;\n')
        f.write('}\n')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_structure.py <model_name>")
    else:
        model_name = sys.argv[1]
        create_project_structure(model_name)
