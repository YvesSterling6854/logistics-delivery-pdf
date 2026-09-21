from logistics_service import InfraiClient, Shipment, create_delivery_document


def main() -> None:
    shipment = Shipment("TRK-2048", "Northwind Imports", "Blue Harbor Foods",
                        "2026-09-07T08:30:00Z", ("pod-signature.png",))
    result = create_delivery_document(shipment, InfraiClient())
    print(result)


if __name__ == "__main__":
    main()
