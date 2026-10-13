[Glossario](Glossario.md)

# Tema 3 — Máscaras com AND

Uma máscara é um valor binário usado para selecionar ou modificar posições específicas de outro número.

## Verificar um bit
Para verificar o bit de valor 4, use a máscara 00000100.

```python
numero = 13
mascara = 4
resultado = numero & mascara
print(resultado)  # 4
```

Se o resultado for diferente de zero, o bit selecionado está ligado. Se for zero, está desligado.

## Exemplo com bit desligado
```python
numero = 9       # 00001001
mascara = 2      # 00000010
print(numero & mascara)  # 0
```

O bit de valor 2 está desligado em 9.

Essa regra é direta quando a máscara seleciona apenas um bit.