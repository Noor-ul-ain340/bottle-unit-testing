"""
Noor ul Ain - Unit tests for bottle.SimpleTemplate (template rendering)
Techniques: ECP + BVA on template source, variables, loops and escaping.
"""
import pytest

from bottle import SimpleTemplate, TemplateError, template

pytestmark = [pytest.mark.noor_tests, pytest.mark.template]


def render(source, *args, **kwargs):
    return SimpleTemplate(source).render(*args, **kwargs)


# ---------------------------------------------------------------- smoke
@pytest.mark.smoke
@pytest.mark.order(1)
def test_variable_substitution():
    """TC-N13: {{name}} is replaced by the given value."""
    assert render("Hello {{name}}!", name="World") == "Hello World!"


# ---------------------------------------------------------------- ECP: expressions & types
@pytest.mark.ecp
@pytest.mark.order(2)
@pytest.mark.parametrize(
    "source, ctx, expected",
    [
        ("{{x}}", {"x": 0}, "0"),                   # falsy number
        ("{{x}}", {"x": 3.5}, "3.5"),               # float
        ("{{x}}", {"x": None}, ""),                 # None -> empty string
        ("{{x}}", {"x": b"bytes"}, "bytes"),        # bytes decoded
        ("{{1 + 2}}", {}, "3"),                     # expression
        ("{{x[0]}}", {"x": [9]}, "9"),              # indexing
        ("{{'a' if x else 'b'}}", {"x": 1}, "a"),   # conditional expression
    ],
    ids=["zero", "float", "none", "bytes", "expr", "index", "ternary"],
)
def test_expression_and_value_types(source, ctx, expected):
    """TC-N14: Different value types / expressions render as expected."""
    assert render(source, **ctx) == expected


@pytest.mark.ecp
@pytest.mark.order(3)
def test_multiple_variables_and_unicode():
    """TC-N15: Several placeholders and non-ASCII text work together."""
    assert render("{{x}} {{y}}", x="a", y="b") == "a b"
    assert render("{{name}}", name="\u00e9") == "\u00e9"


# ---------------------------------------------------------------- escaping
@pytest.mark.ecp
@pytest.mark.order(4)
def test_html_is_escaped_by_default():
    """TC-N16: {{x}} escapes < > & \" ' so templates are XSS-safe by default."""
    assert render("{{x}}", x="<b>&\"'") == "&lt;b&gt;&amp;&quot;&#039;"


@pytest.mark.ecp
@pytest.mark.order(5)
def test_bang_prefix_and_noescape_disable_escaping():
    """TC-N17: {{!x}} and noescape=True output raw HTML."""
    assert render("{{!x}}", x="<b>") == "<b>"
    assert SimpleTemplate("{{x}}", noescape=True).render(x="<b>") == "<b>"


# ---------------------------------------------------------------- control flow
@pytest.mark.bva
@pytest.mark.order(6)
@pytest.mark.parametrize(
    "items, expected",
    [([], ""), (["a"], "<li>a</li>\n"), (["a", "b"], "<li>a</li>\n<li>b</li>\n")],
    ids=["zero-items", "one-item", "two-items"],
)
def test_for_loop_boundaries_zero_one_many(items, expected):
    """TC-N18: Loop with 0, 1 and 2 items (0/1/many boundary)."""
    src = "% for i in items:\n<li>{{i}}</li>\n% end\n"
    assert render(src, items=items) == expected


@pytest.mark.ecp
@pytest.mark.order(7)
@pytest.mark.parametrize("flag, expected", [(True, "yes\n"), (False, "no\n")], ids=["true", "false"])
def test_if_else_branches(flag, expected):
    """TC-N19: Both branches of if/else are reachable."""
    src = "% if a:\nyes\n% else:\nno\n% end\n"
    assert render(src, a=flag) == expected


# ---------------------------------------------------------------- invalid input
@pytest.mark.bva
@pytest.mark.order(8)
def test_template_without_source_raises_template_error():
    """TC-N20: An empty source string means 'no template' -> TemplateError."""
    with pytest.raises(TemplateError):
        SimpleTemplate("")


@pytest.mark.ecp
@pytest.mark.order(9)
def test_plain_text_and_whitespace_only_templates():
    """TC-N21: Text without placeholders is returned unchanged (also a single space)."""
    assert render("no vars at all") == "no vars at all"
    assert render(" ") == " "


@pytest.mark.ecp
@pytest.mark.order(10)
def test_undefined_variable_and_runtime_errors_propagate():
    """TC-N22: Missing variable -> NameError; 1/0 -> ZeroDivisionError."""
    with pytest.raises(NameError):
        render("{{missing}}")
    with pytest.raises(ZeroDivisionError):
        render("{{x/0}}", x=1)


# ---------------------------------------------------------------- helper functions inside templates
@pytest.mark.ecp
@pytest.mark.order(11)
def test_builtin_helpers_get_defined_setdefault():
    """TC-N23: get(), defined() and setdefault() are available inside templates."""
    assert render('{{get("q", "none")}}') == "none"
    assert render('% if defined("z"):\nY\n% else:\nN\n% end') == "N\n"
    assert render('% setdefault("v", "dflt")\n{{v}}') == "dflt"


@pytest.mark.ecp
@pytest.mark.order(12)
def test_template_function_and_dict_argument():
    """TC-N24: template() and render() both accept a dict as well as keywords."""
    assert template("Hi {{n}}", n="kw") == "Hi kw"
    assert template("Hi {{n}}", {"n": "dict"}) == "Hi dict"
    assert render("Hi {{n}}", {"n": "dict"}) == "Hi dict"
