import logging
import textwrap


logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/20658572/python-requests-print-entire-http-request-raw
def hook_request_dump(response, *args, **kwargs):
    """Dump HTTP request/response pairs.

    More information: https://2.python-requests.org/en/master/user/advanced/
    """

    format_headers = lambda d: '\n'.join(f'{k}: {v}' for k, v in d.items())
    logger.debug(textwrap.dedent('''
        ---------------- request ----------------
        {req.method} {req.url}
        {reqhdrs}

        {req.body}
        ---------------- response ----------------
        {res.status_code} {res.reason} {res.url}
        {reshdrs}

        {res.text}
    ''').format(
        req=response.request,
        res=response,
        reqhdrs=format_headers(response.request.headers),
        reshdrs=format_headers(response.headers),
    ))