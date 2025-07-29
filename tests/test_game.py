from app.game import Baralho

def test_baralho_tem_108_cartas():
    b = Baralho()
    assert len(b.cartas) == 108

def test_baralho_comprar_carta():
    b = Baralho()
    carta = b.comprar()
    assert carta is not None
    assert isinstance(carta.cor, str)
    assert isinstance(carta.valor, str)
