import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check
from pathlib import Path
from datetime import datetime
import re
from typing import Tuple


def _calcular_digito_verificador(cpf_parcial: str) -> int:
    """
    Calcula o dígito verificador do CPF.

    """
    soma = 0
    for i, digito in enumerate(cpf_parcial):
        soma += int(digito) * (len(cpf_parcial) + 1 - i)
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def validar_cpf_individual(cpf: str) -> bool:
    """
    Valida um CPF brasileiro individual.

    """
    # Rejeita valores nulos ou vazios
    cpf_str = str(cpf).strip()
    if pd.isna(cpf) or cpf_str == '' or cpf_str == 'nan':
        return False
    
    # Remove caracteres não numéricos
    cpf_limpo = re.sub(r'\D', '', cpf_str)
    
    # CPF deve ter 11 dígitos
    if len(cpf_limpo) != 11:
        return False
    
    # CPFs com todos os dígitos iguais são inválidos
    if cpf_limpo == cpf_limpo[0] * 11:
        return False
    
    # Valida primeiro dígito verificador
    digito1 = _calcular_digito_verificador(cpf_limpo[:9])
    if digito1 != int(cpf_limpo[9]):
        return False
    
    # Valida segundo dígito verificador
    digito2 = _calcular_digito_verificador(cpf_limpo[:10])
    if digito2 != int(cpf_limpo[10]):
        return False
    
    return True


def validar_cpf(serie: pd.Series) -> pd.Series:
    """
    Valida uma série de CPFs.

    """
    return serie.apply(validar_cpf_individual)


def validar_email_individual(email: str) -> bool:
    """
    Valida um endereço de email individual.

    """
    # Rejeita valores nulos ou vazios
    if pd.isna(email) or str(email).strip() == '' or str(email).strip() == 'nan':
        return False
    
    # Padrão básico de validação de email
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, str(email)))


def validar_email(serie: pd.Series) -> pd.Series:
    """
    Valida uma série de emails.

    """
    return serie.apply(validar_email_individual)


# Definir o schema de validação usando Pandera
schema = DataFrameSchema(
    {
        "nome": Column(
            str,
            checks=[
                Check.str_length(min_value=1, max_value=255),
            ],
            nullable=False,
            coerce=True,
            description="Nome completo do cliente"
        ),
        "cpf": Column(
            str,
            checks=[
                Check(validar_cpf, error="CPF inválido")
            ],
            nullable=False,  # CPF is required
            coerce=True,
            description="CPF do cliente (com ou sem formatação)"
        ),
        "email": Column(
            str,
            checks=[
                Check(validar_email, error="Email inválido")
            ],
            nullable=False,  # Email is required
            coerce=True,
            description="Email do cliente"
        ),
        "valor_contrato": Column(
            float,
            checks=[
                Check.greater_than_or_equal_to(0, error="Valor do contrato não pode ser negativo")
            ],
            nullable=False,
            coerce=True,
            description="Valor do contrato em reais"
        ),
        "idade": Column(
            int,
            checks=[
                Check.greater_than_or_equal_to(1, error="Idade deve ser maior ou igual a 1"),
                Check.less_than_or_equal_to(150, error="Idade deve ser menor ou igual a 100 anos")
            ],
            nullable=False,
            coerce=True,
            description="Idade do cliente"
        )
    },
    strict=False,
    coerce=True
)


