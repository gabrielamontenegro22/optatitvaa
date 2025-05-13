from locust import HttpUser, task, between

class ProductUser(HttpUser):
    wait_time = between(1, 5)

    @task(1)
    def get_productos(self):
        self.client.get("/productos")

    @task(2)
    def get_productos_categoria(self):
        self.client.get("/productos/categoria/1")

    @task(3)
    def post_producto(self):
        self.client.post("/productos", json={
            "nombre": "Smartwatch",
            "descripcion": "Reloj inteligente",
            "cantidad": 50,
            "precio": 100.00,
            "categoria_id": 1
        })
