# Thoth, the Cairo/Starknet security toolkit (analyzer, disassembler and decompiler)

> [!IMPORTANT]  
> This repository is no longer maintained. If you have any questions or need further assistance, please contact [FuzzingLabs](https://fuzzinglabs.com/).

<img src ="https://img.shields.io/badge/python-3.10-blue.svg"/>

Thoth (pronounced "taut" or "toss") is a Cairo/Starknet security toolkit including analyzers, disassemblers & decompilers written in Python 3. Thoth's features include the generation of the call graph, the control-flow graph (CFG) and the data-flow graph for a given [Sierra file](/sierra/README.md) or Cairo/Starknet compilation artifact. It also includes some really advanced tools like a Symbolic execution engine and Symbolic bounded model checker.

Learn more about Thoth internals here: [Demo video](https://www.youtube.com/watch?v=T0KvG8Zps6I), [StarkNetCC 2022 slides](https://fuzzinglabs.com/wp-content/uploads/2022/11/Thoth_cairo_analyzer_starknetcc_lisbon_2022.pdf)

## Features
- **Remote & Local**: Thoth can both analyze contracts deployed on Mainnet/Goerli and compiled locally on your machine. 
- **[Decompiler](#decompile-the-contracts-compilation-artifact-json)**: Thoth can convert assembly into decompiled code with SSA (Static Single Assignment)  
- **[Call Flow analysis](#print-the-contracts-call-graph)**: Thoth can generate a **Call Flow Graph** 
- **[Static analysis](#run-the-static-analysis)**: Thoth can run various **analyzers** of different types (*security*/*optimization*/*analytics*) on the contract
- **[Symbolic execution](#use-the-symbolic-execution)**: Thoth can use the **symbolic execution** to find the right variables values to get through a specific path in a function and also automatically **generate test cases** for a function.
- **[Data Flow analysis](#print-the-contracts-data-flow-graph-dfg)**: Thoth can generate a **Data Flow Graph** (DFG) for each function
- **[Disassembler](#disassemble-the-contracts-compilation-artifact-json)**: Thoth can translate bytecode into assembly representation
- **[Control Flow analysis](#print-the-contracts-control-flow-graph-cfg)**: Thoth can generate a **Control Flow Graph** (CFG)
- **[Cairo Fuzzer inputs generation](#generate-inputs-for-the-cairo-fuzzer)**: Thoth can generate inputs for the  [**Cairo fuzzer**](https://github.com/FuzzingLabs/cairo-fuzzer)
- **[Sierra files analysis](/sierra/README.md)** : Thoth can analyze **Sierra** files 
- **[Sierra files symbolic execution](/doc/symbolic_execution.md)** : Thoth allows **symbolic execution** on sierra files
- **[Symbolic bounded model checker](/doc/symbolic_bounded_model_checker_sierra.md)** : Thoth can be used as a **Symbolic bounded model checker**
- **[Use it with a Scarb project](#use-it-with-a-scarb-project)** : Thoth can be used in a project created with the Scarb toolchain

## Installation
 
```
sudo apt install graphviz
git clone https://github.com/FuzzingLabs/thoth && cd thoth
pip install .
thoth -h
```

## Decompile the contract's compilation artifact (JSON)

``` python
# Remote contrat deployed on starknet (mainnet/goerli)
thoth remote --address 0x0323D18E2401DDe9aFFE1908e9863cbfE523791690F32a2ff6aa66959841D31D --network mainnet -d
# Local contract compiled locally (JSON file)
thoth local tests/json_files/cairo_0/cairo_test_addition_if.json -d
```

Example 1 with strings:
<p align="center">
	<b> source code </b></br>
	<img src="/doc/images/thoth/thoth_decompile_sourcecode.png"/></br>
	<b> decompiler code </b></br>
	<img src="/doc/images/thoth/thoth_decompile.png"/></br>
</p>
Example 2 with function call:
<p align="center">
	<b> source code </b></br>
	<img src="/doc/images/thoth/thoth_decompile_sourcecode_2.png"/></br>
	<b> decompiler code </b></br>
	<img src="/doc/images/thoth/thoth_decompile_2.png"/></br>
</p>


## Print the contract's call graph 

The call flow graph represents calling relationships between functions of the contract. We tried to provide a maximum of information, such as the entry-point functions, the imports, decorators, etc.

``` python
thoth local tests/json_files/cairo_0/cairo_array_sum.json -call -view
# For a specific output format (pdf/svg/png):
thoth local tests/json_files/cairo_0/cairo_array_sum.json -call -view -format png
```
The output file (pdf/svg/png) and the dot file are inside the `output-callgraph` folder.
If needed, you can also visualize dot files online using [this](https://dreampuf.github.io/GraphvizOnline/) website. The legend can be found [here](images/callgraph_legend.png).

<p align="center">
	<img src="/doc/images/thoth/thoth_callgraph_simple.png"/>
</p>

A more complexe callgraph:
<p align="center">
	<img src="/doc/images/thoth/starknet_get_full_contract_l2_dai_bridge.gv.png"/>
</p>

## Run the static analysis

The static analysis is performed using *analyzers* which can be either informative or security/optimization related.

|Analyzer|Command-Line argument|Description|Impact|Precision|Category|Bytecode|Sierra|
|---|---|---|---|---|---|---|---|
|**ERC20**|`erc20`|Detect if a contract is an ERC20 Token|Informational|High|Analytics|✔️|❌|
|**ERC721**|`erc721`|Detect if a contract is an ERC721 Token|Informational|High|Analytics|✔️|❌|
|**Strings**|`strings`|Detect strings inside a contract|Informational|High|Analytics|✔️|✔️|
|**Functions**|`functions`|Retrieve informations about the contract's functions|Informational|High|Analytics|✔️|✔️|
|**Statistics**|`statistics`|General statistics about the contract|Informational|High|Analytics|✔️|✔️|
|**Test cases generator**|`tests`|Automatically generate test cases for each function of the contract|Informational|High|Analytics|✔️|❌|
|**Assignations**|`assignations`|List of variables assignations|Informational|High|Optimization|✔️|❌|
|**Integer overflow**|`int_overflow`|Detect direct integer overflow/underflow|High (direct) / Medium (indirect)|Medium|Security|✔️|✔️|
|**Function naming**|`function_naming`|Detect functions names that are not in snake case|Informational|High|Security|✔️|❌|
|**Variable naming**|`variable_naming`|Detect variables names that are not in snake case|Informational|High|Security|✔️|❌|
|**Delegate calls detector**|`delegate_call`|Detect delegate calls|Informational|High|Security|❌|✔️|
|**Dead code detector**|`dead_code`|Detect dead code|Informational|High|Security|❌|✔️|
|**Unused arguments detector**|`unused_arguments`|Detect unused arguments|Informational|High|Security|❌|✔️|
|**User defined function call detector**|`user_defined`|Detect calls of user defined functions|Informational|High|Security|❌|✔️|

#### Run all the analyzers
``` python
thoth local tests/json_files/cairo_0/cairo_array_sum.json -a
```

#### Selects which analyzers to run
``` python
thoth local tests/json_files/cairo_0/cairo_array_sum.json -a erc20 erc721
```

#### Only run a specific category of analyzers
``` python
thoth local tests/json_files/cairo_0/cairo_array_sum.json -a security
thoth local tests/json_files/cairo_0/cairo_array_sum.json -a optimization
thoth local tests/json_files/cairo_0/cairo_array_sum.json -a analytics
```

#### Print a list of all the available analyzers
```
thoth local tests/json_files/cairo_0/cairo_array_sum.json --analyzers-help
```

## Use the symbolic execution 

You can find a detailed documentation for the symbolic execution [here](https://github.com/FuzzingLabs/thoth/blob/master/doc/symbolic_execution.md).

## Print the contract's data-flow graph (DFG)

``` python
thoth local tests/json_files/cairo_0/cairo_double_function_and_if.json -dfg -view
# For a specific output format (pdf/svg/png):
thoth local tests/json_files/cairo_0/cairo_double_function_and_if.json -dfg -view -format png
# For tainting visualization:
thoth remote --address 0x069e40D2c88F479c86aB3E379Da958c75724eC1d5b7285E14e7bA44FD2f746A8 -n mainnet  -dfg -view --taint
```
The output file (pdf/svg/png) and the dot file are inside the `output-dfg` folder.

<p align="center">
	<img src="/doc/images/thoth/thoth_dataflow_graph.png"/>
</p>

<p align="center">
	<img src="/doc/images/thoth/thoth_dfg_tainting.png"/>
</p>

## Disassemble the contract's compilation artifact (JSON)

``` python
# Remote contrat deployed on starknet (mainnet/goerli)
thoth remote --address 0x0323D18E2401DDe9aFFE1908e9863cbfE523791690F32a2ff6aa66959841D31D --network mainnet -b
# Local contract compiled locally (JSON file)
thoth local tests/json_files/cairo_0/cairo_array_sum.json -b
# To get a pretty colored version:
thoth local tests/json_files/cairo_0/cairo_array_sum.json -b -color
# To get a verbose version with more details about decoded bytecodes:
thoth local tests/json_files/cairo_0/cairo_array_sum.json -vvv
```

<p align="center">
	<img src="/doc/images/thoth/thoth_disas_color.png"/>
</p>

## Print the contract's control-flow graph (CFG)

``` python
thoth local tests/json_files/cairo_0/cairo_double_function_and_if.json -cfg -view
# For a specific function:
thoth local tests/json_files/cairo_0/cairo_double_function_and_if.json -cfg -view -function "__main__.main"
# For a specific output format (pdf/svg/png):
thoth local tests/json_files/cairo_0/cairo_double_function_and_if.json -cfg -view -format png
```
The output file (pdf/svg/png) and the dot file are inside the `output-cfg` folder.

<p align="center">
	<img src="/doc/images/thoth/cairo_double_function_and_if_cfg.png"/>
</p>

## Generate inputs for the Cairo fuzzer

You can generate inputs for the [Cairo fuzzer](https://github.com/FuzzingLabs/cairo-fuzzer) using this command

```
thoth local ./tests/json_files/cairo_0/cairo_test_symbolic_execution_2.json -a fuzzer
```

## Use it with a Scarb project

Add these lines to your `Scarb.toml` : 

```yaml
[[target.starknet-contract]]
sierra = true
casm = true
```

Then build the project using Scarb :

```sh
scarb build
```

You can now run Thoth with the `--scarb` flag :

```sh
// Run the disassembler
thoth local --scarb -b

// Run the analyzer
thoth local --scarb -a

// Generate the control-flow graph
thoth local --scarb --cfg

// Generate the callgraph
thoth local --scarb --call
```

# F.A.Q

## How to find a Cairo/Starknet compilation artifact (json file)?

Thoth supports cairo and starknet compilation artifact (json file) generated after compilation using `cairo-compile` or `starknet-compile`. Thoth also supports the json file returned by: `starknet get_full_contract`.

## How to run the tests?

```
python3 tests/test.py
```

## How to build the documentation?

``` python
# Install sphinx
apt-get install python3-sphinx

#Create the docs folder
mkdir docs & cd docs

#Init the folder
sphinx-quickstart docs

#Modify the `conf.py` file by adding
import thoth

#Generate the .rst files before the .html files
sphinx-apidoc -f -o . ..

#Generate the .html files
make html

#Run a python http server
cd _build/html; python3 -m http.server
```

## Why my bytecode is empty?

First, verify that your JSON is correct and that it contains a data section.
Second, verify that your JSON is not a contract interface.
Finally, it is possible that your contract does not generate bytecodes, for example:

``` cairo
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance() -> (res : felt):
end
```

# Acknowledgments

Thoth is inspired by a lot of different security tools developed by friends such as: [Octopus](https://github.com/FuzzingLabs/octopus), [Slither](https://github.com/crytic/slither), [Mythril](https://github.com/ConsenSys/mythril), etc.

# License

Thoth is licensed and distributed under the AGPLv3 license. [Contact us](mailto:contact@fuzzinglabs.com) if you're looking for an exception to the terms.
