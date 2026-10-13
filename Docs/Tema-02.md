[Glossario](Glossario.md)

# Tema 2 — Operadores bit a bit

## AND (&)
O resultado de cada posição é 1 somente quando os dois bits são 1.

```python
12 & 10  # 8
```

## OR (|)
O resultado de cada posição é 1 quando pelo menos um dos bits é 1.

```python
12 | 10  # 14
```

## XOR (^)
O resultado de cada posição é 1 quando os bits são diferentes.

```python
12 ^ 10  # 6
```

XOR com 1 inverte o bit; XOR com 0 mantém o bit.

## NOT (~)
Inverte os bits de acordo com a representação inteira da linguagem.

Em Python, `~n` equivale a `-n - 1`. Para limitar o resultado a 8 bits, use `(~n) & 0xFF`.

## Atenção
Em Python, `and` combina condições lógicas, enquanto `&` realiza AND bit a bit. São operadores diferentes.