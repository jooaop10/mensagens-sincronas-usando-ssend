# Troca de Mensagens Síncronas com MPI (`Ssend`)

Demonstração prática de comunicação síncrona ponto a ponto utilizando **MPI** (`mpi4py`) e **NumPy** em Python. O objetivo é evidenciar, com exatamente dois processos, que `Ssend()` realiza um envio **síncrono e bloqueante**: a chamada de envio no processo remetente só retorna após o processo receptor iniciar a chamada `Recv()` correspondente.

---

## Objetivo

Mostrar na prática o comportamento de *handshake* do modo de envio síncrono (`Ssend()`) no MPI, medindo o tempo em que o processo remetente (`rank 0`) permanece bloqueado aguardando o processo receptor (`rank 1`) iniciar a recepção após um atraso configurável.

---

## Como funciona

O fluxo de execução entre os dois processos segue as etapas abaixo:

1. **Alinhamento inicial**: ambos os processos executam `Barrier()` para iniciar a demonstração no mesmo ponto lógico.
2. **Preparação dos dados (`rank 0`)**: o processo `0` prepara um inteiro de 64 bits (`np.int64`, padrão `21`) em um buffer NumPy.
3. **Atraso intencional (`rank 1`)**: antes de chamar `Recv()`, o processo `1` aguarda um intervalo configurável (`--atraso`, padrão `1.0` s).
4. **Envio síncrono (`rank 0` → `rank 1`)**: o `rank 0` chama `Ssend()` com a tag `TAG_PERGUNTA` (`101`) e mede a duração da chamada com `MPI.Wtime()`. Ele fica bloqueado até que o `rank 1` inicie o `Recv()` correspondente com a mesma origem e tag.
5. **Processamento (`rank 1`)**: após receber o valor, o `rank 1` aplica a transformação `2 * valor + 1`.
6. **Retorno síncrono (`rank 1` → `rank 0`)**: o `rank 1` devolve o resultado usando `Ssend()` com uma tag distinta (`TAG_RESPOSTA = 202`), evitando confusão entre os dois sentidos da comunicação, enquanto o `rank 0` aguarda com `Recv()`.
7. **Conferência (`rank 0`)**: o `rank 0` exibe a duração do primeiro `Ssend()`, o valor recebido e valida se o resultado confere com o cálculo esperado.

---

## Principais funções e conceitos MPI

| Recurso | Descrição |
| --- | --- |
| `MPI.COMM_WORLD` | Comunicador global que engloba todos os processos MPI iniciados. |
| `Get_rank()` | Identifica o índice do processo atual (`0` ou `1`). |
| `Get_size()` | Retorna a quantidade total de processos no comunicador. |
| `Barrier()` | Sincroniza o ponto de partida lógico entre os processos; não realiza o pareamento de `Ssend()`. |
| `Ssend()` | Envio **bloqueante em modo síncrono**: só conclui quando a recepção correspondente é iniciada. |
| `Recv()` | Recepção bloqueante que consome o buffer correspondente (identificado por origem, destino, comunicador e `tag`). |
| `MPI.Wtime()` | Relógio de alta resolução usado para medir a duração da chamada `Ssend()`. |

> **Nota sobre buffers e tags**: Os métodos com inicial maiúscula (`Ssend`, `Recv`) operam diretamente sobre buffers NumPy tipados (como `np.int64` / `MPI.INT64_T`), evitando sobrecarga de serialização. Cada mensagem é identificada pelo envelope composto por origem, destino, comunicador e `tag` (`TAG_PERGUNTA = 101` e `TAG_RESPOSTA = 202`).

---

## Pré-requisitos e Setup

1. **Python 3.8+** instalado.
2. **Implementação MPI** instalada no sistema operacional (por exemplo: MS-MPI no Windows, Open MPI ou MPICH no Linux/macOS), necessária para disponibilizar o comando `mpiexec`.
3. **Dependências Python** (`numpy` e `mpi4py`):

```bash
python -m pip install numpy mpi4py
```

---

## Execução

Execute o script com exatamente **2 processos** via `mpiexec`:

```bash
mpiexec -n 2 python mensagens_sincronas.py --valor 21 --atraso 1.0
```

### Parâmetros de linha de comando

| Argumento | Tipo | Padrão | Descrição |
| --- | --- | --- | --- |
| `--valor` | `int` | `21` | Número inteiro enviado do `rank 0` para o `rank 1`. |
| `--atraso` | `float` | `1.0` | Tempo (em segundos, `>= 0`) que o `rank 1` aguarda antes de chamar `Recv()`. |

### Comportamento esperado

Como `Ssend()` aguarda o início de `Recv()` no `rank 1`, o tempo medido pelo `rank 0` será aproximadamente igual ao valor configurado em `--atraso` (por exemplo, `~1.000 s`).

---

## Pontos de atenção

- **Bloqueante ≠ Síncrono**: em MPI, `Send()` (modo padrão) é bloqueante quanto ao reuso do buffer, mas pode completar imediatamente copiando mensagens pequenas para um buffer interno, sem esperar o receptor. Já `Ssend()` garante o *handshake* síncrono com a recepção correspondente.
- **Quantidade fixa de processos**: esta prática foi projetada para **exatamente 2 processos** (`-n 2`). Executar com mais ou menos processos encerrará a execução com aviso de erro.
