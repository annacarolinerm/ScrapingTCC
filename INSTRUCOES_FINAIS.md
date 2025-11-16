# 🎉 NORMALIZER FINAL - INSTRUÇÕES

## ✅ O QUE FOI CORRIGIDO

### 1. **Palavras-chave**
- Antes: Esperava dict/list
- Agora: Trata como STRING direta
- Código: `if isinstance(pk, str): palavras = pk.strip()`

### 2. **Orientações**
- Antes: Buscava `nomeDoInstituicao` na raiz
- Agora: Busca em `detalhamentoDeOutrasOrientacoesConcluidas.nomeDaInstituicao`
- Exemplo: Instituto Federal de Brasília ✅

## 🚀 COMO USAR

### Execute:
```powershell
python normalizer_definitivo.py
```

**MAS ANTES**, baixe o código corrigido que vou criar!

## 📋 ALTERAÇÕES NECESSÁRIAS

No arquivo `normalizer_definitivo.py`, faça estas mudanças:

### Mudança 1: extract_dados_gerais (linha ~80)
```python
# ADICIONE após a linha do lattes_url:
palavras = ''
try:
    pk = data.get('palavrasChave')
    if isinstance(pk, str):  # ← NOVO: Trata STRING
        palavras = pk.strip()
    elif isinstance(pk, list):
        palavras = ', '.join([str(p) for p in pk if p])
    elif isinstance(pk, dict):
        plist = []
        for i in range(1, 10):
            p = pk.get(f'palavraChave{i}')
            if p:
                plist.append(str(p).strip())
        palavras = ', '.join(plist)
except:
    pass
```

### Mudança 2: extract_orientacoes (linha ~400)
```python
# SUBSTITUA o código de "Outras Orientações" por:

# Outras Orientações
outras = self.get_list_safe(item, 'outrasOrientacoesConcluidas')
for ori in outras:
    if not isinstance(ori, dict):
        continue
    
    # CORRIGIDO: Nome correto do campo
    det = ori.get('detalhamentoDeOutrasOrientacoesConcluidas', {})
    if not isinstance(det, dict):
        continue
    
    nome_ori = self.to_str(det.get('nomeDoOrientado'))
    curso = self.to_str(det.get('nomeDoCurso'))
    inst = self.to_str(det.get('nomeDaInstituicao'))  # ← Aqui!
    
    if not self.is_if(inst):
        continue
    
    basicos = ori.get('dadosBasicosDeOutrasOrientacoesConcluidas', {})
    tit = self.to_str(basicos.get('titulo', ''))
    ano = self.safe_int(basicos.get('ano'))
    
    # ... resto do código
```

## 📊 RESULTADO ESPERADO

Após executar o normalizer corrigido:

```
✅ Palavras-chave: 700+ docentes
✅ Orientações (IFs): 100-300 registros
```