def gerar_relatorio_erros(erros: pd.DataFrame, arquivo_saida: str) -> None:
    """
    Gera um relatório de erros em formato texto.

    """
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RELATÓRIO DE ERROS - VALIDAÇÃO DE DADOS DE CLIENTES\n")
        f.write("=" * 80 + "\n")
        f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Total de erros: {len(erros)}\n")
        f.write("=" * 80 + "\n\n")
        
        # Agrupar erros por linha
        for idx, grupo in erros.groupby('index'):
            f.write(f"\n{'─' * 80}\n")
            f.write(f"LINHA {idx + 2}\n")  # +2 porque: +1 para índice começar em 1, +1 para header
            f.write(f"{'─' * 80}\n")
            
            for _, erro in grupo.iterrows():
                f.write(f"\n  Campo: {erro['column']}\n")
                f.write(f"  Erro: {erro['check']}\n")
                if pd.notna(erro.get('failure_case')):
                    f.write(f"  Valor: {erro['failure_case']}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("FIM DO RELATÓRIO\n")
        f.write("=" * 80 + "\n")


def validar_dados(arquivo_entrada: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Valida os dados do arquivo Excel.

    """
    print(f"\n{'=' * 80}")
    print("INICIANDO VALIDAÇÃO DE DADOS")
    print(f"{'=' * 80}\n")
    
    # Ler arquivo Excel
    print(f"Lendo arquivo: {arquivo_entrada}")
    df = pd.read_excel(arquivo_entrada, engine='openpyxl')
    print(f"Arquivo lido com sucesso: {len(df)} registros encontrados\n")
    
    # Validar usando Pandera
    print("Iniciando validação dos dados...\n")
    
    try:
        # Tentar validar todo o DataFrame
        dados_validados = schema.validate(df, lazy=True)
        print("Todos os dados são válidos!")
        return dados_validados, pd.DataFrame()
        
    except pa.errors.SchemaErrors as e:
        print(f"Foram encontrados erros nos dados\n")
        
        # Obter DataFrame com os erros
        erros_df = e.failure_cases
        
        # Filtrar erros que têm índice válido
        erros_df = erros_df[erros_df['index'].notna()]
        
        print(f"Total de erros de validação: {len(erros_df)}\n")
        
        # Identificar linhas com erros
        linhas_com_erro = set(erros_df['index'].unique())
        print(f"Linhas com erros: {sorted(linhas_com_erro)}\n")
        
        # Separar dados válidos dos inválidos
        dados_validos = df[~df.index.isin(linhas_com_erro)]
        
        print(f"Registros válidos: {len(dados_validos)}")
        print(f"Registros inválidos: {len(linhas_com_erro)}\n")
        
        return dados_validos, erros_df


def main():
    """Função principal do script."""
    # Definir caminhos
    base_path = Path(__file__).parent
    arquivo_entrada = base_path / 'dados_clientes.xlsx'
    arquivo_relatorio = base_path / f'relatorio_erros_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    arquivo_saida_validos = base_path / 'dados_clientes_validos.xlsx'
    
    # Verificar se arquivo de entrada existe
    if not arquivo_entrada.exists():
        print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado!")
        print("Execute primeiro o script 'gerar_dados_exemplo.py' para criar o arquivo de exemplo.")
        return
    
    # Validar dados
    dados_validos, erros = validar_dados(str(arquivo_entrada))
    
    # Se houver erros, gerar relatório
    if not erros.empty:
        print(f"\nGerando relatório de erros...")
        gerar_relatorio_erros(erros, str(arquivo_relatorio))
        print(f"Relatório salvo em: {arquivo_relatorio}\n")
        
        # Exibir resumo dos erros
        print("RESUMO DOS ERROS POR TIPO:")
        print("─" * 80)
        resumo = erros.groupby('column').size().sort_values(ascending=False)
        for campo, quantidade in resumo.items():
            print(f"  • {campo}: {quantidade} erro(s)")
        print()
    
    # Salvar dados válidos
    if not dados_validos.empty:
        dados_validos.to_excel(arquivo_saida_validos, index=False, engine='openpyxl')
        print(f"Dados válidos salvos em: {arquivo_saida_validos}")
        print(f"   Total de registros válidos: {len(dados_validos)}\n")
    else:
        print("Nenhum registro válido foi encontrado!\n")
    
    print(f"{'=' * 80}")
    print("VALIDAÇÃO CONCLUÍDA")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
