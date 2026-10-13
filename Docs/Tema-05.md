[Glossario](Glossario.md)

# Tema 5 — Desligar bits com AND e NOT

Para desligar um bit, use uma máscara que tenha 0 na posição desejada e 1 nas demais posições.

Exemplo em um octeto: desligar o bit de valor 2 no número 11.

Número: 00001011
Máscara invertida: 11111101
Resultado: 00001001 = 9

```python
numero = 11
mascara = 2
resultado = numero & (~mascara & 0xFF)
print(resultado)  # 9
```

O `0xFF` limita a operação a 8 bits neste exemplo.

## Regra
AND com 0 desliga a posição; AND com 1 preserva o bit original.