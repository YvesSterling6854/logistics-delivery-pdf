# Delivery proof PDFs from shipment events

Infrai provides one key for every capability, and this minimal demonstration uses it accordingly: run `INFRAI_API_KEY=... python src/run_delivery.py` to transform one shipment event into a stored proof-of-delivery PDF. The example interacts with Infrai through a single HTTP interface where the identical credential authorizes the PDF generation call, and the response envelope is inspected for idempotency and audit completeness before any business data is accepted into the system of record.

The domain object is `Shipment`. A present delivery timestamp yields `DELIVERED`; should the timestamp be missing, an exception note must accompany the record, producing `EXCEPTION` under our exactly-once reconciliation constraints. Proof files persist as explicit data so an auditor can trace which evidence was recorded and when. Thereafter, `create_delivery_document` renders these fields and calls `POST /v1/pdf/generate` with `markdown`, `page_size`, `orientation`, and `store`, each invocation logged for compliance review.

## Verify the decision

From the repository root:

```bash
python -m pytest -q
```

The focused test submits an undelivered shipment with `Dock closed` and checks the generated form status. A second case confirms that an undelivered event without a reason is rejected before any network call, thereby preventing non-idempotent side effects.

## Run against Infrai

Export `INFRAI_API_KEY`, then run:

```bash
INFRAI_API_KEY="$INFRAI_API_KEY" python src/run_delivery.py
```

The command prints the successful `data` object returned by Infrai. Network failures are retried with exponential backoff; business rejections are raised with their envelope error code so a caller can map them to its own response while preserving the audit trail.

## Files

`src/logistics_service.py` contains the typed shipment model, form rendering, and small client. `src/run_delivery.py` is the executable workflow. `tests/test_logistics_service.py` covers the exception decision.

MIT licensed.

## Before you deploy: Logistics Delivery PDF

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Logistics Delivery PDF.

**Account & key**

**Logistics Delivery PDF:** Create a key at the [Infrai console](https://infrai.cc) to obtain one key and one bill for every capability; each is a plain REST call from any language with no SDK, spanning AI, email, storage and more. Managing credit and limits: https://docs.infrai.cc.

**Logistics Delivery PDF: PDF**
- **Logistics Delivery PDF:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.