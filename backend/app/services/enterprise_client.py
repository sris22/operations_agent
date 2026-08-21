import time
from uuid import uuid4

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class EnterpriseAPIError(Exception):
    def __init__(self, status_code: int, detail: str, request_id: str | None = None):
        self.status_code = status_code
        self.detail = detail
        self.request_id = request_id
        super().__init__(f"Enterprise API error {status_code}: {detail}")


class EnterpriseClient:
    def __init__(self, request_id: str | None = None):
        self.base_url = settings.enterprise_api_base_url.rstrip("/")
        self.timeout = settings.external_api_timeout_seconds
        self.request_id = request_id or str(uuid4())
        self.max_retries = settings.max_retries

    def _headers(self) -> dict:
        return {
            "X-Request-ID": self.request_id,
            "Accept": "application/json",
        }

    async def _request(self, method: str, path: str, retry_safe: bool = False, **kwargs) -> dict:
        url = f"{self.base_url}{path}"
        headers = {**self._headers(), **kwargs.pop("headers", {})}

        attempts = self.max_retries if (retry_safe and method == "GET") else 1

        for attempt in range(attempts):
            logger.info(
                "enterprise_api_request",
                method=method,
                url=url,
                attempt=attempt + 1,
                request_id=self.request_id,
            )

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                try:
                    response = await client.request(method, url, headers=headers, **kwargs)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as e:
                    logger.error(
                        "enterprise_api_error",
                        status_code=e.response.status_code,
                        detail=e.response.text,
                        request_id=self.request_id,
                    )
                    if e.response.status_code >= 500 and attempt < attempts - 1:
                        wait = 2**attempt
                        logger.info(
                            "retrying_request", wait_seconds=wait, request_id=self.request_id
                        )
                        time.sleep(wait)
                        continue
                    raise EnterpriseAPIError(
                        status_code=e.response.status_code,
                        detail=e.response.text,
                        request_id=self.request_id,
                    )
                except httpx.TimeoutException:
                    Exception("timeout")
                    logger.error("enterprise_api_timeout", url=url, request_id=self.request_id)
                    if attempt < attempts - 1:
                        wait = 2**attempt
                        logger.info(
                            "retrying_request", wait_seconds=wait, request_id=self.request_id
                        )
                        time.sleep(wait)
                        continue
                    raise EnterpriseAPIError(
                        status_code=504,
                        detail="Enterprise API request timed out",
                        request_id=self.request_id,
                    )
                except httpx.RequestError as e:
                    logger.error(
                        "enterprise_api_connection_error", error=str(e), request_id=self.request_id
                    )
                    if attempt < attempts - 1:
                        wait = 2**attempt
                        logger.info(
                            "retrying_request", wait_seconds=wait, request_id=self.request_id
                        )
                        time.sleep(wait)
                        continue
                    raise EnterpriseAPIError(
                        status_code=503,
                        detail="Enterprise API is unavailable",
                        request_id=self.request_id,
                    )

        raise EnterpriseAPIError(
            status_code=503,
            detail="Enterprise API unavailable after retries",
            request_id=self.request_id,
        )

    async def get_customer(self, customer_id: str) -> dict:
        return await self._request("GET", f"/customers/{customer_id}", retry_safe=True)

    async def get_order(self, order_id: str) -> dict:
        return await self._request("GET", f"/orders/{order_id}", retry_safe=True)

    async def get_payment(self, payment_id: str) -> dict:
        return await self._request("GET", f"/payments/{payment_id}", retry_safe=True)

    async def create_ticket(
        self, customer_id: str, subject: str, description: str, priority: str = "MEDIUM"
    ) -> dict:
        return await self._request(
            "POST",
            "/tickets",
            json={
                "customer_id": customer_id,
                "subject": subject,
                "description": description,
                "priority": priority,
            },
        )

    async def refund_payment(self, payment_id: str, amount: float) -> dict:
        return await self._request(
            "POST", f"/payments/{payment_id}/refund", json={"amount": amount}
        )

    async def get_ticket(self, ticket_id: str) -> dict:
        return await self._request("GET", f"/tickets/{ticket_id}", retry_safe=True)


def get_enterprise_client(request_id: str | None = None) -> EnterpriseClient:
    return EnterpriseClient(request_id=request_id)
