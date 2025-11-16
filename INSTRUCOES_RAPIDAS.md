# 🚀 INSTRUÇÕES RÁPIDAS DE USO

## ⚡ Setup Rápido

```bash
# 1. Instalar dependências
pip install aiohttp --break-system-packages

# 2. Testar o sistema
python test_sistema.py

# 3. Fazer diagnóstico (RECOMENDADO)
python diagnostico.py

# 4. Coletar dados
python main.py                    # Todas as 40 instituições
python main.py IFB IFSP          # Instituições específicas

# 5. Normalizar dados
python normalizer.py

# 6. Visualizar estatísticas
python visualizar_banco.py
```

## 📊 Scripts Disponíveis

| Script | Função |
|--------|--------|
| `main.py` | Coleta principal de dados |
| `diagnostico.py` | Testa conectividade e filtros |
| `normalizer.py` | Extrai dados estruturados |
| `verificar_faltantes.py` | Lista instituições faltantes |
| `comparar_totais.py` | Valida completude da coleta |
| `visualizar_banco.py` | Estatísticas detalhadas |
| `test_sistema.py` | Testa se tudo está OK |

## ✅ Checklist de Uso

- [ ] Instalar aiohttp
- [ ] Executar test_sistema.py
- [ ] Executar diagnostico.py
- [ ] Executar main.py (pode demorar ~1 hora)
- [ ] Executar normalizer.py
- [ ] Executar visualizar_banco.py
- [ ] Validar com comparar_totais.py

## 🎯 40 Instituições da Rede Federal

1. IFAC (AC) 2. IFAL (AL) 3. IFAP (AP) 4. IFAM (AM)
5. IFBA (BA) 6. IFBAIANO (BA) 7. IFB (DF) 8. IFCE (CE)
9. IFES (ES) 10. IFG (GO) 11. IFGOIANO (GO) 12. IFMA (MA)
13. IFMG (MG) 14. IFNMG (MG) 15. IFSUDESTEMG (MG)
16. IFSULDEMINAS (MG) 17. IFTM (MG) 18. CEFET-MG (MG)
19. IFMT (MT) 20. IFMS (MS) 21. IFPA (PA) 22. IFPB (PB)
23. IFPE (PE) 24. IFSertaoPE (PE) 25. IFPI (PI) 26. IFPR (PR)
27. IFRJ (RJ) 28. IFFLUMINENSE (RJ) 29. CEFET-RJ (RJ)
30. IFRN (RN) 31. IFRO (RO) 32. IFRR (RR) 33. IFRS (RS)
34. IFFARROUPILHA (RS) 35. IFSUL (RS) 36. IFSC (SC)
37. IFC (SC) 38. IFSP (SP) 39. IFS (SE) 40. IFTO (TO)

## ⚙️ Configurações Importantes

**config.py:**
- `PAGE_SIZE = 50` - Itens por página
- `MAX_CONCURRENT_INSTITUTIONS = 5` - Instituições em paralelo
- `MAX_CONCURRENT_DETAILS = 50` - Requisições simultâneas
- `TIMEOUT = 60` - Timeout em segundos
- `MAX_RETRIES = 3` - Tentativas em caso de falha

## 📈 Dados Esperados

- **Total:** ~40.000 docentes
- **Por instituição:** 400 a 3.500 docentes
- **Tempo de coleta:** ~1 hora (todas)
- **Tamanho do banco:** ~500 MB a 2 GB

## 🔧 Troubleshooting

**Erro de timeout?**
→ Aumente `TIMEOUT` em config.py

**Poucos docentes filtrados?**
→ Execute diagnostico.py e analise os cargos ignorados

**Instituições falharam?**
→ Execute novamente só elas: `python main.py IFG IFMT IFS`

**Banco vazio?**
→ Execute main.py primeiro

## 💡 Dicas

1. Sempre execute o diagnóstico antes da coleta completa
2. Monitore o progresso (exibe em tempo real)
3. Se interromper, pode retomar depois (dados já salvos permanecem)
4. Use verificar_faltantes.py para saber o que falta
5. Use comparar_totais.py para validar completude

## 📚 Estrutura do Banco

**Tabela principal:** `docentes`
- Contém JSON completo + dados básicos

**7 tabelas normalizadas:**
1. dados_gerais - Nome, ORCID, resumo CV
2. formacoes - Graduação, mestrado, doutorado
3. atuacoes - Vínculos profissionais
4. producao_bibliografica - Artigos, livros
5. orientacoes_concluidas - Orientações
6. premios_titulos - Prêmios recebidos
7. areas_atuacao - Áreas CNPq

## 🎓 Uso Acadêmico

Sistema desenvolvido para TCC/pesquisa acadêmica sobre o perfil dos docentes da Rede Federal. Os dados são públicos e acessíveis via Portal Integra.

---

**Sistema robusto, testado e funcional!** 🚀

Leia README.md para informações detalhadas.
