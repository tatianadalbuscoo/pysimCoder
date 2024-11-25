"""
This is a procedural interface to the RCPblk library

roberto.bucher@supsi.ch

The following class is provided:

  RCPblk      - class with info for Rapid Controller Prototyping

The following commands are provided:

  load_module    - Reads file source and loads it as a module
  run_plugin     - run plugin if exists
  genCode        - Create  C code from BlockDiagram
  genMake        - Generate the Makefile for the C code
  detBlkSeq      - Get the right block sequence for simulation and RT
  sch2blks       - Generate block list fron schematic
  
"""
from numpy import nonzero, ones, asmatrix, size, array, zeros
from os import environ
import copy
import sys
from supsisim.RCPblk import RCPblk
from supsisim.SHVgen import genSHVtree, genSHVcode, genSHVheader, genSHVend
import importlib.util
import os

def load_module(module_path):

    """ 
    Reads a file source and loads it as a module.
    
    Example Call:
    -------------
    module = load_module('/path/to/script.py')
    
    Parameters
    ----------
    module_path: Path to the file to load.
    
    Returns
    -------
    module or None
        The loaded module, or None if an error occurs during loading.
    """

    try:

        # Extracts the module name from the path (removes the .py extension)
        module_name = os.path.basename(module_path).replace('.py', '')
        
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        return module

    except FileNotFoundError:
        print(f"Error: File {module_path} not found.")
        return None
    except Exception as e:
        print(f"Error loading module {module_path}: {e}")
        return None


def run_plugin(model, template, function_name=None, function_args=None):

    """ 
    Runs a plugin with the same name as the template (for example, run delfino.py if the template is delfino.tmf). 
    If a function is specified with its arguments, runs the specified function.
    If the function does not exist, the plugin is executed anyway. All statements outside the functions are executed.
    If there is no .py script corresponding to the .tmf file, nothing is executed and nothing happens.

    
    Example Call:
    -------------
    run_plugin('model_name', 'template_name.tmf', 'create_project_structure', {'arg1': value1})
    run_plugin('model_name', 'template_name.tmf')
    
    Parameters
    ----------
    model        : The name of the model.
    template     : The template file (e.g., 'delfino.tmf') from which the corresponding Python script (e.g., 'delfino.py') is derived.
    function_name: (optional) The name of the function to execute in the loaded script. If None, the entire script will be executed.
    function_args: dict or list, (optional) Arguments to pass to the specified function. If None, the function will be called without arguments.
    
    Returns
    -------
    -

    """

    template_path = environ.get('PYSUPSICTRL')
    
    # Removes the extension from the template file (.tmf)
    base_name = os.path.splitext(template)[0]
    
    script_path = os.path.join(template_path, 'CodeGen', 'templates', base_name + '.py')

    # If specific .py file exists
    if os.path.exists(script_path):

        # Loads the module
        module = load_module(script_path)

        if module:
            try:

                # Executes the module
                spec = importlib.util.spec_from_file_location(module.__name__, script_path)
                spec.loader.exec_module(module)

                if function_name:

                    # Execute the specified function
                    if hasattr(module, function_name):
                        func = getattr(module, function_name)
                        
                        try:
                            # Call the function based on function_args
                            if function_args is None:
                                func()  # No arguments passed
                            elif isinstance(function_args, dict):
                                func(**function_args)
                            elif isinstance(function_args, list):
                                func(*function_args)

                        except AttributeError as e:
                            print(f"AttributeError: The function '{function_name}' encountered an attribute issue: {e}")
                        except TypeError as e:
                            print(f"TypeError: The arguments provided to the function '{function_name}' are incorrect: {e}")
                        except Exception as e:
                            print(f"An unexpected error occurred while calling '{function_name}': {e}")
            except Exception as e:
                print(f"An error occurred while executing: {e}")
        else:
            print("Failed to load the module.")


