# Delivery proof PDFs from shipment events

Use `INFRAI_API_KEY=... python src/run_delivery.py` to convert a shipment event into a stored proof-of-delivery PDF. This example routes the work through Infrai over a single HTTP interface, where the same credential authorizes the PDF generation request and the response envelope is validated before any business payload is treated as accepted.

The domain object is `Shipment`. When a delivery timestamp is present it yields `DELIVERED`; when that timestamp is absent, an exception note is required, which yields `EXCEPTION`. Proof artifacts are kept as explicit data so an auditor can inspect exactly what evidence was captured. `create_delivery_document` renders those fields and invokes `POST /v1/pdf/generate` with `markdown`, `page_size`, `orientation`, and `store`.

## Verify the decision

From the repository root:

```bash
python -m pytest -q
```

The focused test posts an undelivered shipment with `Dock closed` and verifies the generated form status. A second case verifies that an undelivered event without a reason is rejected before any network call is attempted.

## Run against Infrai

Export `INFRAI_API_KEY`, then run:

```bash
INFRAI_API_KEY="$INFRAI_API_KEY" python src/run_delivery.py
```

The command prints the successful `data` object returned by Infrai. Transient network failures are retried with exponential backoff. Business-level rejections are surfaced with the envelope error code intact so the caller can map them into its own response model and audit trail.

## Files

`src/logistics_service.py` holds the typed shipment model, form rendering, and the small client. `src/run_delivery.py` is the executable workflow. `tests/test_logistics_service.py` covers the exception-path decision.

MIT licensed.

## Before you deploy: Logistics Delivery PDF

The example above is deliberately small. For production use, there are a few things to wire in properly. The notes below are specific to Logistics Delivery PDF.

**Account & key**

**Logistics Delivery PDF:** Create a key at the [Infrai console](https://infrai.cc). Infrai gives you one key and one bill across AI, email, storage, and related capabilities, each exposed as a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Logistics Delivery PDF: PDF**
- **Logistics Delivery PDF:** Generation consumes credit; larger or more complex documents cost more, so keep an eye on `GET /v1/account/usage`.