import os
import unittest

RAIZ_PROJETO = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_TESTES = os.path.join(RAIZ_PROJETO, "test")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(
        start_dir=DIRETORIO_TESTES,
        pattern="test_*.py",
        top_level_dir=RAIZ_PROJETO,
    )

    resultado = unittest.TextTestRunner(verbosity=2).run(suite)

    if not resultado.wasSuccessful():
        raise SystemExit(1)
