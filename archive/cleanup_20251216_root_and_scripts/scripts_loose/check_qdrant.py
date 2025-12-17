#!/usr/bin/env python3
"""
Script para verificar collections e métricas do Qdrant.

Uso:
    python check_qdrant.py                    # Verificar todas as collections
    python check_qdrant.py --collection NAME  # Verificar collection específica
    python check_qdrant.py --stats            # Estatísticas gerais
    python check_qdrant.py --cloud            # Verificar se há dados na nuvem
"""

import argparse
import json
import sys
from typing import Any, Dict

try:
    from qdrant_client import QdrantClient
except ImportError:
    print("❌ qdrant-client não instalado. Instale com: pip install qdrant-client")
    sys.exit(1)


class QdrantInspector:
    """Inspeciona collections e métricas do Qdrant."""

    def __init__(self, url: str = "http://localhost:6333"):
        self.client = QdrantClient(url=url)
        self.url = url

    def list_collections(self) -> Dict[str, Any]:
        """Lista todas as collections."""
        try:
            collections = self.client.get_collections()
            return {
                "collections": [col.name for col in collections.collections],
                "count": len(collections.collections),
            }
        except Exception as e:
            return {"error": f"Erro ao listar collections: {e}"}

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Obtém informações detalhadas de uma collection."""
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": info.config.name,
                "vectors": (
                    info.config.params.vectors.size  # type: ignore
                    if hasattr(info.config.params.vectors, "size")
                    else "N/A"
                ),
                "distance": (
                    info.config.params.vectors.distance  # type: ignore
                    if hasattr(info.config.params.vectors, "distance")
                    else "N/A"
                ),
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "status": info.status,
                "config": {
                    "vectors": str(info.config.params.vectors),
                    "optimizers_config": str(info.config.optimizer_config),
                    "wal_config": str(info.config.wal_config),
                },
            }
        except Exception as e:
            return {"error": f"Erro ao obter info da collection {collection_name}: {e}"}

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Obtém estatísticas de uma collection."""
        try:
            # Contar pontos
            count_result = self.client.count(collection_name)  # type: ignore
            points_count = count_result.count

            # Obter vetores de exemplo (se houver)
            sample_vectors = []
            if points_count > 0:
                try:
                    scroll_result = self.client.scroll(
                        collection_name=collection_name,
                        limit=5,
                        with_payload=True,
                        with_vectors=True,
                    )
                    for point in scroll_result[0]:
                        sample_vectors.append(
                            {
                                "id": point.id,
                                "payload_keys": list(point.payload.keys()) if point.payload else [],
                                "vector_dim": len(point.vector) if point.vector else 0,
                            }
                        )
                except Exception as e:
                    sample_vectors = [{"error": f"Erro ao obter amostra: {e}"}]

            return {
                "collection": collection_name,
                "total_points": points_count,
                "sample_vectors": sample_vectors,
                "has_data": points_count > 0,
            }
        except Exception as e:
            return {"error": f"Erro ao obter stats da collection {collection_name}: {e}"}

    def check_cloud_status(self) -> Dict[str, Any]:
        """Verifica se há conexão com Qdrant Cloud."""
        try:
            # Tentar obter informações do cluster
            cluster_info = self.client.get_cluster_info()  # type: ignore
            return {
                "cloud_connected": True,
                "cluster_info": {
                    "peer_id": cluster_info.peer_id,
                    "uris": cluster_info.uris,
                    "status": cluster_info.status,
                },
            }
        except Exception as e:
            # Verificar se é erro de rede ou autenticação
            if "401" in str(e) or "403" in str(e):
                return {
                    "cloud_connected": False,
                    "error": "Erro de autenticação - verifique API key",
                    "details": str(e),
                }
            elif "connection" in str(e).lower():
                return {
                    "cloud_connected": False,
                    "error": "Erro de conexão - possivelmente não é Qdrant Cloud",
                    "details": str(e),
                }
            else:
                return {
                    "cloud_connected": False,
                    "error": f"Erro desconhecido: {e}",
                    "details": str(e),
                }

    def get_system_info(self) -> Dict[str, Any]:
        """Obtém informações do sistema Qdrant."""
        try:
            telemetry = self.client.get_telemetry()  # type: ignore
            return {
                "version": telemetry.app.version if hasattr(telemetry, "app") else "N/A",
                "uptime": telemetry.app.uptime_seconds if hasattr(telemetry, "app") else "N/A",
                "collections_count": len(self.list_collections().get("collections", [])),
                "memory_used": (
                    telemetry.system.memory_used_bytes if hasattr(telemetry, "system") else "N/A"
                ),
                "cpu_usage": (
                    telemetry.system.cpu_usage_percent if hasattr(telemetry, "system") else "N/A"
                ),
            }
        except Exception as e:
            return {"error": f"Erro ao obter info do sistema: {e}"}


