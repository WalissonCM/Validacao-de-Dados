# 🔍 Validação de Dados para Importação de Clientes 

Sistema de validação de dados para importação segura de informações de clientes. Este projeto demonstra como evitar que dados inconsistentes ou inválidos entrem no banco de dados através de validações robustas.

## 📋 Descrição

Este projeto implementa um script Python que:
- ✅ Valida dados de clientes antes da importação para o ERP
- ✅ Verifica CPFs brasileiros (com algoritmo de validação completo)
- ✅ Valida endereços de email
- ✅ Garante que valores monetários e numéricos sejam não-negativos
- ✅ Gera relatórios detalhados de erros encontrados
- ✅ Separa dados válidos dos inválidos para processamento correto

## 🎯 O que este projeto demonstra

- **Validação de Dados**: Implementação de regras de negócio para garantir qualidade dos dados
- **Prevenção de Erros**: Evita que "lixo" entre no banco de dados
- **Relatórios**: Geração automática de relatórios de erros para correção
- **Tratamento de Dados Reais**: Simulação de cenário real de importação de dados

## Analisar os Resultados

O script irá:
- Ler o arquivo `dados_clientes.xlsx`
- Validar todos os campos conforme as regras definidas
- Gerar um relatório de erros (se houver): `relatorio_erros_YYYYMMDD_HHMMSS.txt`
- Salvar os dados válidos em: `dados_clientes_validos.xlsx`

## 📊 Estrutura dos Dados

O arquivo Excel deve conter as seguintes colunas:

| Campo | Tipo | Validações |
|-------|------|-----------|
| `nome` | String | Obrigatório, 1-255 caracteres |
| `cpf` | String | Obrigatório, CPF válido (com ou sem formatação) |
| `email` | String | Obrigatório, formato de email válido |
| `valor_contrato` | Float | Obrigatório, maior ou igual a 0 |
| `idade` | Integer | Obrigatório, entre 1 e 150 anos |

## 🔍 Regras de Validação

### CPF
- ✅ Aceita formatação: `123.456.789-09` ou `12345678909`
- ✅ Valida dígitos verificadores
- ❌ Rejeita CPFs com todos os dígitos iguais (`111.111.111-11`)
- ❌ Rejeita CPFs com tamanho incorreto

### Email
- ✅ Formato padrão: `usuario@dominio.com`
- ❌ Rejeita emails incompletos ou sem `@`

### Valores Monetários e Numéricos
- ✅ Aceita valores maiores ou iguais a zero
- ❌ Rejeita valores negativos

## 🎓 Conceitos Demonstrados

1. **Data Quality**: Garantia de qualidade dos dados antes do processamento
2. **Schema Validation**: Uso de schemas declarativos com Pandera
3. **Business Rules**: Implementação de regras de negócio específicas
4. **Error Reporting**: Geração de relatórios úteis para correção de dados
5. **Data Pipeline**: Simulação de pipeline de ETL (Extract, Transform, Load)

## 💡 Diferenciais

- ✨ Validação completa de CPF com algoritmo de dígitos verificadores
- ✨ Relatórios detalhados e organizados por linha/campo
- ✨ Separação automática de dados válidos e inválidos
- ✨ Código limpo, comentado e bem estruturado