def genCode(model, Tsamp, blocks, template, rkstep=10):
    """Generate C-Code

    Call: genCode(model, Tsamp, Blocks, rkstep)

    Parameters
    ----------
    model     : Model name
    Tsamp     : Sampling Time
    Blocks    : Block list
    rkstep    : step division per sample time for fixed step solver

    Returns
    -------
    -
    """

    run_plugin(model, template, 'check_blocks', [model, blocks])

    maxNode = 0
    for blk in blocks:
        for n in range(0, size(blk.pin)):
            if blk.pin[n] > maxNode:
                maxNode = blk.pin[n]
        for n in range(0, size(blk.pout)):
            if blk.pout[n] > maxNode:
                maxNode = blk.pout[n]

    # Check outputs not connected together!
    outnodes = zeros(maxNode + 1)
    for blk in blocks:
        for n in range(0, size(blk.pout)):
            if outnodes[blk.pout[n]] == 0:
                outnodes[blk.pout[n]] = 1
            else:
                raise ValueError('Problem in diagram: outputs connected together!')

    Blocks = detBlkSeq(maxNode, blocks)
    if size(Blocks) == 0:
        raise ValueError('No possible to determine the block sequence')

    fn = model + '.c'
    f = open(fn, 'w')
    strLn = "#include <pyblock.h>\n#include <stdio.h>\n#include <stdlib.h>\n\n"
    f.write(strLn)

    N = size(Blocks)

    genSHVheader(f, model, N)

    totContBlk = 0
    for blk in Blocks:
        totContBlk += blk.nx[0]

    f.write("/* Function prototypes */\n\n")

    prototypes = []
    
    for blk in Blocks:
        prototypes.append("void " + blk.fcn + "(int Flag, python_block *block);\n")
    setProto = set(prototypes)
    for el in setProto:
        f.write(el)

    f.write("\n")

    strLn = "double " + model + "_get_tsamp(void)\n"
    strLn += "{\n"
    strLn += "  return (" + str(Tsamp) + ");\n"
    strLn += "}\n\n"
    f.write(strLn)

    strLn = "python_block block_" + model + "[" + str(N) + "];\n\n"
    f.write(strLn)

    for n in range(0, N):
        blk = Blocks[n]
        if (size(blk.realPar) != 0):
            strLn = "static double realPar_" + str(n) +"[] = {"
            strLn += str(asmatrix(blk.realPar).tolist())[2:-2] + "};\n"
            strLn += "static char *realParNames_" + str(n) + "[] = {"
            tmp = 0
            if (size(blk.realPar) != size(blk.realParNames)):
                for i in range(0, size(blk.realPar)):
                    strLn += "\"double" + str(i) + "\""
                    if ((tmp + 1) != size(blk.realPar)):
                        strLn += ", "
                    tmp += 1
            else:
                for i in range(0, size(blk.realPar)):
                    strLn += "\"" + str(blk.realParNames[i]) + "\""
                    if ((tmp + 1) != size(blk.realPar)):
                        strLn += ", "
                    tmp += 1
            strLn += "};\n"
            f.write(strLn)
        if (size(blk.intPar) != 0):
            strLn = "static int intPar_" + str(n) +"[] = {"
            strLn += str(asmatrix(blk.intPar).tolist())[2:-2] + "};\n"
            strLn += "static char *intParNames_" + str(n) + "[] = {"
            tmp = 0
            for i in range(0, size(blk.intPar)):
                strLn += "\"int" + str(i) + "\""
                if ((tmp + 1) != size(blk.intPar)):
                    strLn += ", "
                tmp += 1
            strLn += "};\n"
            f.write(strLn)
        strLn = "static int nx_" + str(n) +"[] = {"
        strLn += str(asmatrix(blk.nx).tolist())[2:-2] + "};\n"
        f.write(strLn)
    f.write("\n")

    f.write("/* Nodes */\n")
    for n in range(1, maxNode+1):
        strLn = "static double Node_" + str(n) + "[] = {0.0};\n"
        f.write(strLn)

    f.write("\n")

    f.write("/* Input and outputs */\n")
    for n in range(0, N):
        blk = Blocks[n]
        nin = size(blk.pin)
        nout = size(blk.pout)
        if nin != 0:
            strLn = "static void *inptr_" + str(n) + "[]  = {"
            for m in range(0, nin):
                strLn += "&Node_" + str(blk.pin[m]) + ","
            strLn = strLn[0:-1] + "};\n"
            f.write(strLn)
        if nout != 0:
            strLn = "static void *outptr_" + str(n) + "[] = {"
            for m in range(0, nout):
                strLn += "&Node_" + str(blk.pout[m]) + ","
            strLn = strLn[0:-1] + "};\n"
            f.write(strLn)

    f.write("\n\n")

    Blks = []
    for n in range(0, N):
        Blks.append(Blocks[n].name)

    BlksOrigin = copy.deepcopy(Blks)
    Blks.sort()

    if (environ["SHV_TREE_TYPE"] == "GSA_STATIC") and (environ["SHV_USED"] == "True"):
        genSHVtree(f, Blocks, Blks)

    f.write("/* Initialization function */\n\n")
    strLn = "void " + model + "_init(void)\n"
    strLn += "{\n\n"
    f.write(strLn)

    f.write("/* Block definition */\n\n")
    for n in range(0, N):
        blk = Blocks[n]
        nin = size(blk.pin)
        nout = size(blk.pout)
        num = 0

        strLn = "  block_" + model + "[" + str(n) + "].nin  = " + str(nin) + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].nout = " + str(nout) + ";\n"

        port = "nx_" + str(n)
        strLn += "  block_" + model + "[" + str(n) + "].nx   = " + port + ";\n"

        if nin == 0:
            port = "NULL"
        else:
            port = "inptr_" + str(n)
        strLn += "  block_" + model + "[" + str(n) + "].u    = " + port + ";\n"
        if nout == 0:
            port = "NULL"
        else:
            port = "outptr_" + str(n)
        strLn += "  block_" + model + "[" + str(n) + "].y    = " + port + ";\n"
        if size(blk.realPar) != 0:
            par = "realPar_" + str(n)
            parNames = "realParNames_" + str(n)
            num = size(blk.realPar)
        else:
            par = "NULL"
            parNames = "NULL"
            num = 0
        strLn += "  block_" + model + "[" + str(n) + "].realPar = " + par + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].realParNum = " + str(num) + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].realParNames = " + parNames + ";\n"
        if size(blk.intPar) != 0:
            par = "intPar_" + str(n)
            parNames = "intParNames_" + str(n)
            num = size(blk.intPar)
        else:
            par = "NULL"
            parNames = "NULL"
            num = 0
        strLn += "  block_" + model + "[" + str(n) + "].intPar = " + par + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].intParNum = " + str(num) + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].intParNames = " + parNames + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].str = " +'"' + blk.str + '"' + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].ptrPar = NULL;\n"
        f.write(strLn)
        f.write("\n")
    f.write("\n")

    if environ["SHV_USED"] == "True":
        genSHVcode(f, model, Blocks, Blks)

    f.write("/* Set initial outputs */\n\n")

    for n in range(0, N):
        blk = Blocks[n]
        strLn = "  " + blk.fcn + "(CG_INIT, &block_" + model + "[" + str(n) + "]);\n"
        f.write(strLn)
    f.write("}\n\n")

    f.write("/* ISR function */\n\n")
    strLn = "void " + model + "_isr(double t)\n"
    strLn += "{\n"
    f.write(strLn)

    if totContBlk != 0:
        f.write("int i;\n")
        f.write("double h;\n\n")

    for n in range(0, N):
        blk = Blocks[n]
        strLn = "  " + blk.fcn + "(CG_OUT, &block_" + model + "[" + str(n) + "]);\n"
        f.write(strLn)
    f.write("\n")

    for n in range(0, N):
        blk = Blocks[n]
        if blk.nx[1] != 0:
            strLn = "  " + blk.fcn + "(CG_STUPD, &block_" + model + "[" + str(n) + "]);\n"
            f.write(strLn)
    f.write("\n")

    if totContBlk != 0:
        strLn = "  h = " + model + "_get_tsamp()/" + str(rkstep) + ";\n\n"
        f.write(strLn)

        for n in range(0, N):
            blk = Blocks[n]
            if blk.nx[0] != 0:
                strLn = "  block_" + model + "[" + str(n) + "].realPar[0] = h;\n"
                f.write(strLn)

        strLn = "  for(i=0;i<" + str(rkstep) + ";i++){\n"
        f.write(strLn)
        for n in range(0, N):
            blk = Blocks[n]
            if blk.nx[0] != 0:
                strLn = "    " + blk.fcn + "(CG_OUT, &block_" + model + "[" + str(n) + "]);\n"
                f.write(strLn)

        for n in range(0, N):
            blk = Blocks[n]
            if blk.nx[0] != 0:
                strLn = "    " + blk.fcn + "(CG_STUPD, &block_" + model + "[" + str(n) + "]);\n"
                f.write(strLn)

        f.write("  }\n")

    f.write("}\n")

    f.write("/* Termination function */\n\n")

    strLn = "void " + model + "_end(void)\n"
    strLn += "{\n"
    f.write(strLn)

    if environ["SHV_USED"] == "True":
        genSHVend(f, model)

    for n in range(0, N):
        blk = Blocks[n]
        strLn = "  " + blk.fcn + "(CG_END, &block_" + model + "[" + str(n) + "]);\n"
        f.write(strLn)
    f.write("}\n\n")
    f.close()


