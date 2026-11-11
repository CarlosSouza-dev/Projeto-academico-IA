"""Testes do projeto (só biblioteca padrão).

Rode, a partir da raiz do repositório, com:
    python -m unittest discover -s src -v
(o pytest, se você usar, também encontra estes testes)
"""
import itertools
import unittest

from mapas import MAPA_GRANDE, MAPA_MEDIO, MAPA_PEQUENO, validar_mapa
from buscas import (
    _busca_melhor_primeiro, a_estrela, busca_custo_uniforme,
    calibrar_escala_heuristica, custo_do_caminho, distancia_direta, heuristica_hdd,
)
from trechos import (
    TRECHOS, Trecho, chave_trecho, fator_transito, gerar_dataset_sintetico,
    montar_grafo_tempo, tempo_trecho,
)

MAPAS = {"pequeno": MAPA_PEQUENO, "medio": MAPA_MEDIO, "grande": MAPA_GRANDE}
HORAS = [3, 8, 12, 18, 22]


def hdd_consistente(grafo, escala):
    """h(a) <= c(a,b) + h(b) para toda aresta e qualquer objetivo."""
    for obj in grafo:
        for a, viz in grafo.items():
            for b, c in viz.items():
                if heuristica_hdd(a, obj, escala) > c + heuristica_hdd(b, obj, escala) + 1e-9:
                    return False
    return True


class TestMapas(unittest.TestCase):
    def test_mapas_integros(self):
        for nome, m in MAPAS.items():
            with self.subTest(mapa=nome):
                self.assertEqual(validar_mapa(m), [])

    def test_pequeno_e_medio_sao_subconjuntos_do_grande(self):
        for m in (MAPA_PEQUENO, MAPA_MEDIO):
            for a, viz in m.items():
                for b, d in viz.items():
                    self.assertEqual(MAPA_GRANDE[a][b], d)


class TestHeuristica(unittest.TestCase):
    def test_hdd_calibrada_consistente_na_distancia(self):
        for nome, g in MAPAS.items():
            with self.subTest(mapa=nome):
                self.assertTrue(hdd_consistente(g, calibrar_escala_heuristica(g)))

    def test_divisor_10_antigo_era_inconsistente(self):
        """Documenta o bug original: dist/10 viola a consistência (Saffron-Celadon)."""
        self.assertFalse(hdd_consistente(MAPA_GRANDE, 0.1))

    def test_hdd_calibrada_consistente_no_tempo(self):
        for hora in HORAS:
            with self.subTest(hora=hora):
                g = montar_grafo_tempo(MAPA_GRANDE, hora)
                self.assertTrue(hdd_consistente(g, calibrar_escala_heuristica(g)))

    def test_erro_sem_coordenada(self):
        with self.assertRaises(KeyError):
            distancia_direta("Cianwood City", "Cidade Fantasma")


