import argparse
import time

try:
    import numpy as np
    from mpi4py import MPI
except ImportError as erro:
    raise SystemExit(
        "Instale NumPy e mpi4py com: python -m pip install numpy mpi4py"
    ) from erro

TAG_PERGUNTA = 101
TAG_RESPOSTA = 202


def calcular_resposta(valor):
    return 2 * valor + 1


def main():
    parser = argparse.ArgumentParser(
        description="Demonstra envio síncrono MPI com Ssend e Recv."
    )
    parser.add_argument("--valor", type=int, default=21,
                        help="Número enviado do rank 0 ao rank 1.")
    parser.add_argument("--atraso", type=float, default=1.0,
                        help="Segundos que o rank 1 espera antes de Recv().")
    args = parser.parse_args()
    if args.atraso < 0:
        parser.error("--atraso não pode ser negativo")

    comunicador = MPI.COMM_WORLD
    rank = comunicador.Get_rank()
    quantidade = comunicador.Get_size()

    if quantidade != 2:
        if rank == 0:
            print("ERRO: esta atividade exige exatamente dois processos. "
                  "Use: mpiexec -n 2 python pratica4_mensagens_sincronas.py")
        return

    comunicador.Barrier()

    if rank == 0:
        mensagem = np.array([args.valor], dtype=np.int64)
        resposta = np.empty(1, dtype=np.int64)

        print(f"[rank 0] Tentando enviar {mensagem[0]} com Ssend...",
              flush=True)
        inicio = MPI.Wtime()

        comunicador.Ssend([mensagem, MPI.INT64_T],
                          dest=1, tag=TAG_PERGUNTA)

        duracao = MPI.Wtime() - inicio
        print(f"[rank 0] Ssend retornou após {duracao:.3f} s.",
              flush=True)

        comunicador.Recv([resposta, MPI.INT64_T],
                         source=1, tag=TAG_RESPOSTA)
        print(f"[rank 0] Resposta recebida: {int(resposta[0])}.",
              flush=True)
        print(f"[rank 0] Conferência: "
              f"{int(resposta[0]) == calcular_resposta(args.valor)}",
              flush=True)

    else:
        recebida = np.empty(1, dtype=np.int64)
        print(f"[rank 1] Esperando {args.atraso:.2f} s "
              "ANTES de chamar Recv...", flush=True)
        time.sleep(args.atraso)

        comunicador.Recv([recebida, MPI.INT64_T],
                         source=0, tag=TAG_PERGUNTA)
        valor_recebido = int(recebida[0])
        print(f"[rank 1] Mensagem recebida: {valor_recebido}.",
              flush=True)

        novo_valor = calcular_resposta(valor_recebido)
        devolucao = np.array([novo_valor], dtype=np.int64)
        print(f"[rank 1] Enviando de volta {novo_valor} com Ssend...",
              flush=True)

        comunicador.Ssend([devolucao, MPI.INT64_T],
                          dest=0, tag=TAG_RESPOSTA)
        print("[rank 1] Resposta entregue.", flush=True)


if __name__ == "__main__":
    main()
