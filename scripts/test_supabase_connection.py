import os
import asyncio
from supabase import create_client, Client

async def test_supabase():
    url = os.environ.get("OMNIMIND_SUPABASE_URL")
    key = os.environ.get("OMNIMIND_SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("❌ Supabase credentials missing in environment")
        return

    try:
        supabase: Client = create_client(url, key)
        # Tenta uma operação simples, como listar tabelas (se possível via API) ou ler uma tabela padrão
        # Como não sabemos as tabelas, vamos tentar auth.admin.list_users() se for service role

        print(f"Connecting to {url}...")
        # A biblioteca supabase-py é síncrona por padrão, mas vamos rodar em thread se precisasse.
        # Aqui é script de teste, pode ser síncrono.

        # Teste básico de auth (geralmente funciona se a chave for válida)
        try:
            users = supabase.auth.admin.list_users()
            print(f"✅ Supabase Connection OK. Users found: {len(users)}")
        except Exception as e:
            print(f"⚠️  Supabase Auth check failed: {e}")
            # Tenta listar uma tabela 'memories' se existir
            try:
                data = supabase.table("memories").select("*").limit(1).execute()
                print("✅ Supabase Table 'memories' access OK")
            except Exception as e2:
                print(f"❌ Supabase Table access failed: {e2}")

    except Exception as e:
        print(f"❌ Supabase Connection Failed: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(test_supabase())
