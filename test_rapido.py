import requests
import json

# Test rápido: verificar si todos los campos funcionan
def test_rapido():
    base_url = 'http://127.0.0.1:5000'
    
    try:
        # 1. Verificar API
        response = requests.get(f'{base_url}/rastreos/12345678')
        if response.status_code == 200:
            data = response.json()[0]
            
            # Campos críticos que mencionaste
            campos_criticos = {
                'destino_cedula': data.get('destino_cedula'),
                'destino_telefono': data.get('destino_telefono'), 
                'destino_direccion': data.get('destino_direccion'),
                'origen_cedula': data.get('origen_cedula'),
                'origen_telefono': data.get('origen_telefono'),
                'origen_direccion': data.get('origen_direccion')
            }
            
            todos_funcionan = all(valor for valor in campos_criticos.values())
            
            print("RESPUESTA RÁPIDA:")
            if todos_funcionan:
                print("✅ SÍ, TODOS LOS CAMPOS FUNCIONAN")
                print("\nCampos verificados:")
                for campo, valor in campos_criticos.items():
                    print(f"  ✅ {campo}: {valor}")
            else:
                print("❌ NO, ALGUNOS CAMPOS FALLAN")
                for campo, valor in campos_criticos.items():
                    status = "✅" if valor else "❌"
                    print(f"  {status} {campo}: {valor}")
        else:
            print("❌ NO FUNCIONA - Error en API")
            
    except Exception as e:
        print(f"❌ NO FUNCIONA - Error: {e}")

test_rapido()
