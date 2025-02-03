# Simulador de Escalonamento de Sistemas Operacionais

## Visão Geral

Este projeto é um simulador gráfico para diversos algoritmos de escalonamento de CPU e algoritmos de substituição de páginas. Ele permite que os usuários insiram informações sobre processos, selecionem algoritmos de escalonamento e visualizem a linha do tempo da execução dos processos e o gerenciamento de memória usando um gráfico de Gantt e uma representação da RAM.

## Integrantes do Grupo

*   Arthur Batista
*   Iris Nogueira
*   Malu Brito
*   Victor Manoel

## Professor

*   Maycon Leone Peixoto

## Funcionalidades

*   **Entrada de Processos:** Os usuários podem especificar o número de processos e suas características individuais:
    *   Tempo de Chegada
    *   Tempo de Execução
    *   Deadline (para EDF)
    *   Páginas de Memória
*   **Algoritmos de Escalonamento:** Implementa os seguintes algoritmos de escalonamento de CPU:
    *   Primeiro a Chegar, Primeiro a Ser Servido (FIFO)
    *   Trabalho Mais Curto Primeiro (SJF)
    *   Round Robin (RR)
    *   Primeiro Prazo Mais Próximo (EDF)
*   **Algoritmos de Substituição de Páginas:** Implementa os seguintes algoritmos de substituição de páginas:
    *   Primeiro a Entrar, Primeiro a Sair (FIFO)
*   **Visualização em Tempo Real:**
    *   Atualizações incrementais do gráfico de Gantt para mostrar o progresso da execução dos processos passo a passo.
    *   Contador de linha do tempo para indicar a unidade de tempo.
    *   Cálculo do tempo de turnaround em tempo real.
    *   Visualização do uso da RAM para substituição de páginas.
*   **Parâmetros de Simulação:**
    *   Quantum configurável para Round Robin.
    *   Sobrecarga configurável para Round Robin e EDF.
*   **Saída:**
    *   Exibe o uso da CPU ao longo do tempo.
    *   Calcula e mostra o tempo médio de turnaround.

## Como Executar

1.  **Pré-requisitos:** Certifique-se de que o Python 3.x esteja instalado.
2.  **Executar:**
    ```bash
    python simulador.py
    ```
3.  **Uso:**
    *   Insira o número de processos.
    *   Clique em "Adicionar Processos" para definir os dados individuais de cada processo.
    *   Selecione um algoritmo de escalonamento.
    *   Defina os parâmetros de quantum e sobrecarga, se necessário.
    *   Selecione um algoritmo de substituição de páginas.
    *   Clique em "Iniciar Simulação" para começar.

## Implementações de Algoritmos

*   **FIFO (Primeiro a Chegar, Primeiro a Ser Servido):** Os processos são executados na ordem em que chegam.
*   **SJF (Trabalho Mais Curto Primeiro):** Os processos são executados com base no tempo de execução mais curto primeiro.
*   **Round Robin:** Os processos são executados com base em um quantum de tempo definido.
*   **EDF (Primeiro Prazo Mais Próximo):** Os processos são executados com base em seus prazos.
*   **FIFO (Substituição de Páginas):** As páginas são substituídas na ordem em que chegaram na RAM.

Este projeto é para fins educacionais.
