# SimPly

## Introduction

**SimPly** est un parser d'un sous-ensemble très limité du langage Python.

`./simply.py <file1>.py [ <file2>.py ... ]`

Le résultat est créé dans `output.html`.

Les fichiers des arbres syntaxiques sont créés sous les noms `<file1>.s.gv` (arbre simple sans récursivité sur les expressions) et `<file1>.d.gv` (arbre profond avec récursivité sur les expressions). Les images `png` présentes sur la sortie `html` de même.

**Exemple**

Avec les fichiers d'exemples fournis :

`./simply.py examples/*.py`

## Sous-ensemble reconnu :

* Type `int` :
  * Opérations associées : `+`, `-`, `*`, `//` et `%` (le `-` unaire n'est pas reconnu)
  * Comparateurs : `<`, `>`, `<=` et `>=` (non-associatifs)
* Type `bool` :
  * Opérations assocées : `not`,`and`,`or`
* Comparateurs `==` et `!=` sur types identiques
* Parenthésage
* Structures `while` et `if`-`elif`-`else`

## À venir ? :

* `<<`, `>>`, `&` et `|`
* Listes (avec restrictions de type "tableau" ?)
* Fonctions

## Traitement de l'indentation :

Le traitement de l'indentation n'est pas vérifié. Lors d'un premier passage, une modification du code est effectué afin d'inférer le type d'indentation utilisée et remplacer chaque indentation par une tabulation `\t`, seule reconnue. Les espaces sont ignorés.

Lors du *parsing*, chaque tabulation rencontrée incrémente un compteur de tabulations, ce compteur servant à descendre récursivement l'arbre syntaxique afin d'insérer la ligne *parsée* au bon endroit dans l'arbre.

## Structure de l'arbre syntaxique :

La racine de l'arbre est un objet de type `ASTSequence`.
