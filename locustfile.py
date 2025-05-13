from locust import HttpUser, task, between

class ProductUser(HttpUser):
    wait_time = between(2, 5)  # Tiempo de espera entre tareas

    @task(1)
    def get_productos(self):
        print("Enviando GET /productos")
        response = self.client.get("/productos")
        print(f"GET /productos - Status Code: {response.status_code}, Respuesta: {response.text}")

    @task(2)
    def get_productos_categoria(self):
        print("Enviando GET /productos/categoria/1")
        response = self.client.get("/productos/categoria/1")
        print(f"GET /productos/categoria/1 - Status Code: {response.status_code}, Respuesta: {response.text}")

    @task(3)
    def post_producto(self):
        print("Enviando POST /productos")
        response = self.client.post("/productos", json={
            "nombre": "Smartwatch",
            "descripcion": "Reloj inteligente",
            "cantidad": 50,
            "precio": 100.00,
            "categoria_id": 1
        })
        print(f"POST /productos - Status Code: {response.status_code}, Respuesta: {response.text}")