def main():
    parser = argparse.ArgumentParser(description="Inspecionar Qdrant collections e métricas")
    parser.add_argument(
        "--url",
        default="http://localhost:6333",
        help="URL do Qdrant (padrão: http://localhost:6333)",
    )
    parser.add_argument("--collection", help="Nome da collection para inspecionar")
    parser.add_argument("--stats", action="store_true", help="Mostrar estatísticas gerais")
    parser.add_argument("--cloud", action="store_true", help="Verificar status da nuvem")
    parser.add_argument("--json", action="store_true", help="Output em JSON")

    args = parser.parse_args()

    try:
        inspector = QdrantInspector(url=args.url)

        if args.cloud:
            # Verificar status da nuvem
            cloud_status = inspector.check_cloud_status()
            if args.json:
                print(json.dumps(cloud_status, indent=2))
            else:
                print("🔍 Status da Nuvem Qdrant:")
                if cloud_status.get("cloud_connected"):
                    print("✅ Conectado ao Qdrant Cloud")
                    print(f"   Peer ID: {cloud_status['cluster_info']['peer_id']}")
                    print(f"   Status: {cloud_status['cluster_info']['status']}")
                else:
                    print("❌ Não conectado ao Qdrant Cloud")
                    print(f"   Erro: {cloud_status.get('error', 'Desconhecido')}")

        elif args.collection:
            # Informações específicas da collection
            info = inspector.get_collection_info(args.collection)
            stats = inspector.get_collection_stats(args.collection)

            if args.json:
                result = {"info": info, "stats": stats}
                print(json.dumps(result, indent=2))
            else:
                print(f"📊 Collection: {args.collection}")
                print(f"   Pontos: {info.get('points_count', 'N/A')}")
                print(f"   Vetores: {info.get('vectors', 'N/A')} dimensões")
                print(f"   Distância: {info.get('distance', 'N/A')}")
                print(f"   Status: {info.get('status', 'N/A')}")
                print(f"   Segmentos: {info.get('segments_count', 'N/A')}")

                if stats.get("has_data"):
                    print(f"   ✅ Contém dados: {stats['total_points']} pontos")
                    if stats.get("sample_vectors"):
                        print("   Amostra de vetores:")
                        for sample in stats["sample_vectors"][:3]:
                            print(
                                f"     ID {sample['id']}: {sample['payload_keys']} keys, {sample['vector_dim']} dims"  # noqa
                            )
                else:
                    print("   ❌ Collection vazia")

        elif args.stats:
            # Estatísticas gerais
            collections = inspector.list_collections()
            system_info = inspector.get_system_info()

            if args.json:
                result = {"collections": collections, "system": system_info}
                print(json.dumps(result, indent=2))
            else:
                print("📊 Estatísticas do Qdrant:")
                print(f"   URL: {args.url}")
                print(f"   Collections: {collections.get('count', 0)}")
                print(f"   Versão: {system_info.get('version', 'N/A')}")
                print(f"   Uptime: {system_info.get('uptime', 'N/A')}s")
                print(f"   Memória: {system_info.get('memory_used', 'N/A')} bytes")
                print(f"   CPU: {system_info.get('cpu_usage', 'N/A')}%")

                if collections.get("collections"):
                    print("   Collections encontradas:")
                    for col in collections["collections"]:
                        col_stats = inspector.get_collection_stats(col)
                        points = col_stats.get("total_points", 0)
                        print(f"     - {col}: {points} pontos")

        else:
            # Listar collections
            collections = inspector.list_collections()

            if args.json:
                print(json.dumps(collections, indent=2))
            else:
                print("📋 Collections no Qdrant:")
                if collections.get("collections"):
                    for col in collections["collections"]:
                        col_stats = inspector.get_collection_stats(col)
                        points = col_stats.get("total_points", 0)
                        status = "✅" if points > 0 else "❌"
                        print(f"   {status} {col}: {points} pontos")
                else:
                    print("   Nenhuma collection encontrada")

    except Exception as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
