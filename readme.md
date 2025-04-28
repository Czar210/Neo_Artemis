# Neo_Artemis - Análise de Estilos de Junglers no League of Legends

## 🎯 Objetivo

Este projeto visa analisar o estilo de jogo de jogadores que atuam como junglers em League of Legends, neutralizando o impacto dos campeões utilizados para recomendar campeões que potencializem seus pontos fortes e minimizem seus pontos fracos.

---

## 🏗️ Estrutura do Projeto

| Pasta | Conteúdo |
|:---|:---|
| `/api_site/` | Código principal da API Flask e do site para análise de jogadores. |
| `/massa_dados/` | Scripts antigos de coleta, limpeza e organização das partidas para montar as bases de dados. |
| `/dados_brutos/` | CSVs contendo dados crus ou estatísticas não utilizadas diretamente na API. |
| `/logs/` | Arquivos de log de execução de testes, erros e coletas. |
---

## ⚙️ Tecnologias Utilizadas

- **Python 3.12**
- **Flask** (API e Front-End)
- **SQLite** (Banco de Dados Local)
- **Pandas e Numpy** (Processamento de dados)
- **Chart.js** (Gráficos Radar)
- **Bootstrap 5** (Estilização de páginas)

---

## 🚀 Como Rodar o Projeto Localmente

1. Clone o repositório:
    ```bash
    git clone https://github.com/Czar210/Neo_Artemis.git
    cd Trabalho Engenharia Social LoL - codigo do site api e bd
    ```

2. Instale as dependências necessárias:
    ```bash
    pip install flask pandas numpy python-dotenv
    ```

3. Crie um arquivo `.env` na raiz da pasta `/api_site/` com o conteúdo:

    ```
    RIOT_API_KEY=coloque_sua_chave_aqui
    ```

4. Inicie o servidor Flask:
    ```bash
    python app.py
    ```

5. Acesse o site no navegador:
    ```
    http://127.0.0.1:5000/
    ```

---

## 📚 Funcionalidades do Site

- 🔎 **Buscar jogador**: Coletar e analisar partidas ranqueadas (fila 420) do jogador, calcular seus scores compostos e recomendar campeões compatíveis.
- 📈 **Ver Tabela de Scores dos Campeões**: Visualizar os scores médios de dezenas de junglers profissionais baseados em dados reais de vitória e derrota.
- 🧠 **Fazer o Quiz**: Caso o usuário não tenha conta no jogo, poderá fazer um quiz e obter recomendações baseadas em seu estilo pessoal.
- ℹ️ **Sobre o Projeto**: Página explicativa sobre a metodologia, etapas, tecnologias e equipe.

---

## 📈 Como Funciona a Análise?

- Os dados são coletados diretamente da API da Riot Games, respeitando filtros de qualidade (AFK, rendições precoces, etc.).
- São extraídas mais de 50 estatísticas por partida.
- São construídos 8 scores compostos:
  - Agressividade
  - Controle de Mapa
  - Eficiência de Recursos
  - Pressão em Estruturas
  - Sustentação e Sobrevivência
  - Impacto Utilitário
  - Impacto no Early Game
  - Controle de Objetivos
- As recomendações de campeões são feitas via similaridade vetorial (Similaridade de Cosseno).

---

## 👥 Equipe do Projeto

- **André Messina** — "O Bruxo dos Dados"  
    Responsável pela integração API-Flask, backend, banco de dados e pela organização geral do sistema.

- **César Sibila** — "O Gênio da Lâmpada"  
    Especialista nos cálculos matemáticos dos scores compostos, estruturação lógica dos indicadores e divisão de tarefas.

- **Takida** — "Escudeiro Fiel"  
    Atuação crítica na validação das variáveis relevantes, testes de consistência, decisões estratégicas e documentação.

- **Willian** — Apoio Geral  
    Suporte na revisão de scripts, testes e brainstorming de ideias durante o desenvolvimento.

---

## 📦 Observações

- O projeto exige uma chave válida da Riot Games para funcionar (`RIOT_API_KEY`).
- O arquivo `.env` **não é enviado para o repositório** por motivos de segurança.
- Para coleta em larga escala (mais de 100 partidas), ajustes de rate limit serão necessários.

---

# 🏆 Conclusão

Este projeto combina conceitos de Ciência de Dados, Engenharia de Software e Machine Learning para resolver um problema real de recomendação no contexto de jogos online.  
É uma entrega completa de um sistema robusto, modular e escalável, feito com alta qualidade técnica e cuidado com a experiência do usuário.

---

