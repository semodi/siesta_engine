from ase.calculators.siesta.siesta import Siesta
from ase.calculators.calculator import Calculator, all_changes
import shutil
import os
if not 'SIESTA_COMMAND' in os.environ:
    os.environ['SIESTA_COMMAND'] = 'siesta < ./%s > ./%s'

class CustomSiesta(Siesta):

    def __init__(self, fdf_path = None, *args, **kwargs):
        self.fdf_path = fdf_path
        if 'label' in kwargs:
            kwargs['label'] = kwargs['label'].lower()
        super().__init__(*args, **kwargs)


    def write_input(self, atoms, properties=None, system_changes=None):
        super().write_input(atoms, properties, system_changes)

        # add custom fdf
        if self.fdf_path:
            filename = os.path.join(self.directory, self.label + '.fdf')
            with open(self.fdf_path,'r') as custom_fdf:
                all_custom_keys = [list(entry.keys())[0]\
                 for _, entry in next_fdf_entry(custom_fdf)]

            filename_tmp = os.path.join(self.directory, self.label + '.tmp')
            with open(filename_tmp, 'w') as tmp_file:
                with open(self.fdf_path, 'r') as custom_fdf:
                    tmp_file.write(custom_fdf.read())

                with open(filename, 'r') as ase_fdf:
                    for is_block, entry in next_fdf_entry(ase_fdf):
                        if not list(entry.keys())[0] in all_custom_keys:
                            if 'pao' in list(entry.keys())[0] \
                            and any(['pao' in key for key in all_custom_keys]): continue
                            if is_block:
                                tmp_file.write('%block ')
                                tmp_file.write(list(entry.keys())[0])
                                tmp_file.write('\n')
                                tmp_file.write(list(entry.values())[0])
                                tmp_file.write('%endblock ')
                                tmp_file.write(list(entry.keys())[0])
                                tmp_file.write('\n')
                            else:
                                tmp_file.write(' '.join(list(entry.items())[0]))
                                tmp_file.write('\n')

            with open(filename_tmp, 'r') as tmp_file:
                with open(filename, 'w') as ase_fdf:
                    ase_fdf.write(tmp_file.read())

    def calculate(self, atoms=None, properties=['energy'],
                  system_changes=all_changes):

        if '0_NORMAL_EXIT' in os.listdir('.'):
            Calculator.calculate(self, atoms, properties, system_changes)
            self.write_input(self.atoms, properties, system_changes)
            # if self.command is None:
                # raise CalculatorSetupError(
                    # 'Please set ${} environment variable '
                    # .format('ASE_' + self.name.upper() + '_COMMAND') +
                    # 'or supply the command keyword')
            # command = self.command.replace('PREFIX', self.prefix)
            # errorcode = subprocess.call(command, shell=True, cwd=self.directory)

            # if errorcode:
            #     raise CalculationFailed('{} in {} returned an error: {}'
            #                             .format(self.name, self.directory,
            #                                     errorcode))
            self.read_results()
        else:
            super().calculate(atoms, properties, system_changes)



def next_fdf_entry(file):

    inside_block = False
    block_content = ''
    block_name = ''
    line = file.readline()
    while(line):
        if len(line.strip()) > 0:
            if line.strip()[0] == '%':
                if not inside_block:
                    block_name = ' '.join(line.split()[1:]).lower()
                else:
                    block_out = block_content
                    block_content = ''
                    yield True, {block_name: block_out}

                inside_block = (not inside_block)

            elif not inside_block:
                yield False, {line.split()[0].lower() : ' '.join(line.split()[1:])}
            else:
                block_content += line

        line = file.readline()
