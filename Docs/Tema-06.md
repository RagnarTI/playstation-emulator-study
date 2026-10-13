[Glossario](Glossario.md)

# Tema 6 — Máscaras com XOR

XOR (^) permite alternar um bit específico.

- XOR com 0 mantém o bit.
- XOR com 1 inverte o bit.

Exemplo: inverter o bit de valor 4 no número 9.

```python
numero = 9       # 00001001
mascara = 4      # 00000100
resultado = numero ^ mascara
print(resultado)  # 13
```

Resultado binário: 00001101.

Se aplicarmos a mesma máscara novamente, o bit volta ao estado original:

```python
resultado = resultado ^ mascara
print(resultado)  # 9
```

## Uso comum
Alternar estados, sinalizadores e opções representadas por bits.