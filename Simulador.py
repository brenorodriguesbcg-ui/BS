import ipywidgets as widgets
from IPython.display import display

# Fator calibrado com precisão cirúrgica para que 100k resulte em exatos R$ 341,50 de meia parcela
FATOR_TABELA = 0.006830

# Criando a área onde o resultado será impresso de forma estável no Colab
zona_resultado = widgets.Output()

def calcular_e_exibir(change=None):
    # Pega os valores digitados nas caixas de texto
    credito_nominal = credito_input.value
    entrada_bolso = entrada_box.value
    usar_embutido = embutido_check.value
    
    # 1. Cálculos de Parcelas Originais
    parcela_integral_original = credito_nominal * FATOR_TABELA
    meia_parcela = parcela_integral_original * 0.50
    
    # 2. Regra do Lance Embutido Condicional
    if usar_embutido:
        lance_embutido = credito_nominal * 0.30
        credito_liquido = credito_nominal - lance_embutido
        proporcao_abatimento_embutido = 0.70  # reduz 30% da parcela pelo embutido
    else:
        lance_embutido = 0.0
        credito_liquido = credito_nominal  # Pega o crédito 100% cheio
        proporcao_abatimento_embutido = 1.0   # sem abatimento inicial pelo embutido
        
    lance_total = lance_embutido + entrada_bolso
    
    # 3. Pós-Contemplação: Recálculo do Saldo Devedor com desconto do Embutido + Entrada do Bolso
    saldo_total_com_taxas = parcela_integral_original * 180
    saldo_devedor_pos_embutido = saldo_total_com_taxas * proporcao_abatimento_embutido
    
    # Deduz o valor que o cliente colocou do bolso do saldo devedor
    saldo_devedor_final = max(0.0, saldo_devedor_pos_embutido - entrada_bolso)
    nova_parcela_integral = saldo_devedor_final / 180
    
    # 4. Projeções de Rentabilização (Baseado no crédito líquido real do ativo)
    aluguel_estimado = credito_liquido * 0.007
    sobra_imovel = aluguel_estimado - nova_parcela_integral
    
    rendimento_rf = credito_liquido * 0.0095
    sobra_rf = rendimento_rf - nova_parcela_integral
    
    # Atualiza a área de texto do resultado de forma limpa e em tempo real
    with zona_resultado:
        zona_resultado.clear_output(wait=True)
        print("=" * 65)
        print("        SIMULADOR BASIS CAPITAL - ENGENHARIA FINANCEIRA       ")
        print("=" * 65)
        print(f"📉 FASE DE CARREGAMENTO (PRÉ-CONTEMPLAÇÃO):")
        print(f"  • BOLETO DE ESPERA (MEIA PARCELA): R$ {meia_parcela:,.2f} / mês")
        print(f"  • Parcela Integral Original:       R$ {parcela_integral_original:,.2f} / mês")
        print("-" * 65)
        print(f"🔑 MOMENTO DA CONTEMPLAÇÃO (ESTRATÉGIA DE LANCE):")
        print(f"  • Lance Embutido (30%):             R$ {lance_embutido:,.2f}")
        print(f"  • Entrada / Aporte do Bolso:        R$ {entrada_bolso:,.2f}")
        print(f"  • LANCE TOTAL P/ ASSEMBLEIA:       R$ {lance_total:,.2f} ({((lance_total/credito_nominal)*100):.1f}% do Grupo)")
        print(f"  🎯 CRÉDITO LÍQUIDO DISPONÍVEL:     R$ {credito_liquido:,.2f}")
        print("-" * 65)
        print(f"🏢 ALAVANCAGEM PÓS-CONTEMPLAÇÃO:")
        print(f"  • Nova Parcela Recalculada:        R$ {nova_parcela_integral:,.2f} / mês")
        print("\n  💼 Cenário A: Imóvel (Aluguel estimado a 0.7% a.m.)")
        print(f"    - Renda do Aluguel:              R$ {aluguel_estimado:,.2f} / mês")
        if sobra_imovel >= 0:
            print(f"    - 🎉 SOBRA MENSAL NO BOLSO:      + R$ {sobra_imovel:,.2f} / mês")
        else:
            print(f"    - 📉 ESFORÇO LÍQUIDO REAL:        - R$ {abs(sobra_imovel):,.2f} / mês")
            
        print("\n  📈 Cenário B: Renda Fixa / FIIs (Estimado a 0.95% a.m. líquido)")
        print(f"    - Rendimento Mensal Isento:      R$ {rendimento_rf:,.2f} / mês")
        if sobra_rf >= 0:
            print(f"    - 🎉 SOBRA MENSAL NO BOLSO:      + R$ {sobra_rf:,.2f} / mês")
        else:
            print(f"    - 📉 ESFORÇO LÍQUIDO REAL:        - R$ {abs(sobra_rf):,.2f} / mês")
        print("=" * 65)

# Criando as caixas de texto e seleção interativas do Colab (Sem barras deslizantes)
credito_input = widgets.IntText(value=100000, description='Crédito R$:', continuous_update=False)
entrada_box = widgets.IntText(value=0, description='Aporte Bolso:', continuous_update=False)
embutido_check = widgets.Checkbox(value=True, description='Utilizar Lance Embutido (30%)')

# Vincula a função para rodar e atualizar os cálculos sempre que mudar o valor digitado
credito_input.observe(calcular_e_exibir, names='value')
entrada_box.observe(calcular_e_exibir, names='value')
embutido_check.observe(calcular_e_exibir, names='value')

# Organiza o layout dos campos na tela
ui = widgets.VBox([credito_input, entrada_box, embutido_check])
display(ui, zona_resultado)

# Inicializa o cálculo na abertura para mostrar os dados corretos de largada
calcular_e_exibir()