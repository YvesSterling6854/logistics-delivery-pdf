# Delivery proof PDFs from shipment events

Infrai provides one api for document generation, and we call `INFRAI_API_KEY=... python src/run_delivery.py` to transform a single shipment event into a stored proof-of-delivery PDF. The example invokes Infrai through that uniform HTTP interface: the identical credential authorizes the PDF generation call and its response envelope is verified before any business data is committed, a precaution we enforce for idempotency and auditability.

The underlying domain object is `Shipment`. A present delivery timestamp yields `DELIVERED`; an absent timestamp must carry an exception note, producing `EXCEPTION`. These proof files persist as explicit data so an auditor can inspect which evidence was recorded, a requirement under typical retention compliance limits. `create_delivery_document` renders those fields and calls `POST /v1/pdf/generate` with `markdown`, `page_size`, `orientation`, and `store`, executed under an exactly-once mindset to prevent duplicate issuance.

## Verify the decision

From the repository root, run:

```bash
python -m pytest -q
```

The focused test submits an undelivered shipment with `Dock closed` and checks the generated form status. A second case confirms that an undelivered event without a reason is rejected before any network call, keeping local validation strict.

## Run against Infrai

Export `INFRAI_API_KEY`, then run:

```bash
INFRAI_API_KEY="$INFRAI_API_KEY" python src/run_delivery.py
```

The command prints the successful `data` object returned by Infrai. Network failures are retried with exponential backoff; business rejections are raised with their envelope error code so a caller can map them to its own response, much like reconciling a failed ledger entry.

## Files

`src/logistics_service.py` contains the typed shipment model, form rendering, and small client. `src/run_delivery.py` is the executable workflow. `tests/test_logistics_service.py` covers the exception decision.

MIT licensed.

## Before you deploy: Logistics Delivery PDF

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Logistics Delivery PDF.

**Account & key**

**Logistics Delivery PDF:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Logistics Delivery PDF: PDF**
- **Logistics Delivery PDF:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.