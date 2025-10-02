# Seguridad de APIs - Demo Dockerizado

## 1. Desarrollo Conceptual

**Definición:**  
La seguridad de APIs consiste en un conjunto de prácticas, políticas y técnicas diseñadas para proteger las interfaces de programación de aplicaciones (APIs) frente a accesos no autorizados, ataques y exposición de información sensible. Las APIs son puntos críticos de integración entre sistemas, por lo que garantizar su seguridad es fundamental.

**Relación con atributos de calidad:**  
- **Seguridad:** Protege los datos y recursos frente a accesos indebidos.  
- **Fiabilidad / Disponibilidad:** Evita ataques que interrumpan el servicio, como DDoS.  
- **Integridad:** Asegura que los datos enviados y recibidos no sean alterados.  
- **Mantenibilidad:** Permite políticas de seguridad centralizadas, facilitando actualizaciones futuras.

**Tácticas de seguridad implementadas:**  
1. **Autenticación:** Verificación de identidad mediante JWT.  
2. **Autorización:** Control de acceso a recursos según el usuario autenticado.  
3. **Cifrado de datos en tránsito:** Uso de HTTPS (TLS) para proteger la comunicación.  
4. **Limitación de tasa (Rate Limiting):** Prevención de abusos y ataques de fuerza bruta mediante Redis.  
5. **Validación de entradas:** Prevención de inyecciones y datos maliciosos.  
6. **Registro y monitoreo:** Monitoreo de solicitudes y eventos de seguridad.

**Ejemplos de uso:**  
- Un servicio de e-commerce que expone su API de pedidos solo a clientes y empleados autenticados.  
- Una API bancaria que limita solicitudes por minuto para prevenir fraudes.  
- Una API de gestión de documentos que utiliza HTTPS y JWT para proteger información sensible.

---

## 2. Consideraciones Técnicas

**Requisitos:**  
- Docker y Docker Compose instalados.  
- Python 3.12 (para desarrollo local si se desea ejecutar sin contenedores).

**Estructura del proyecto:**  
```
api-security-demo/
│
├─ app/
│  ├─ main.py
│  ├─ requirements.txt
│
├─ docker-compose.yml
└─ Dockerfile
```

**Endpoints implementados:**  
- `POST /token`: Login y generación de JWT.  
- `GET /tasks`: Endpoint protegido con JWT y rate limiting (máximo 5 solicitudes/minuto).

**Contenedores:**  
- **API FastAPI:** Ejecuta los endpoints y valida tokens JWT.  
- **Redis:** Almacena información para la limitación de tasa y puede usarse como caché.

**Ejecución:**  
1. Construir y levantar contenedores:  
   ```bash
   docker-compose up --build
   ```
2. Acceder a la API:  
   - Login: `POST http://localhost:8000/token`  
   - Endpoint protegido: `GET http://localhost:8000/tasks` con el token JWT en el header `Authorization: Bearer <token>`

**Notas técnicas:**  
- Uso de JWT para autenticación y autorización.  
- Rate limiting configurado con `fastapi-limiter` y Redis.  
- Configuración modular para escalar con API Gateway u otros servicios.  
- Fácil adaptación a entornos cloud (AWS, GCP, Azure).

---

## 3. Diagrama de Contenedores

```mermaid
graph TD
    A[Cliente <br> (Browser / App)] -->|HTTPS / Bearer Token| B[API Gateway <br> (Opcional) <br> - Rate Limiting <br> - Logging <br> - Auth Middleware]
    B -->| | C[FastAPI Service <br> - /login <br> - /tasks <br> - JWT Validation]
    B -->|Rate Limiting <br> Users / Tasks| D[Redis / DB]
```

**Descripción del flujo:**  
1. El cliente se autentica mediante `/token` y recibe un JWT.  
2. Cada solicitud a endpoints protegidos incluye el token JWT en el encabezado.  
3. La API valida el token y aplica rate limiting usando Redis.  
4. Los datos solicitados se retornan al cliente solo si las políticas de seguridad se cumplen.