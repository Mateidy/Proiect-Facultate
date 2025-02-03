import flwr as fl
from flwr.server import ServerConfig

def weighted_average(metrics):
    return {"loss": sum(m["loss"] for m in metrics) / len(metrics)}

strategy = fl.server.strategy.FedAvg(
    evaluate_metrics_aggregation_fn=weighted_average,
    fraction_fit=1.0,
    min_fit_clients=1,
    min_available_clients=1,
)

if __name__ == "__main__":
    print("🚀 [SERVER] Pornire server Federated Learning...")
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=ServerConfig(num_rounds=5),
    )
