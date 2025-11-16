# 🎓 Scraper Portal Integra - Rede Federal de Ensino

Sistema completo e robusto para coleta de dados dos docentes dos Institutos Federais e CEFETs através do Portal Integra.

## 📋 Sobre

Este sistema realiza web scraping dos dados públicos de docentes das 40 instituições da Rede Federal de Ensino (38 Institutos Federais + 2 CEFETs), armazenando em um banco SQLite para análise posterior.

**Características principais:**
- ✅ Coleta assíncrona com paralelização inteligente
- ✅ Retry automático em caso de falhas
- ✅ Filtro abrangente para capturar todos os docentes
- ✅ Banco de dados SQLite normalizado
- ✅ Scripts de diagnóstico e validação
- ✅ Sem necessidade de Selenium (API REST pública)

## 🚀 Instalação

### Requisitos

- Python 3.8 ou superior
- Conexão com internet

### Instalação de dependências

```bash
pip install aiohttp --break-system-packages
```

**Observação:** As bibliotecas `sqlite3`, `json`, `asyncio` já vêm com o Python.

## 📂 Estrutura de Arquivos

```
projeto/
├── main.py                      # Script principal de coleta
├── config.py                    # Configurações e lista de instituições
├── scraper.py                   # Lógica de coleta com retry
├── database.py                  # Gerenciamento do SQLite
├── normalizer.py                # Normalização dos dados
├── diagnostico.py               # Diagnóstico completo das APIs
├── verificar_faltantes.py       # Verifica instituições faltantes
├── comparar_totais.py           # Compara API vs Banco
├── visualizar_banco.py          # Estatísticas do banco
├── lista_instituicoes.json      # JSON das 40 instituições
├── integra.db                   # Banco SQLite (gerado após coleta)
└── README.md                    # Este arquivo
```

## 🎯 Uso

### 1. Diagnóstico (Recomendado antes de coletar)

Antes de iniciar a coleta completa, é recomendado executar o diagnóstico para verificar a conectividade e o filtro de docentes:

```bash
python diagnostico.py
```

Este script irá:
- Testar conexão com todas as 40 instituições
- Mostrar quantas pessoas existem em cada API
- Quantos docentes serão filtrados
- Exemplos de cargos encontrados e ignorados
- Identificar possíveis problemas

### 2. Coleta de Dados

#### Coletar TODAS as 40 instituições:

```bash
python main.py
```

#### Coletar instituições ESPECÍFICAS:

```bash
python main.py IFB IFSP IFRJ
```

#### Coletar instituições que falharam:

```bash
python main.py IFG IFMT IFS IFSUDESTEMG IFTM
```

**Tempo estimado:** ~1 hora para todas as 40 instituições (dependendo da conexão).

### 3. Normalização dos Dados

Após a coleta, execute o normalizador para extrair dados estruturados:

```bash
python normalizer.py
```

Este script extrai do JSON completo e popula 7 tabelas normalizadas:
- `dados_gerais` - Informações básicas
- `formacoes` - Formações acadêmicas
- `atuacoes` - Atuações profissionais
- `producao_bibliografica` - Artigos, livros, capítulos
- `orientacoes_concluidas` - Orientações de mestrado/doutorado
- `premios_titulos` - Prêmios recebidos
- `areas_atuacao` - Áreas de conhecimento

### 4. Scripts de Validação

#### Verificar instituições faltantes:

```bash
python verificar_faltantes.py
```

Mostra quais das 40 instituições ainda não foram coletadas.

#### Comparar totais (API vs Banco):

```bash
python comparar_totais.py
```

Compara o número de docentes na API com o que está no banco, identificando possíveis inconsistências.

#### Visualizar estatísticas:

```bash
python visualizar_banco.py
```

Exibe estatísticas detalhadas:
- Total de docentes por instituição
- Distribuição por estado
- Cobertura dos dados normalizados
- Produções bibliográficas
- Orientações concluídas
- Áreas de conhecimento mais comuns

## 📊 Estrutura do Banco de Dados

### Tabela Principal: `docentes`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| sigla | TEXT | Sigla da instituição (IFB, IFSP, etc) |
| slug | TEXT | Identificador único (UNIQUE) |
| nome | TEXT | Nome do docente |
| campus | TEXT | Campus de lotação |
| cargo | TEXT | Cargo/função |
| email | TEXT | Email (quando disponível) |
| url | TEXT | URL do perfil no Integra |
| data_completa | TEXT | JSON completo da API |
| atualizado_em | TIMESTAMP | Data da última atualização |