class TestBusca(unittest.TestCase):
    def test_astar_igual_ucs_em_todos_os_pares_distancia(self):
        for nome, g in MAPAS.items():
            escala = calibrar_escala_heuristica(g)
            for o, d in itertools.permutations(g, 2):
                with self.subTest(mapa=nome, origem=o, destino=d):
                    cam_u, c_u, _, _ = busca_custo_uniforme(o, d, g)
                    cam_a, c_a, _, _ = a_estrela(o, d, g, escala)
                    self.assertAlmostEqual(c_a, c_u)
                    self.assertEqual((cam_a[0], cam_a[-1]), (o, d))
                    self.assertAlmostEqual(custo_do_caminho(cam_a, g), c_a)

    def test_astar_igual_ucs_em_todos_os_pares_tempo(self):
        for hora in HORAS:
            g = montar_grafo_tempo(MAPA_GRANDE, hora, acidentes=[("Mahogany Town", "Ice Path")])
            escala = calibrar_escala_heuristica(g)
            for o, d in itertools.permutations(g, 2):
                with self.subTest(hora=hora, origem=o, destino=d):
                    self.assertAlmostEqual(
                        a_estrela(o, d, g, escala)[1], busca_custo_uniforme(o, d, g)[1]
                    )

    def test_astar_expande_menos_ou_igual_que_ucs(self):
        _, _, n_u, _ = busca_custo_uniforme("Cianwood City", "Cinnabar Island", MAPA_GRANDE)
        _, _, n_a, _ = a_estrela("Cianwood City", "Cinnabar Island", MAPA_GRANDE)
        self.assertLessEqual(n_a, n_u)

    def test_origem_igual_destino(self):
        self.assertEqual(a_estrela("Pallet Town", "Pallet Town", MAPA_GRANDE)[:3],
                         (["Pallet Town"], 0, 0))

    def test_cidade_inexistente(self):
        with self.assertRaises(ValueError):
            a_estrela("Cianwood City", "Cidade Fantasma", MAPA_PEQUENO)

    def test_destino_inalcancavel(self):
        cam, custo, _, _ = busca_custo_uniforme("A", "B", {"A": {}, "B": {}})
        self.assertIsNone(cam)
        self.assertIsNone(custo)

    def test_reabre_no_quando_heuristica_e_inconsistente(self):
        """Heurística admissível porém inconsistente: o laço antigo (conjunto
        de explorados) devolvia rota subótima; o `melhor_g` acerta."""
        g = {
            "S": {"A": 1, "B": 1},
            "A": {"S": 1, "C": 1},
            "B": {"S": 1, "C": 3},
            "C": {"A": 1, "B": 3, "G": 20},
            "G": {"C": 20},
        }
        h = {"S": 0, "A": 18, "B": 0, "C": 0, "G": 0}
        cam, custo, _, _ = _busca_melhor_primeiro("S", "G", g, lambda e: h[e])
        self.assertEqual((custo, cam), (22, ["S", "A", "C", "G"]))


class TestCustosFase2(unittest.TestCase):
    def test_todas_as_estradas_tem_caracteristicas(self):
        for a, viz in MAPA_GRANDE.items():
            for b in viz:
                self.assertIn(chave_trecho(a, b), TRECHOS)

    def test_grafo_de_tempo_simetrico_e_positivo(self):
        g = montar_grafo_tempo(MAPA_GRANDE, 18)
        for a, viz in g.items():
            for b, t in viz.items():
                self.assertGreater(t, 0)
                self.assertEqual(g[b][a], t)

    def test_transito_de_pico(self):
        self.assertAlmostEqual(fator_transito(3), 1.0, delta=0.01)
        self.assertGreater(fator_transito(18), 1.8)
        self.assertGreater(fator_transito(8), 1.6)

    def test_cada_obstaculo_aumenta_o_tempo(self):
        base = Trecho(50, 0, 0, "asfalto")
        t0 = tempo_trecho(base, 12)
        self.assertGreater(tempo_trecho(Trecho(50, 3, 0, "asfalto"), 12), t0)
        self.assertGreater(tempo_trecho(Trecho(50, 0, 3, "asfalto"), 12), t0)
        self.assertGreater(tempo_trecho(base, 12, acidente=True), t0)
        self.assertGreater(tempo_trecho(base, 18), t0)
        paralelo = tempo_trecho(Trecho(50, 0, 0, "paralelepipedo"), 12)
        self.assertGreater(paralelo, t0)
        self.assertGreater(tempo_trecho(Trecho(50, 0, 0, "obras"), 12), paralelo)

    def test_acidente_so_afeta_o_trecho_informado(self):
        livre = montar_grafo_tempo(MAPA_GRANDE, 12)
        acid = montar_grafo_tempo(MAPA_GRANDE, 12, acidentes=[("Ice Path", "Mahogany Town")])
        mudou = {(a, b) for a in livre for b in livre[a] if livre[a][b] != acid[a][b]}
        self.assertEqual(mudou, {("Ice Path", "Mahogany Town"), ("Mahogany Town", "Ice Path")})

    def test_modelo_aprendido_pluga_no_grafo(self):
        g = montar_grafo_tempo(MAPA_PEQUENO, 12, prever=lambda t, h, a: t.distancia)
        self.assertEqual(g["Cianwood City"]["Whirl Islands"], 15)

    def test_dataset_reprodutivel(self):
        a = gerar_dataset_sintetico(n_por_trecho=3)
        self.assertEqual(a, gerar_dataset_sintetico(n_por_trecho=3))
        self.assertEqual(len(a), 3 * len(TRECHOS))
        self.assertTrue(all(r["tempo_min"] > 0 for r in a))


if __name__ == "__main__":
    unittest.main(verbosity=2)
