# SimPly

## Introduction

**SimPly** est un compilateur d'un sous-ensemble très limité du langage Python vers le langage assembleur ARM.

`./simply.py file.py file.S`

Le fichier destination comprend :
* Le code source original
* L'arbre syntaxique au format ASCII
* Une partie compilée
* Les "fonctions" utilitaires pour `print`

**Exemple**

Avec un d'exemple fourni :
* `./simply.py examples/factorial.py test.S`

Sous linux, le fichier peut alors être assemblé et exécuté avec les commandes
suivantes :
* assembleur : `arm-linux-gnueabihf-gcc -ggdb3 -nostdlib -o test -static test.S`
* exécution : `qemu-arm test`

## Sous-ensemble reconnu :

* Type `int` :
  * Opérations associées : `+`, `-`, `*`, `//` et `%` (le `-` unaire n'est pas reconnu)
  * Comparateurs : `<`, `>`, `<=` et `>=` (non-associatifs)
* Type `bool` :
  * Opérations assocées : `not`,`and`,`or`
* Comparateurs `==` et `!=` sur types identiques
* Parenthésage
* Structures `while` et `if`-`elif`-`else`
* Affichage `print(var)` où `var` est du type `int` ou `bool`

## Limitations connues :

* Nombre de variables (champ .data de l'assembleur) fixé
* Entiers négatifs non/mal gérés
* Entiers sur 32 bits
* Pas d'optimisation de la compilation

## À venir ? :

* Opérateurs bit-à-bit : `<<`, `>>`, `&` et `|`
* Chaînes de caractères
* Listes (avec restrictions de type "tableau" ?)
* Fonctions

## Traitement de l'indentation :

Lors d'un premier passage, une modification du code est effectué afin d'inférer le type d'indentation utilisée et remplacer chaque indentation par une tabulation `\t`, seule reconnue. Les espaces sont ignorés.

La classe SimplyLex est un "wrapper" du lexer lex. Elle permet :
* de rajouter artificiellement les tokens `INDENT` et `DEDENT`, en particulier les `DEDENT` multiples qui, sinon, ne pourraient pas être ajoutés à la pile des tokens.
* de garder trace du code source et de la position du lexer pour chaque token rencontré, afin de pouvoir réaliser une coloration syntaxique du code.

## Structure de l'arbre syntaxique :

La racine de l'arbre est un objet de type `ASTRoot`.
