# Plus court chemin stochastique

## Version de python
Le programme a été testé sur python 3.6.2.

## Dépendances
- Au minimum GLPK installé sur la machine (normalement nativement installé sous Linux et macos)
  https://www.gnu.org/software/glpk/
- pyYaml
  https://pypi.python.org/pypi/PyYAML
- puLP
  https://pypi.python.org/pypi/PuLP/1.6.5
- numpy
  http://www.numpy.org
- matplotlib
  https://matplotlib.org
- graphviz
  http://www.graphviz.org
- graphviz (package python)
  https://pypi.python.org/pypi/graphviz

## Exécutables
La documentation reliée à la façon dont il faut exécuter ces programmes
est décrite dans le fichier en docstring.

- solvers/reachability (problème d'accessibilité)
- solvers/sspe.py (problème de l'espérance du plus court chemin stochastique)
- solvers/sspp.py (problème des plus courts chemins stochastiques de taille limitée)
- structures/generator.py
- benchmarks/solvers_benchmarks.py

## Exemples du rapport
La résolution des exemples du rapport se trouve dans le dossier report.
Le numéro de l'exemple du rapport est stipulé en commentaire de
chaque fichier.

## Exemples de commandes
```
python3 solvers/reachability.py examples/mdp2.yaml t
python3 solvers/reachability.py examples/mdp3.yaml s5

python3 solvers/sspe.py examples/mdp2.yaml t
python3 solvers/sspe.py examples/agent_stochastic_maze.yaml --from '(1, 1)' --threshold 10 t1 t2

python3 solvers/sspp.py examples/simple_mdp.yaml s 8 0.2 t
python3 solvers/sspp.py examples/agent_stochastic_maze.yaml '(1, 1)' 20 0.2 t1 t2
```
