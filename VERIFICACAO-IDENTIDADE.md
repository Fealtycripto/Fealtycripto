# Conferência da identidade profissional

A referência pública contém apenas fatos aprovados: `identidade-publica.json`, versão editorial BIO-1.0. O minicurrículo está em `MINICURRICULO.md`. A versão editorial não é versão da estratégia de investimento.

Execute manualmente, com Python 3, na pasta deste repositório:

```sh
python tools/verificar_identidade.py --self-test
```

O verificador lê somente os caminhos listados em `identidade-fontes.json`. Não faz login, não usa rede, não publica, não altera as fontes e não depende de segredos ou de arquivos privados. O teste cria cópias temporárias deliberadamente divergentes e verifica nome, função, associação entre entidades e versão. Também aceita aliases históricos, textos curtos e canais de marca.

Para conferir outras fontes locais públicas, crie um manifesto explícito com `sources`, `path`, `required` (expressões em texto sem acentos) e, se necessário, `start` e `end` para delimitar a apresentação atual. Use:

```sh
python tools/verificar_identidade.py --manifest caminho/manifesto.json
```

Não inclua registros históricos ou contexto privado como biografia atual. A conferência identifica os fatos e padrões listados; não prova credenciais, disponibilidade dos produtos ou consistência de toda a internet.

Para corrigir um fato aprovado, revise os dados e os textos pertinentes com a autorização do titular. Registre a nova versão, rode a conferência e releia cada destino após salvar. Não há sincronização ou publicação automática.

## Reversão editorial

Consulte o diff do commit editorial. Se os mesmos campos não tiverem sido editados depois, reverta esse commit em uma nova branch e passe pelo fluxo normal de revisão. Havendo edição posterior, concilie somente os trechos necessários. Evite restaurar arquivos inteiros de uma versão antiga e nunca force o histórico.
