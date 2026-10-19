"""
SenseVision - Conversor Pedagógico de Matemática para Frutas
Desenvolvido especificamente para contornar barreiras de abstração da Discalculia.
Converte operações em representações concretas:
- Divisão: Frutas distribuídas para pessoinhas (ex: 🍓🍓🍓🍓 ÷ 🧒🧒 = [🧒 🍓🍓] [🧒 🍓🍓])
- Multiplicação: Cestas contendo grupos de frutas (ex: 🧺(🍎🍎) + 🧺(🍎🍎) = 🍎🍎🍎🍎)
- Adição: Junção de grupos de frutas
- Subtração: Retirada concreta de frutas de uma cesta
"""
import random
from typing import Dict, Any, Optional

FRUITS_CATALOG = [
    {"name_singular": "maçã", "name_plural": "maçãs", "emoji": "🍎", "gender": "f"},
    {"name_singular": "banana", "name_plural": "bananas", "emoji": "🍌", "gender": "f"},
    {"name_singular": "laranja", "name_plural": "laranjas", "emoji": "🍊", "gender": "f"},
    {"name_singular": "morango", "name_plural": "morangos", "emoji": "🍓", "gender": "m"},
    {"name_singular": "uva", "name_plural": "uvas", "emoji": "🍇", "gender": "f"}
]

PERSON_EMOJI = "🧒"
BASKET_EMOJI = "🧺"

