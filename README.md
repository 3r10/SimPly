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

Lors d'un premier passage, une modification du code est effectué afin d'inférer le type d'indentation utilisée et remplacer chaque indentation par une tabulation `\t`, seule reconnue. Les espaces sont ignorés.

La classe SimplyLex est un "wrapper" du lexer lex. Elle permet :
* de rajouter artificiellement les tokens `INDENT` et `DEDENT`, en particulier les `DEDENT` multiples qui, sinon, ne pourraient pas être ajoutés à la pile des tokens.
* de garder trace du code source et de la position du lexer pour chaque token rencontré, afin de pouvoir réaliser une coloration syntaxique du code.

## Structure de l'arbre syntaxique :

La racine de l'arbre est un objet de type `ASTSequence`.
