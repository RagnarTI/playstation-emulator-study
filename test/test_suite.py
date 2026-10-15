import os
import unittest


if __name__ == "__main__":
    pasta_testes = os.path.dirname(os.path.abspath(__file__))

    suite = unittest.defaultTestLoader.discover(
        start_dir=pasta_testes,
        pattern="test_*.py",
    )

    resultado = unittest.TextTestRunner(verbosity=2).run(suite)

    if not resultado.wasSuccessful():
        raise SystemExit(1)