### Tabelas Normalizadas

1. **dados_gerais** - Nome completo, ORCID, resumo CV
2. **formacoes** - Graduação, mestrado, doutorado, etc
3. **atuacoes** - Vínculos profissionais
4. **producao_bibliografica** - Artigos, livros, capítulos
5. **orientacoes_concluidas** - Orientações de TCC/mestrado/doutorado
6. **premios_titulos** - Prêmios e títulos recebidos
7. **areas_atuacao** - Áreas de conhecimento CNPQ

## ⚙️ Configurações

### Arquivo `config.py`

Principais configurações que podem ser ajustadas:

```python
PAGE_SIZE = 50                      # Itens por página da API
MAX_CONCURRENT_INSTITUTIONS = 5     # Instituições em paralelo
MAX_CONCURRENT_DETAILS = 50         # Requisições de detalhes por instituição
TIMEOUT = 60                        # Timeout em segundos
MAX_RETRIES = 3                     # Tentativas em caso de falha
RETRY_DELAY = 2                     # Delay entre tentativas
```

### Filtro de Docentes

O sistema usa um filtro **ABRANGENTE** para capturar todos os docentes. Os termos incluídos são:

```python
TERMOS_DOCENTE = [
    "professor", "docente", "ebtt", "magistério", 
    "ensino", "titular", "adjunto", "assistente",
    "auxiliar", "substituto", "temporário", "visitante",
    "associado", "colaborador"
]
```

Se necessário, você pode adicionar mais termos em `config.py`.

## 🔧 Resolução de Problemas

### Problema: Algumas instituições falharam na coleta

**Solução:** Execute novamente apenas as instituições que falharam:

```bash
python main.py IFG IFMT IFS
```

O sistema tem retry automático (3 tentativas) e deve resolver a maioria dos problemas temporários.

### Problema: Poucos docentes foram filtrados

**Solução:** Execute o diagnóstico para ver os cargos ignorados:

```bash
python diagnostico.py
```

Analise os "Cargos ignorados" e, se necessário, adicione novos termos em `config.py`.

### Problema: Timeout constante

**Solução:** Aumente o timeout em `config.py`:

```python
TIMEOUT = 120  # 2 minutos
```

### Problema: Erro de SSL/Certificado

O sistema já está configurado para aceitar certificados inválidos (`ssl=False` no aiohttp). Se ainda assim houver problemas, verifique sua conexão com internet.

## 📈 Dados Esperados

- **Total estimado:** ~40.000 docentes em toda a rede
- **Por instituição:** 400 a 3.500 docentes
- **Tamanho do banco:** ~500 MB a 2 GB (dependendo dos detalhes)
- **Tempo de coleta:** ~1 hora (todas as instituições)
- **Tempo de normalização:** ~10-30 minutos

## 🎓 Uso Acadêmico

Este sistema foi desenvolvido para uso em pesquisa acadêmica (TCC). Os dados coletados são **públicos** e estão disponíveis nos portais Integra de cada instituição.

**Importante:** Respeite os termos de uso e privacidade. Não use os dados para fins comerciais ou inapropriados.

## 🐛 Troubleshooting Adicional

### IFFLUMINENSE usa HTTP

O Instituto Federal Fluminense é a única instituição que usa HTTP ao invés de HTTPS. Isso é normal e já está configurado corretamente.

### Certificados SSL inválidos

Algumas instituições possuem certificados SSL inválidos ou expirados. O sistema já está configurado para ignorar isso.

### Delay entre requisições

O sistema inclui delays estratégicos entre requisições para não sobrecarregar as APIs:
- 0.1s entre páginas de pessoas
- 0.5s entre lotes de detalhes

## 📞 Suporte

Se encontrar problemas:

1. Execute o diagnóstico: `python diagnostico.py`
2. Verifique os logs de erro exibidos
3. Compare totais: `python comparar_totais.py`
4. Visualize estatísticas: `python visualizar_banco.py`

## 📝 Licença

Este código é disponibilizado para fins educacionais e de pesquisa. Use com responsabilidade.

---

**Desenvolvido para TCC - Análise do Perfil dos Docentes da Rede Federal de Ensino**

🚀 **Sistema robusto, testado e funcional!**
