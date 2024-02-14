# Misc 
from argparse import ArgumentParser
from ruamel.yaml.main import YAML
# Surfaxe 
from surfaxe.generation import generate_slabs

def _oxstates_to_dict(ox): 
    keys, values = ([] for i in range(2))
    for i in ox.split(','): 
        m = i.split(':')
        values.append(float(m.pop(1)))
        keys.append(str(m.pop(0)))

    ox_states_dict = dict(zip(keys,values))
    return ox_states_dict

def _hkl(hkl): 
    if len(hkl) == 1: 
        # one hkl
        if ',' in hkl[0]: 
            miller = tuple(map(int, hkl[0].strip('[]()').split(',')))
        # max index
        else: 
            miller = int(hkl[0])
    else: 
        # several hkl 
        miller = []
        for i in hkl: 
            miller.append(tuple(map(int, i.strip('[]()').split(','))))

    return miller

def _get_parser(): 
    parser = ArgumentParser(
        description="""Generates all unique slabs for a specified Miller indices 
        or up to a maximum Miller index with minimum slab and vacuum thicknesses. 
        It includes all combinations for multiple zero dipole symmetric 
        terminations for the same Miller index. Always saves slabs to file. 
        If no slabs are produced, check if the Miller index requested has a 
        zero-dipole termination"""
    )

    parser.add_argument('-s', '--structure', default=None, type=str,
    help='Filename of structure file in any format supported by pymatgen')
    parser.add_argument('--hkl', default=None, nargs='+',
    help='Maximum Miller index (e.g. 1), a specific Miller index (e.g. 0,0,1) '
    'or several Miller indices (e.g. 0,0,1 1,1,1)')
    parser.add_argument('-t', '--thicknesses', default=None, nargs='+', type=int,
    help='The minimum sizes of the slab in Angstroms, e.g. 10 20')
    parser.add_argument('-v', '--vacuums', default=None, nargs='+', type=int,
    help='The minimum sizes of the vacuum in Angstroms, e.g. 10 20')
    parser.add_argument('-r', '--fols', default=False, action='store_true', 
    help=('Makes folders for each termination and slab/vacuum thickness ' 
          'combinations containing POSCARs (default: False)'))
    parser.add_argument('-f', '--files', default=False, action='store_true', 
    help='Makes INCAR, POTCAR and KPOINTS files in each folder (default: False)')
    parser.add_argument('--max-size', default=500, dest='max_size', type=int,
    help=('The maximum number of atoms in the slab specified to raise warning ' 
          'about slab size. Even if the warning is raised, it still outputs ' 
          'the slabs regardless. (default: 500)'))
    parser.add_argument('--not-centered', default=True, dest='center_slab',
    action='store_false', help='The position of the slab in the simulation cell')
    parser.add_argument('--oxi-list', default=None, dest='ox_states_list', 
    nargs='+', type=float, 
    help='Add oxidation states to the structure as a list e.g. 3 3 -2 -2 -2')
    parser.add_argument('--oxi-dict', default=None, type=_oxstates_to_dict,
    dest='ox_states_dict', help=('Add oxidation states to the structure as ' 
    'a dictionary e.g. Fe:3,O:-2'))
    parser.add_argument('--no-sym', default=True, action='store_false', 
    dest='is_symmetric', help=('Whether the slabs cleaved should have inversion '
    'symmetry. By default searches for slabs with inversion symmetry'))
    parser.add_argument('--sd', default=None, type=int, 
    help='Number of layers to relax using selective dyanamics in VASP.')
    parser.add_argument('--fmt', default='poscar', type=str, 
    help='Format of output files (default: poscar)')
    parser.add_argument('--name', default='POSCAR', type=str, 
    help='Name of the surface slab structure file created (default: POSCAR)')
    parser.add_argument('--config-dict', default='PBEsol.json', 
    dest='config_dict', 
    help='Specifies the dictionary used for the generation of the input files')
    parser.add_argument('-i', '--incar', default=None,
    help='Overrides the default INCAR parameter settings')
    parser.add_argument('-k', '--kpoints', default=None,
    help='Overrides the default KPOINTS settings.')
    parser.add_argument('-p', '--potcar', default=None,
    help='Overrides the default POTCAR settings')
    parser.add_argument('--processes', default=None,
    help='CPU processes to use in multiprocessing, default is max-1')
    parser.add_argument('--yaml', default=None, type=str,
    help=('Read all args from surfaxe_config.yaml file. Completely overrides any '
    'other flags set'))

    return parser

def main(): 
    args = _get_parser().parse_args()

    if args.yaml is not None: 
        with open(args.yaml, 'r') as y:
            yaml = YAML(typ='safe', pure=True)
            yaml_args = yaml.load(y)

        # get hkl first as a list, then convert to 
        hkl = list(yaml_args.pop('hkl'))
        miller = _hkl(hkl)
        generate_slabs(hkl=miller, **yaml_args)

    else: 
        if args.ox_states_dict: 
            ox_states = args.ox_states_dict 
        elif args.ox_states_list: 
            ox_states = args.ox_states_list
        else: 
            ox_states=None

        miller = _hkl(args.hkl)

        generate_slabs(args.structure, miller, args.thicknesses, 
        args.vacuums, make_fols=args.fols, make_input_files=args.files, 
        max_size=args.max_size, center_slab=args.center_slab, name=args.name, 
        ox_states=ox_states,is_symmetric=args.is_symmetric, fmt=args.fmt, 
        config_dict=args.config_dict, user_incar_settings=args.incar, 
        user_potcar_settings=args.potcar, user_kpoints_settings=args.kpoints, 
        layers_to_relax=args.sd, processes=args.processes)

if __name__ == "__main__":
    main()
