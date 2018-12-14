#!/usr/bin/env python
from __future__ import print_function

import os
# Must be done before any CDAT library is called.
os.environ['UVCDAT_ANONYMOUS_LOG'] = 'no'
os.environ['CDAT_ANONYMOUS_LOG'] = 'no'
# Needed for when using hdf5 >= 1.10.0,
# without this, errors are thrown on Edison compute nodes.
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
# Used by numpy, causes too many threads to spawn otherwise.
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

import sys
import importlib
import traceback
import cdp.cdp_run
from cdp.cdp_provenance import save_provenance
from acme_diags.acme_parser import ACMEParser
from acme_diags.acme_viewer import create_viewer
from acme_diags.driver import utils
from acme_diags import INSTALL_PATH, container


def _get_default_diags(set_name, run_type):
    """
    Returns the path for the default diags for plotset set_name.
    These are different depending on the run_type.
    """
    set_num = utils.general.get_set_name(set_name)

    folder = '{}'.format(set_name)
    fnm = '{}_{}.cfg'.format(set_name, run_type)
    pth = os.path.join(INSTALL_PATH, folder, fnm)

    print('Using {} for {}.'.format(pth, set_name))
    if not os.path.exists(pth):
        raise RuntimeError(
            "Plotting via set '{}' not supported, file {} not installed".format(set_name, fnm))
    return pth


def _collapse_results(parameters):
    """
    When using cdp_run, parameters is a list of lists: [[Parameters], ...].
    Make this just a list: [Parameters, ...].
    """
    output_parameters = []

    for p1 in parameters:
        if isinstance(p1, list):
            for p2 in p1:
                output_parameters.append(p2)
        else:
            output_parameters.append(p1)

    return output_parameters


def get_parameters(parser=ACMEParser()):
    """
    Get the parameters from the parser.
    """
    args = parser.view_args()

    # There weren't any arguments defined.
    if not any(getattr(args, arg) for arg in vars(args)):
        parser.print_help()
        sys.exit()

    if args.parameters and not args.other_parameters:  # -p only
        original_parameter = parser.get_orig_parameters(argparse_vals_only=False)

        # Load the default cfg files.
        run_type = getattr(original_parameter, 'run_type', 'model_vs_obs')
        if original_parameter.no_viewer:
            # When ran with no_viewer, it's most likely that
            # output from the provenance is used to run this.
            # So don't use the default cfgs to choose diags from,
            # all parameters needed is from the file.
            default_diags_paths = []
        else:
            default_diags_paths = [_get_default_diags(set_name, run_type) for set_name in utils.general.SET_NAMES]

        other_parameters = parser.get_other_parameters(files_to_open=default_diags_paths, argparse_vals_only=False)

        parameters = parser.get_parameters(orig_parameters=original_parameter,
            other_parameters=other_parameters, cmd_default_vars=False, argparse_vals_only=False)

    else:
        parameters = parser.get_parameters(cmd_default_vars=False, argparse_vals_only=False)

    parser.check_values_of_params(parameters)

    print('len(parameters)', len(parameters))
    return parameters


def run_diag(parameters):
    """
    For a single set of parameters, run the corresponding diags.
    """
    results = []
    for pset in parameters.sets:
        set_name = utils.general.get_set_name(pset)

        parameters.current_set = set_name
        mod_str = 'acme_diags.driver.{}_driver'.format(set_name)
        try:
            module = importlib.import_module(mod_str)
            single_result = module.run_diag(parameters)
            print('')
            results.append(single_result)
        except:
            print('Error in {}'.format(mod_str))
            traceback.print_exc()
            if parameters.debug:
                sys.exit()

    return results


def main():
    parser = ACMEParser()
    parameters = get_parameters(parser)

    # Save this value before running the diags.
    # When the Python file is created for this run,
    # this is always set to True.
    no_viewer = parameters[0].no_viewer

    if not os.path.exists(parameters[0].results_dir):
        os.makedirs(parameters[0].results_dir)
    if not no_viewer:  # Only save provenance for full runs.
        msg = '# e3sm_diags was ran in a container.\n' if container.is_container() else ''
        save_provenance(parameters[0].results_dir, parser, msg)

    if container.is_container():
        print('Running e3sm_diags in a container.')
        # Parameters will decontainerized by the viewer later.
        # That's to make sure the command shown in the viewer works with or without the viewer.
        for p in parameters:
            container.containerize_parameter(p)

    if parameters[0].multiprocessing:
        parameters = cdp.cdp_run.multiprocess(run_diag, parameters)
    elif parameters[0].distributed:
        parameters = cdp.cdp_run.distribute(run_diag, parameters)
    else:
        parameters = cdp.cdp_run.serial(run_diag, parameters)

    parameters = _collapse_results(parameters)

    if not parameters:
        print('There was not a single valid diagnostics run, no viewer created.')
    else:
        if no_viewer:
            print('Viewer not created because the no_viewer parameter is True.')
        else:
            pth = os.path.join(parameters[0].results_dir, 'viewer')
            if not os.path.exists(pth):
                os.makedirs(pth)
            create_viewer(pth, parameters, parameters[0].output_format[0])
            path = os.path.join(parameters[0].results_dir, 'viewer')
            print('Viewer HTML generated at {}/index.html'.format(path))

if __name__ == '__main__':
    main()
