[Glossario](Glossario.md)

# Tema 4 — Máscaras com OR

OR (|) pode ser usado para ligar um bit específico sem desligar os outros.

Exemplo: ligar o bit de valor 2 no número 9.

```python
numero = 9       # 00001001
mascara = 2      # 00000010
resultado = numero | mascara
print(resultado)  # 11
```

Resultado binário: 00001011.

## Regra
- Máscara com 1: o bit resultante fica ligado.
- Máscara com 0: o bit original é preservado.

Se o bit já estava ligado, o valor não muda.