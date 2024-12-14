import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Classe para representar um Gasto
class Gasto:
    def __init__(self, descricao, categoria, valor, data):
        self.descricao = descricao
        self.categoria = categoria
        self.valor = valor
        self.data = datetime.strptime(data, '%d/%m/%Y')

    def to_dict(self):
        return {
            "Descrição": self.descricao,
            "Categoria": self.categoria,
            "Valor (R$)": self.valor,
            "Data": self.data.strftime('%d/%m/%Y')
        }

# Classe para gerenciar a planilha de gastos
class PlanilhaGastos:
    def __init__(self):
        self.gastos = []

    def adicionar_gasto(self, descricao, categoria, valor, data):
        gasto = Gasto(descricao, categoria, valor, data)
        self.gastos.append(gasto)
        print("Gasto adicionado com sucesso!")

    def gerar_dataframe(self):
        dados = [gasto.to_dict() for gasto in self.gastos]
        return pd.DataFrame(dados)

    def calcular_total(self):
        return sum(gasto.valor for gasto in self.gastos)

    def calcular_gastos_por_categoria(self):
        df = self.gerar_dataframe()
        return df.groupby("Categoria")["Valor (R$)"].sum()

    def filtrar_por_mes(self, mes, ano):
        df = self.gerar_dataframe()
        df["Data"] = pd.to_datetime(df["Data"], format='%d/%m/%Y')
        return df[(df["Data"].dt.month == mes) & (df["Data"].dt.year == ano)]

    def filtrar_por_semana(self, semana, ano):
        df = self.gerar_dataframe()
        df["Data"] = pd.to_datetime(df["Data"], format='%d/%m/%Y')
        inicio_semana = datetime.strptime(f'{ano}-W{semana - 1}-1', "%Y-W%U-%w")
        fim_semana = inicio_semana + timedelta(days=6)
        return df[(df["Data"] >= inicio_semana) & (df["Data"] <= fim_semana)]

    def salvar_excel(self, filename="planilha_gastos.xlsx"):
        df = self.gerar_dataframe()
        df.to_excel(filename, index=False)
        print(f"Planilha salva como '{filename}'")

    def gerar_grafico_pizza(self):
        df_categoria = self.calcular_gastos_por_categoria()
        plt.figure(figsize=(8, 8))
        df_categoria.plot.pie(y="Valor (R$)", autopct='%1.1f%%', startangle=90, legend=False)
        plt.title("Distribuição dos Gastos por Categoria")
        plt.ylabel('')
        plt.show()

    def gerar_grafico_barras(self):
        df_categoria = self.calcular_gastos_por_categoria()
        df_categoria.plot(kind='bar', color='skyblue', figsize=(10, 6))
        plt.title("Gastos por Categoria")
        plt.xlabel("Categoria")
        plt.ylabel("Valor (R$)")
        plt.xticks(rotation=45)
        plt.show()

    def gerar_relatorio_pdf(self, filename="relatorio_gastos.pdf"):
        c = canvas.Canvas(filename, pagesize=letter)
        c.drawString(100, 750, f"Relatório de Gastos - {datetime.now().strftime('%d/%m/%Y')}")
        
        # Total de gastos
        c.drawString(100, 730, f"Total de Gastos: R$ {self.calcular_total():.2f}")
        
        # Gastos por categoria
        y_position = 710
        c.drawString(100, y_position, "Gastos por Categoria:")
        y_position -= 20
        for categoria, valor in self.calcular_gastos_por_categoria().items():
            c.drawString(100, y_position, f"{categoria}: R$ {valor:.2f}")
            y_position -= 20
        
        # Gerar gráfico de pizza e salvar em arquivo temporário
        self.gerar_grafico_pizza()
        plt.savefig("grafico_pizza.png")
        c.drawImage("grafico_pizza.png", 100, y_position, width=400, height=300)

        c.save()
        print(f"Relatório PDF salvo como '{filename}'")

# Função principal para execução do programa
def main():
    planilha = PlanilhaGastos()
    
    while True:
        descricao = input("Descrição do gasto: ")
        categoria = input("Categoria do gasto: ")
        valor = float(input("Valor do gasto: R$ "))
        data = input("Data do gasto (DD/MM/AAAA): ")
        
        planilha.adicionar_gasto(descricao, categoria, valor, data)
        
        continuar = input("Deseja adicionar outro gasto? (s/n): ")
        if continuar.lower() != 's':
            break

    # Exibir resumo dos gastos
    print("\nResumo dos Gastos")
    print("Total: R$", planilha.calcular_total())
    print("Gastos por Categoria:")
    print(planilha.calcular_gastos_por_categoria())

    # Salvar dados em Excel
    planilha.salvar_excel()

    # Gerar gráficos
    print("\nGerando gráficos...")
    planilha.gerar_grafico_pizza()
    planilha.gerar_grafico_barras()

    # Gerar relatório em PDF
    print("\nGerando relatório em PDF...")
    planilha.gerar_relatorio_pdf()

if __name__ == "__main__":
    main()
