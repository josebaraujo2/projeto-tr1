import unittest
from detecao_erro import calcular_paridade, verificar_paridade, calcular_crc, verificar_crc
from correcao_erro import gerar_hamming, corrigir_hamming

class TestErroProtocolos(unittest.TestCase):
    def test_paridade_par(self):
        # Teste sem erro
        bits = '1010101'
        bits_com_paridade = calcular_paridade(bits)
        self.assertTrue(verificar_paridade(bits_com_paridade))
        
        # Teste com erro
        bits_com_erro = bits_com_paridade[:-1] + ('0' if bits_com_paridade[-1] == '1' else '1')
        self.assertFalse(verificar_paridade(bits_com_erro))

    def test_crc(self):
        # CRC-32 (IEEE 802)
        polinomio = '100000100110000010001110110110111'
        bits = '1010110011'
        bits_com_crc = calcular_crc(bits, polinomio)
        self.assertTrue(verificar_crc(bits_com_crc, polinomio))
        
        # Teste com erro
        bits_com_erro = bits_com_crc[:-1] + ('0' if bits_com_crc[-1] == '1' else '1')
        self.assertFalse(verificar_crc(bits_com_erro, polinomio))

    def test_hamming(self):
        # Teste sem erro
        bits_originais = '1011'
        hamming = gerar_hamming(bits_originais)
        corrigido = corrigir_hamming(hamming)
        self.assertEqual(hamming, corrigido)
        
        # Teste com erro em bit específico
        hamming_com_erro = list(hamming)
        hamming_com_erro[2] = '0' if hamming_com_erro[2] == '1' else '1'
        hamming_com_erro = ''.join(hamming_com_erro)
        corrigido = corrigir_hamming(hamming_com_erro)
        self.assertNotEqual(hamming_com_erro, corrigido)

if __name__ == '__main__':
    unittest.main()