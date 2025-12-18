#!/usr/bin/env python3
"""
Script para otimizar arquivo de log mantendo conteúdo para auditoria.
Remove códigos ANSI, linhas duplicadas consecutivas e espaços excessivos.
"""
import re
import sys
from pathlib import Path


def remove_ansi_codes(text: str) -> str:
    """Remove códigos de escape ANSI (cores, formatação)."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def optimize_log(input_path: str, output_path: str, target_size_mb: int = 200):
    """Otimiza arquivo de log mantendo conteúdo para auditoria."""
    target_size_bytes = target_size_mb * 1024 * 1024

    print(f"Lendo arquivo: {input_path}")
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    print(f"Total de linhas: {len(lines):,}")

    # Processar linha por linha
    optimized_lines = []
    prev_line = None
    duplicate_count = 0

    for i, line in enumerate(lines):
        if i % 100000 == 0:
            print(f"Processando linha {i:,}/{len(lines):,}...")

        # Remove códigos ANSI
        clean_line = remove_ansi_codes(line)

        # Remove espaços em branco no final
        clean_line = clean_line.rstrip() + "\n"

        # Remove linhas duplicadas consecutivas (mas mantém contador)
        if clean_line == prev_line:
            duplicate_count += 1
            # Mantém a linha a cada 1000 duplicatas para reduzir mais
            if duplicate_count % 1000 == 0:
                optimized_lines.append(f"[{duplicate_count}x duplicado] {clean_line}")
            continue
        else:
            if duplicate_count > 0:
                optimized_lines.append(f"[{duplicate_count}x duplicado acima]\n")
            duplicate_count = 0
            prev_line = clean_line
            optimized_lines.append(clean_line)

    # Se ainda estiver muito grande, aplicar compressão adicional
    content = "".join(optimized_lines)
    current_size = len(content.encode("utf-8"))

    print(f"\nTamanho após primeira otimização: {current_size / (1024*1024):.2f} MB")

    # Aplicar otimizações adicionais até atingir o tamanho alvo
    iteration = 1
    while current_size > target_size_bytes and iteration <= 5:
        iteration += 1
        print(
            f"\nIteração {iteration}: Tamanho ainda acima do limite ({target_size_mb}MB). Aplicando otimizações adicionais..."
        )

        # Remover linhas muito longas ou vazias excessivas
        lines = content.split("\n")
        optimized_lines = []
        empty_count = 0

        # Ajustar limites baseado na iteração
        max_line_length = max(3000 - (iteration * 200), 2000)  # Reduz progressivamente

        for line in lines:
            # Pula linhas vazias excessivas (mantém no máximo 1 consecutiva após iteração 2)
            if not line.strip():
                empty_count += 1
                max_empty = 2 if iteration <= 2 else 1
                if empty_count <= max_empty:
                    optimized_lines.append(line)
                continue
            else:
                empty_count = 0

            # Trunca linhas muito longas progressivamente
            if len(line) > max_line_length:
                line = line[:max_line_length] + "... [truncado]\n"

            # Remove espaços múltiplos (mantém apenas 1 espaço)
            if iteration >= 3:
                line = re.sub(r" +", " ", line)

            optimized_lines.append(line)

        content = "\n".join(optimized_lines)
        current_size = len(content.encode("utf-8"))
        print(f"Tamanho após iteração {iteration}: {current_size / (1024*1024):.2f} MB")

        # Se ainda muito grande, aplicar amostragem de logs repetitivos
        if current_size > target_size_bytes * 1.2 and iteration >= 3:
            print("Aplicando amostragem de logs repetitivos...")
            lines = content.split("\n")
            optimized_lines = []
            log_patterns = {}

            for line in lines:
                # Identifica padrões de log (ex: "INFO src.module:function:123 - mensagem")
                match = re.match(r"^(\w+)\s+([^\s:]+:[^\s:]+:\d+)\s+-\s+(.+)$", line.strip())
                if match:
                    level, location, message = match.groups()
                    pattern_key = f"{level} {location}"

                    if pattern_key not in log_patterns:
                        log_patterns[pattern_key] = []
                    log_patterns[pattern_key].append((len(optimized_lines), message))

                    # Mantém apenas 1 a cada 10 logs do mesmo padrão
                    if len(log_patterns[pattern_key]) % 10 == 0:
                        optimized_lines.append(line)
                    elif len(log_patterns[pattern_key]) == 1:
                        optimized_lines.append(line)
                    # Pula os outros
                else:
                    optimized_lines.append(line)

            content = "\n".join(optimized_lines)
            current_size = len(content.encode("utf-8"))
            print(f"Tamanho após amostragem: {current_size / (1024*1024):.2f} MB")

    # Última passada: se ainda acima do limite, aplicar truncamento mais agressivo
    if current_size > target_size_bytes:
        print(f"\nAplicando truncamento final para atingir {target_size_mb}MB...")
        lines = content.split("\n")

        # Calcula quantas linhas manter baseado no tamanho alvo
        # Estima tamanho médio por linha
        avg_line_size = current_size / len(lines)
        target_lines = int((target_size_bytes * 0.95) / avg_line_size)

        print(f"Tamanho atual: {current_size / (1024*1024):.2f} MB, {len(lines):,} linhas")
        print(f"Tamanho alvo: {target_size_bytes / (1024*1024):.2f} MB, ~{target_lines:,} linhas")
        print(f"Tamanho médio por linha: {avg_line_size:.1f} bytes")

        # Mantém cabeçalho e rodapé, amostra o meio proporcionalmente
        header_lines = min(5000, int(len(lines) * 0.02))  # 2% do início
        footer_lines = min(5000, int(len(lines) * 0.02))  # 2% do final
        middle_lines_needed = max(0, target_lines - header_lines - footer_lines)

        if middle_lines_needed > 0 and len(lines) > header_lines + footer_lines:
            middle_total = len(lines) - header_lines - footer_lines
            # Calcula step para manter apenas middle_lines_needed linhas do meio
            step = max(
                1, (middle_total + middle_lines_needed - 1) // middle_lines_needed
            )  # Arredonda para cima

            print(f"  Header: {header_lines}, Footer: {footer_lines}")
            print(
                f"  Middle: {middle_total:,} linhas -> {middle_lines_needed:,} linhas (step: {step})"
            )

            optimized_lines = []
            optimized_lines.extend(lines[:header_lines])

            # Amostra o meio com step calculado
            for i in range(header_lines, len(lines) - footer_lines, step):
                optimized_lines.append(lines[i])

            optimized_lines.extend(lines[-footer_lines:])

            content = "\n".join(optimized_lines)
            current_size = len(content.encode("utf-8"))
            print(
                f"Tamanho após truncamento final: {current_size / (1024*1024):.2f} MB ({len(optimized_lines):,} linhas)"
            )
        else:
            # Se não conseguiu calcular, simplesmente trunca mantendo início e fim
            keep_start = min(header_lines, target_lines // 2)
            keep_end = target_lines - keep_start
            optimized_lines = lines[:keep_start] + lines[-keep_end:]
            content = "\n".join(optimized_lines)
            current_size = len(content.encode("utf-8"))
            print(
                f"Tamanho após truncamento direto: {current_size / (1024*1024):.2f} MB ({len(optimized_lines):,} linhas)"
            )

    # Salvar arquivo otimizado
    print(f"\nSalvando arquivo otimizado: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    final_size = Path(output_path).stat().st_size
    print(f"\n✅ Concluído!")
    print(f"   Arquivo original: {Path(input_path).stat().st_size / (1024*1024):.2f} MB")
    print(f"   Arquivo otimizado: {final_size / (1024*1024):.2f} MB")
    print(f"   Redução: {(1 - final_size / Path(input_path).stat().st_size) * 100:.1f}%")

    return final_size <= target_size_bytes


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Otimiza arquivo de log mantendo conteúdo para auditoria"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="/home/fahbrain/Documentos/consolidated_fast_20251207_201034.md",
        help="Arquivo de entrada (padrão: consolidated_fast_20251207_201034.md)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="/home/fahbrain/Documentos/consolidated_fast_20251207_201034_optimized.md",
        help="Arquivo de saída (padrão: consolidated_fast_20251207_201034_optimized.md)",
    )
    parser.add_argument(
        "-s", "--size", type=int, default=200, help="Tamanho alvo em MB (padrão: 200)"
    )

    args = parser.parse_args()

    print(f"Tamanho alvo configurado: {args.size} MB")
    success = optimize_log(args.input_file, args.output, target_size_mb=args.size)
    sys.exit(0 if success else 1)
