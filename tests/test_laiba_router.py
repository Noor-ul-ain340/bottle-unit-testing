"""
Laiba Tabassum - Unit tests for bottle.Router (URL path matching)
Techniques: ECP + BVA on paths, wildcards (filters) and HTTP methods.
"""
import pytest

from bottle import HTTPError, RouteBuildError, Router

pytestmark = [pytest.mark.laiba_tests, pytest.mark.router]


def env(path, method="GET"):
    return {"PATH_INFO": path, "REQUEST_METHOD": method}


@pytest.fixture
def router():
    r = Router()
    r.add("/", "GET", "root")
    r.add("/hello", "GET", "hello")
    r.add("/user/<id:int>", "GET", "user")
    r.add("/wiki/<page>", "GET", "wiki")
    r.add("/files/<p:path>", "GET", "files")
    r.add("/price/<x:float>", "GET", "price")
    return r


# ---------------------------------------------------------------- smoke
@pytest.mark.smoke
@pytest.mark.order(1)
def test_static_route_matches_exactly(router):
    """TC-L15: A static route returns its target and no URL arguments."""
    assert router.match(env("/hello")) == ("hello", {})


# ---------------------------------------------------------------- ECP: <int> filter
@pytest.mark.ecp
@pytest.mark.order(2)
@pytest.mark.parametrize(
    "path, expected",
    [("/user/42", 42), ("/user/7", 7), ("/user/-5", -5)],
    ids=["positive", "single-digit", "negative"],
)
def test_int_filter_converts_to_integer(router, path, expected):
    """TC-L16: <id:int> accepts integers and converts them to int."""
    target, args = router.match(env(path))
    assert target == "user"
    assert args == {"id": expected}
    assert isinstance(args["id"], int)


@pytest.mark.bva
@pytest.mark.order(3)
def test_int_filter_zero_boundary(router):
    """TC-L17: 0 is the boundary between negative and positive integers."""
    assert router.match(env("/user/0")) == ("user", {"id": 0})


@pytest.mark.ecp
@pytest.mark.order(4)
@pytest.mark.parametrize("path", ["/user/abc", "/user/", "/user/1.5", "/user/12abc"],
                         ids=["letters", "empty", "decimal", "mixed"])
def test_int_filter_rejects_non_integers_with_404(router, path):
    """TC-L18: Non-integer values do not match the int route -> 404."""
    with pytest.raises(HTTPError) as exc:
        router.match(env(path))
    assert exc.value.status_code == 404


# ---------------------------------------------------------------- ECP/BVA: default wildcard & path
@pytest.mark.bva
@pytest.mark.order(5)
@pytest.mark.parametrize(
    "path, ok",
    [("/wiki/home", True), ("/wiki/a", True), ("/wiki/", False), ("/wiki/a/b", False)],
    ids=["normal", "one-char", "empty-segment", "extra-segment"],
)
def test_default_wildcard_matches_one_non_empty_segment(router, path, ok):
    """TC-L19: <page> needs 1+ characters and cannot contain '/'."""
    if ok:
        assert router.match(env(path))[0] == "wiki"
    else:
        with pytest.raises(HTTPError) as exc:
            router.match(env(path))
        assert exc.value.status_code == 404


@pytest.mark.ecp
@pytest.mark.order(6)
def test_path_filter_matches_multiple_segments(router):
    """TC-L20: <p:path> swallows slashes, so nested paths match."""
    target, args = router.match(env("/files/a/b/c.txt"))
    assert target == "files"
    assert args == {"p": "a/b/c.txt"}


@pytest.mark.ecp
@pytest.mark.order(7)
def test_float_filter_valid_and_malformed_values(router):
    """TC-L21: 3.14 converts to float; '1.2.3' matches the pattern but fails conversion -> 400."""
    assert router.match(env("/price/3.14")) == ("price", {"x": 3.14})
    with pytest.raises(HTTPError) as exc:
        router.match(env("/price/1.2.3"))
    assert exc.value.status_code == 400


# ---------------------------------------------------------------- static path edge cases
@pytest.mark.bva
@pytest.mark.order(8)
def test_trailing_slash_is_a_different_path(router):
    """TC-L22: '/hello/' is NOT '/hello' (strict matching) -> 404."""
    with pytest.raises(HTTPError) as exc:
        router.match(env("/hello/"))
    assert exc.value.status_code == 404


@pytest.mark.bva
@pytest.mark.order(9)
def test_empty_path_info_is_treated_as_root(router):
    """TC-L23: Empty PATH_INFO falls back to '/'."""
    assert router.match(env("")) == ("root", {})


# ---------------------------------------------------------------- methods & errors
@pytest.mark.ecp
@pytest.mark.order(10)
def test_wrong_method_gives_405_with_allow_header(router):
    """TC-L24: POST on a GET-only path -> 405 and Allow: GET."""
    with pytest.raises(HTTPError) as exc:
        router.match(env("/hello", "POST"))
    assert exc.value.status_code == 405
    assert exc.value.headers["Allow"] == "GET"


@pytest.mark.ecp
@pytest.mark.order(11)
def test_unknown_path_gives_404(router):
    """TC-L25: A path that no rule covers -> 404."""
    with pytest.raises(HTTPError) as exc:
        router.match(env("/does/not/exist"))
    assert exc.value.status_code == 404


@pytest.mark.ecp
@pytest.mark.order(12)
def test_head_request_falls_back_to_get_route(router):
    """TC-L26: HEAD requests reuse the GET handler."""
    assert router.match(env("/hello", "HEAD")) == ("hello", {})


# ---------------------------------------------------------------- build()
@pytest.mark.ecp
@pytest.mark.order(13)
def test_build_fills_wildcards_and_appends_query():
    """TC-L27: build() makes URLs from a rule, extra args become the query string."""
    r = Router()
    r.add("/user/<id:int>", "GET", "t")
    assert r.build("/user/<id:int>", id=7) == "/user/7"
    assert r.build("/user/<id:int>", id=7, tab="x") == "/user/7?tab=x"


@pytest.mark.ecp
@pytest.mark.order(14)
def test_build_unknown_rule_or_missing_argument_raises():
    """TC-L28: Unknown rule name or missing wildcard value -> RouteBuildError."""
    r = Router()
    r.add("/user/<id:int>", "GET", "t")
    with pytest.raises(RouteBuildError):
        r.build("/nothing")
    with pytest.raises(RouteBuildError):
        r.build("/user/<id:int>")
