# Plus court chemin stochastique

## Version de python
Le programme a été testé sur python 3.6.2

## Dépendances
- Au minimum GLPK installé sur la machine (normalement installé de base sous Linux et macos)
- pyYaml
- puLP
- numpy
- matplotlib
- graphviz
- graphviz (package python)

## Exécutables
La documentation reliée à la façon dont il faut exécuter ces programmes
est décrite dans le fichier en docstring.

- solvers/reachability (problème d'accessibilité)
- solvers/sspe.py (problème de l'espérance du plus court chemin stochastique)
- solvers/sspp.py (problème des plus courts chemins stochastiques de taille limitée)
- structures/generator
- benchmarks/solvers_benchmarks

## Exemples du rapport
La résolution des exemples du rapport se trouve dans le dossier report

## Exemples de commandes
```
python3 solvers/reachability.py examples/mdp2.yaml t
python3 solvers/reachability.py examples/mdp3.yaml s5

python3 solvers/sspe.py examples/mdp2.yaml t
python3 solvers/sspe.py examples/agent_stochastic_maze.yaml --from '(1, 1)' --threshold 10 t1 t2

python3 solvers/sspp.py examples/simple_mdp.yaml s 8 0.2 t
python3 solvers/sspp.py examples/agent_stochastic_maze.yaml '(1, 1)' 20 0.2 t1 t2
```
