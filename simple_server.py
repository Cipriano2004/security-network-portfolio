#!/usr/bin/env python3
"""
Servidor HTTP Simples - Teste de Conectividade
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

class SimpleServer(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests"""
        
        if self.path == '/':
            # Servir página HTML simples
            html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Server</title>
    <style>
        body { font-family: Arial; background: #1a1d23; color: white; padding: 20px; }
        .status { color: #28a745; font-size: 2em; text-align: center; }
        .info { background: #2d3142; padding: 15px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="status">✅ SERVIDOR FUNCIONANDO!</div>
    <div class="info">
        <h3>🛡️ SOC/NOC Test Server</h3>
        <p>Servidor HTTP básico para testar conectividade</p>
        <p>Timestamp: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    </div>
    <div class="info">
        <h3>🔗 APIs Disponíveis:</h3>
        <ul>
            <li><a href="/api/test" style="color: #17a2b8;">/api/test</a> - Teste básico</li>
            <li><a href="/api/time" style="color: #17a2b8;">/api/time</a> - Hora atual</li>
        </ul>
    </div>
    <script>
        console.log('✅ Página carregada com sucesso!');
        setInterval(() => {
            console.log('🔄 Servidor ativo - ' + new Date().toLocaleTimeString());
        }, 5000);
    </script>
</body>
</html>"""
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/api/test':
            # API de teste simples
            data = {
                "status": "OK",
                "message": "Servidor funcionando perfeitamente!",
                "timestamp": datetime.now().isoformat(),
                "test_data": {
                    "devices": 103,
                    "cpu": 25.5,
                    "memory": 45.2
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode())
            
        elif self.path == '/api/time':
            # API de tempo
            data = {
                "current_time": datetime.now().isoformat(),
                "status": "online"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            
        else:
            self.send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        """Log das requisições"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def main():
    print("🚀 Iniciando servidor de teste simples...")
    print("📡 Endereço: http://localhost:8080")
    
    try:
        server = HTTPServer(('localhost', 8080), SimpleServer)
        print("✅ Servidor HTTP básico rodando!")
        print("🌐 Acesse: http://localhost:8080")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado")
        server.shutdown()
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
