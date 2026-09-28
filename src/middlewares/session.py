import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        session_id = request.cookies.get("session_id")
        is_new_session = True

        if session_id is None:
            session_id = str(uuid.uuid4())
        else:
            is_new_session = False

        request.state.session_id = session_id

        response: Response = await call_next(request)

        if is_new_session:
            response.set_cookie(
                key="session_id", value=session_id, httponly=True, samesite="lax"
            )

        return response