class FruitMathConverter:
    """
    Tradutor de operações matemáticas abstratas para representações
    concretas e sensoriais através de grupos de frutas e personagens.
    """

    def _choose_fruit(self) -> Dict[str, str]:
        """Seleciona uma fruta aleatória do catálogo para a representação."""
        return random.choice(FRUITS_CATALOG)

    def _generate_emojis(self, count: int, emoji: str, max_display: int = 12) -> str:
        if count <= 0:
            return "∅ (nenhum)"
        if count <= max_display:
            return emoji * count
        return (emoji * 4) + f"... (+{count - 4} {emoji})"

    def solve_and_convert(self, a: int, op: str, b: int) -> Dict[str, Any]:
        """
        Calcula a expressão e retorna a estrutura pedagógica completa com pessoinhas e frutas.
        """
        fruit = self._choose_fruit()
        singular = fruit["name_singular"]
        plural = fruit["name_plural"]
        emoji = fruit["emoji"]

        # =====================================================
        # 1. DIVISÃO (Frutas divididas entre pessoinhas / amigos)
        # =====================================================
        if op in ('/', '÷', ':'):
            if b <= 0:
                return {
                    "success": False,
                    "error": "Divisão por zero não é permitida.",
                    "speech_text": "Não é possível dividir frutas por zero amigos."
                }

            result = a // b
            remainder = a % b
            op_symbol = "÷"

            # Representação visual solicitada:
            # 🍓🍓🍓🍓🍓🍓🍓🍓🍓🍓 ÷ 🧒🧒 = [🧒 🍓🍓🍓🍓🍓] [🧒 🍓🍓🍓🍓🍓]
            fruits_total_emoji = self._generate_emojis(a, emoji, max_display=12)
            people_emoji = PERSON_EMOJI * min(b, 6)
            if b > 6:
                people_emoji += f" (+{b-6})"

            # Monta cada amigo com sua porção de frutas
            each_share = self._generate_emojis(result, emoji, max_display=8)
            distribution_visual = "  ".join([f"[{PERSON_EMOJI} {each_share}]" for _ in range(min(b, 5))])
            if b > 5:
                distribution_visual += f" ... (para {b} amigos)"

            if remainder > 0:
                remainder_emoji = self._generate_emojis(remainder, emoji)
                distribution_visual += f"  +  {BASKET_EMOJI}({remainder_emoji} sobra na cesta)"

            visual_formula = f"{fruits_total_emoji}  ÷  {people_emoji}  =  {distribution_visual}"

            if remainder == 0:
                explanation_speech = (
                    f"Dividindo {a} {plural if a != 1 else singular} igualmente para {b} amigos, "
                    f"cada amigo fica com {result} {plural if result != 1 else singular}!"
                )
                pedagogical_steps = [
                    f"Frutas na mesa: {self._generate_emojis(a, emoji)} ({a} {plural})",
                    f"Amigos para receber: {people_emoji} ({b} amigos)",
                    f"Distribuição: cada amigo ganhou {self._generate_emojis(result, emoji)} ({result} {plural})"
                ]
            else:
                explanation_speech = (
                    f"Dividindo {a} {plural if a != 1 else singular} para {b} amigos, "
                    f"cada amigo fica com {result} {plural if result != 1 else singular}, "
                    f"e sobra {remainder} na cesta."
                )
                pedagogical_steps = [
                    f"Frutas na mesa: {self._generate_emojis(a, emoji)} ({a} {plural})",
                    f"Amigos para receber: {people_emoji} ({b} amigos)",
                    f"Distribuição: cada amigo ganhou {self._generate_emojis(result, emoji)} ({result} {plural})",
                    f"Sobra na cesta: {self._generate_emojis(remainder, emoji)} ({remainder} {plural if remainder != 1 else singular})"
                ]

            short_speech = f"{a} dividido para {b} amigos dá {result} {plural if result != 1 else singular} para cada."

        # =====================================================
        # 2. MULTIPLICAÇÃO (Cestas contendo grupos de frutas)
        # =====================================================
        elif op in ('*', 'x', 'X', '·'):
            result = a * b
            op_symbol = "×"

            fruits_in_basket = self._generate_emojis(b, emoji, max_display=6)
            baskets_visual = " + ".join([f"{BASKET_EMOJI}({fruits_in_basket})" for _ in range(min(a, 5))])
            if a > 5:
                baskets_visual += f" ... ({a} cestas)"

            total_fruits_visual = self._generate_emojis(result, emoji, max_display=12)
            visual_formula = f"{baskets_visual}  =  {total_fruits_visual}"

            explanation_speech = (
                f"Temos {a} cestas com {b} {plural if b != 1 else singular} dentro de cada uma. "
                f"Juntando todas as cestas, você tem no total {result} {plural if result != 1 else singular}!"
            )
            pedagogical_steps = [
                f"{a} cestas preparadas: {BASKET_EMOJI * min(a, 8)}",
                f"Cada cesta tem: {fruits_in_basket} ({b} {plural})",
                f"Total reunido: {total_fruits_visual} ({result} {plural})"
            ]
            short_speech = f"{a} vezes {b} é igual a {result} {plural if result != 1 else singular}."

        # =====================================================
        # 3. ADIÇÃO (Juntando frutas em uma mesma cesta)
        # =====================================================
        elif op == '+':
            result = a + b
            op_symbol = "+"

            group_a = self._generate_emojis(a, emoji, max_display=10)
            group_b = self._generate_emojis(b, emoji, max_display=10)
            group_total = self._generate_emojis(result, emoji, max_display=15)

            visual_formula = f"{group_a}  +  {group_b}  =  {group_total}"

            explanation_speech = (
                f"Você tem {a} {plural if a != 1 else singular} e ganhou mais {b} {plural if b != 1 else singular}. "
                f"Juntando todas na cesta, agora você tem {result} {plural if result != 1 else singular}!"
            )
            pedagogical_steps = [
                f"Primeiro grupo: {group_a} ({a})",
                f"Segundo grupo adicionado: {group_b} ({b})",
                f"Cesta completa: {group_total} ({result} {plural})"
            ]
            short_speech = f"{a} mais {b} é igual a {result}."

        # =====================================================
        # 4. SUBTRAÇÃO (Retirando frutas de uma cesta)
        # =====================================================
        elif op == '-':
            result = a - b
            op_symbol = "-"

            group_a = self._generate_emojis(a, emoji, max_display=10)
            group_b = self._generate_emojis(b, emoji, max_display=10)
            group_res = self._generate_emojis(max(0, result), emoji, max_display=12)

            visual_formula = f"{group_a}  -  ({group_b} retirados)  =  {group_res}"

            if result > 0:
                explanation_speech = (
                    f"Você tinha {a} {plural if a != 1 else singular} na cesta e comeu ou retirou {b}. "
                    f"Sobraram {result} {plural if result != 1 else singular}!"
                )
            elif result == 0:
                explanation_speech = (
                    f"Você tinha {a} {plural if a != 1 else singular} e tirou todas as {b}. "
                    f"A cesta ficou vazia!"
                )
            else:
                explanation_speech = (
                    f"Você só tem {a} {plural if a != 1 else singular}, mas precisa tirar {b}. "
                    f"Faltam {abs(result)} {plural if abs(result) != 1 else singular} para conseguir!"
                )

            pedagogical_steps = [
                f"Você começou com: {group_a} ({a} {plural})",
                f"Frutas retiradas: {group_b} ({b} {plural})",
                f"O que sobrou na cesta: {group_res} ({result} {plural})"
            ]
            short_speech = f"{a} menos {b} é igual a {result}."

        else:
            return {
                "success": False,
                "error": f"Operador desconhecido: {op}",
                "speech_text": "Não reconheci esta operação matemática."
            }

        math_expression = f"{a} {op_symbol} {b} = {result}"

        return {
            "success": True,
            "operand_a": a,
            "operator": op_symbol,
            "operand_b": b,
            "result": result,
            "math_expression": math_expression,
            "fruit": fruit,
            "visual_formula": visual_formula,
            "pedagogical_steps": pedagogical_steps,
            "short_speech": short_speech,
            "explanation_speech": explanation_speech,
            "audio_full_narration": f"{short_speech} {explanation_speech}"
        }
