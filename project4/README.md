# WAN Traffic Engineering Project

### Information

* Group number: *Group 1*
* Student NetIDs: *rroethlis*, *dominibr*

### Part C explanation

Find edge disjoint paths (networkx.edge_disjoint_paths(graph, i, j, cutoff=5)), then fill up until 10 with shortest paths (networkx.all_simple_paths(graph, i, j, cutoff=4)).

### Getting started

**Dependencies**

* Python 3.7+
* `python3 -m pip install networkx`
* `python3 -m pip install numpy`
* `python3 -m pip install ortools`
* `python3 -m pip install git+https://github.com/snkas/python-ortools-lp-parser.git@v1.5.2`

**What you have to do in a nutshell**

1. You can verify your solutions yourself locally by running `cd code; python3 evaluator_myself.py`
2. Set your team name by editing team_name.txt
3. Implement code/skeleton_a.py (run via `cd code; python3 skeleton_a.py`)
4. Implement code/skeleton_b.py (run via `cd code; python3 skeleton_b.py`)
5. Implement code/skeleton_c.py (run via `cd code; python3 skeleton_c.py`)

Proper software engineering practices (e.g. splitting off shared functionality between the three parts into separate files) are encouraged. For any other explanation look at wan_te_project.pdf

**Leaderboard**

The output you commit and push into the Git repository in myself/output/c is evaluated every 5 min approximately. You can view the leaderboard at:

http://bach02.ethz.ch/leaderboard.html