def genMake(model, template, addObj=''):
    """Generate the Makefile

    Call: genMake(model, template)

    Parameters
    ----------
    model     : Model name
    template  : Template makefile
    addObj    : Additional object files

    Returns
    -------
    -
    """

    # If exists a file with the same name of template run the plugin
    run_plugin(model, template, 'create_project_structure', [model])

    template_path = environ.get('PYSUPSICTRL')
    fname = template_path + '/CodeGen/templates/' + template
    f = open(fname, 'r')
    mf = f.read()
    f.close()
    mf = mf.replace('$$MODEL$$', model)
    mf = mf.replace('$$ADD_FILES$$', addObj)
    f = open('Makefile', 'w')
    f.write(mf)
    f.close()

def detBlkSeq(Nodes, blocks):
    """Generate the Block sequence for simulation and RT

    Call: detBlkSeq(Nodes, Blocks)

    Parameters
    ----------
    Nodes     : Number of total nodes in diagram
    blocks    : List with the unordered blocks

    Returns
    -------
    Blocks    : List with the ordered blocks
    """
    class blkDep:
        def __init__(self, block, blkL, nodeL):
            self.block = block
            self.block_in = []

            if len(block.pin) != 0:
                for node in block.pin:
                    if nodeL[node].block_in[0].uy == 1:
                        self.block_in.append(nodeL[node].block_in[0])
  

        def __str__(self):
            txt  = 'Block: ' + self.block.fcn.__str__() + '\n'
            txt += 'Inputs\n'
            for item in self.block_in:
                txt += item.fcn + '\n'
            txt += '\n'
            return txt

    class nodeClass:
        def __init__(self, N):
            self.PN = N
            self.block_in = []
            self.block_out = []

        def __str__(self):
            txt  = 'Node: ' + self.PN.__str__() + '\n'
            txt += ' Blocks in:\n'
            for item in self.block_in:
                try:
                    txt += item.fcn + '\n'
                except:
                    txt += 'None\n'
            txt += ' Blocks out:\n'
            for item in self.block_out:
                try:
                    txt += item.fcn + '\n'
                except:
                    txt += 'None\n'
            return txt

    def fillNodeList(nN,blks):
        nL = []
        nL.append(nodeClass(0))
        for n in range(1, nN+1):
            node = nodeClass(n)
            nL.append(node)
        for blk in blks:
            for n in blk.pin:
                nL[n].block_out.append(blk)
            for n in blk.pout:
                nL[n].block_in.append(blk)
        return nL

    blks = []
    blks2order = []

    nodes = fillNodeList(Nodes, blocks)

    # First search block with no input and no output

    for blk in blocks:
        if blk.uy == 0:
            if len(blk.pin) == 0 and len(blk.pout) == 0:
                blks.insert(0, blk)
            else:
                blks.append(blk)
        else:
            block = blkDep(blk, blocks, nodes)
            blks2order.append(block)

    # Order the remaining blocks
    counter = 0
    while len(blks2order) != counter:
        blk = blks2order.pop(0)
        if len(blk.block_in) == 0:
            blks.append(blk.block)
            counter = 0

            try:
                for node in blk.block.pout:
                    for bk in nodes[node].block_out:
                        el = [el for el in blks2order if el.block == bk]
                        try:
                            el[0].block_in.remove(blk.block)
                        except:
                            pass
            except:
                pass
        else:
            blks2order.append(blk)
            counter += 1

    # Check if remain blocks in blks2order -> Algeabric loop!
    if len(blks2order) != 0:
        for item in blks2order:
            print(item.block)
        raise ValueError("Algeabric loop!")

    return blks