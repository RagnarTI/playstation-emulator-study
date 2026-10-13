[Glossario](Glossario.md)

# Tema 1 — Fundamentos dos bits

## O que é um bit?
Um bit é a menor unidade de informação binária e pode assumir dois valores: 0 ou 1.

## O que é um octeto?
Um octeto é um conjunto de 8 bits. Ele pode representar 256 combinações diferentes, de 0 a 255, quando interpretado como um número sem sinal.

## Valores posicionais
Da direita para a esquerda, os valores são 1, 2, 4, 8, 16, 32, 64 e 128.

Cada posição representa uma potência de 2.

## Exemplo
00001101 = 8 + 4 + 1 = 13.

Para converter binário em decimal, some os valores das posições que contêm 1.

## Python
```python
numero = 13
print(bin(numero))
print(format(numero, '08b'))
```